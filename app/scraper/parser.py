import asyncio
import datetime
import re
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.db.crud import create_car
from app.db.session import get_async_session
from app.scraper.utils import fetch_page


# safe_get_text — безпечне отримання тексту або атрибута з HTML-елемента.
# Повертає None, якщо елемент не знайдено, щоб уникнути помилки 'NoneType' object has no attribute
def safe_get_text(soup: BeautifulSoup, selector: str, *, attr: str = None) -> str | None:
    tag = soup.select_one(selector)
    if not tag:
        return None
    if attr:
        return tag.get(attr)
    return tag.get_text(strip=True)


def parse_price(soup: BeautifulSoup) -> int | None:
    # Головна ціна
    main_price = safe_get_text(soup, ".price_value strong")
    if main_price and "$" in main_price:
        try:
            return int(main_price
                       .replace("$", "")
                       .replace("\xa0", "")
                       .replace(" ", ""))
        except ValueError:
            pass

    # Альтернативна ціна в USD
    usd_price = safe_get_text(soup, 'span[data-currency="USD"]')
    if usd_price:
        try:
            return int(usd_price
                       .replace("\xa0", "")
                       .replace(" ", ""))
        except ValueError:
            return None

    return None


# пробіг авто
def parse_odometer(soup: BeautifulSoup) -> int | None:
    tag = safe_get_text(soup, ".base-information.bold .size18")
    if not tag:
        return None
    try:
        return int(tag) * 1000  # 13 → 13000
    except ValueError:
        return None


def parse_username(soup: BeautifulSoup) -> str | None:
    return safe_get_text(soup, ".seller_info_name.bold")


def normalize_phone(phone: str) -> int | None:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0") and len(digits) == 10:
        return int("38" + digits)  # 0991236666 → 380991236666
    if digits.startswith("380") and len(digits) == 12:
        return int(digits)  # 380991236666 → 380991236666
    return None  # якщо формат невалідний


def remove_blocking_elements_js() -> str:
    return """
        const selectors = [
            'div.fc-dialog-overlay',
            'div.fc-footer-buttons-container',
            'div.fc-dialog-scrollable-content',
            'div.fc-consent-root',
            'div[class*="cookie"]',
            'div[class*="overlay"]',
            'div[class*="consent"]',
            'iframe',
            '[aria-hidden="true"]'
        ];
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => el.remove());
        });
    """


async def fetch_phone_with_playwright(url: str) -> str | None:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url, timeout=40000, wait_until="load")  # use full page load

            # JS blocking overlays removal (if needed)
            await page.evaluate(remove_blocking_elements_js())
            await page.wait_for_timeout(2000)

            # SCROLL to bottom to trigger JS rendering if needed
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            # Wait manually for button via locator
            try:
                locator = page.locator('button.size-large.conversion[data-action="showBottomPopUp"]')
                await locator.wait_for(state='visible', timeout=6000)
                await locator.scroll_into_view_if_needed()
                await locator.click()
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"[Phone Button Missing or Unclickable] {url}: {e}")
                return None

            # Extract phone number from tel: link
            try:
                phone_link = await page.query_selector('a.action-wrapper-link[href^="tel:"]')
                if phone_link:
                    tel_href = await phone_link.get_attribute("href")
                    phone = tel_href.replace("tel:", "").strip()
                    return normalize_phone(phone)
            except Exception as e:
                print(f"[Phone Parse Fail] {url}: {e}")
                return None
            finally:
                await browser.close()

    except Exception as e:
        print(f"[Playwright Total Fail] {url}: {e}")
        return None


async def parse_phone_number(soup: BeautifulSoup, url: str) -> int | None:
    # Try static HTML first
    raw = safe_get_text(soup, ".phone.bold")
    if raw and "x" not in raw:
        normalized = normalize_phone(raw)
        if normalized:
            return normalized

    # Fallback to Playwright
    phone = await fetch_phone_with_playwright(url)
    return phone


def parse_image_url(soup: BeautifulSoup) -> str | None:
    return safe_get_text(soup, "img.outline.m-auto", attr="src")


def parse_images_count(soup: BeautifulSoup) -> int | None:
    text = safe_get_text(soup, "a.show-all.link-dotted")
    match = re.search(r"\d+", text) if text else None
    return int(match.group()) if match else None


def parse_car_number(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one("span.state-num.ua")
    if tag and tag.contents:
        raw = tag.contents[0].strip()
    else:
        raw = safe_get_text(soup, "span.state-num.ua") or ""

    # Дістає лише валідний номер: 2 літери, 4 цифри, 2 літери
    match = re.search(r"[A-ZА-ЯІЇЄ]{2}\s?\d{4}\s?[A-ZА-ЯІЇЄ]{2}", raw)
    return match.group().replace(" ", "") if match else None


# VIN
def parse_vin(soup: BeautifulSoup) -> str | None:
    return safe_get_text(soup, "span.label-vin")


# Основна функція: збирає дані з картки авто
async def parse_car_card(browser, url: str) -> dict:
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        phone_number = await parse_phone_number(soup, url)

        return {
            "url": url,
            "title": safe_get_text(soup, "#heading-cars .head"),
            "price_usd": parse_price(soup),
            "odometer": parse_odometer(soup),
            "username": parse_username(soup),
            "phone_number": phone_number if phone_number is not None else 0,
            "image_url": parse_image_url(soup),
            "images_count": parse_images_count(soup),
            "car_number": parse_car_number(soup),
            "car_vin": parse_vin(soup),
            "date_found": datetime.today().date(),
        }

    except Exception as e:
        raise Exception(f"parse_car_card failed for {url}: {e}")
    finally:
        await page.close()


# Зберігає одне авто в БД одразу після парсингу
semaphore = asyncio.Semaphore(5)  # контролюємо паралельність


async def limited_parse(browser, url: str):
    async with semaphore:
        try:
            return await parse_car_card(browser, url)
        except Exception as e:
            print(f"[Error] Failed to parse car from {url}: {e}")
            return None


async def parse_and_save_car_data(browser, urls: list[str]):
    tasks = [limited_parse(browser, url) for url in urls]  # створюємо всі задачі
    results = await asyncio.gather(*tasks, return_exceptions=False)  # виконуємо паралельно

    async with get_async_session() as session:
        for car_data in results:
            if car_data:
                try:
                    await create_car(session, car_data)
                except Exception as e:
                    print(f"[Error] Failed to save car: {e}")
