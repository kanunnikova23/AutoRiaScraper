import re
import datetime
from bs4 import BeautifulSoup
import re
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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


def normalize_phone(phone: str) -> str | None:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0") and len(digits) == 10:
        return "38" + digits  # 0991236666 → 380991236666
    if digits.startswith("380") and len(digits) == 12:
        return digits  # 380991236666 → 380991236666
    return None  # якщо формат невалідний


def remove_blocking_elements(driver):
    driver.execute_script("""
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
    """)


def parse_phone_number(soup: BeautifulSoup, url: str) -> str | None:
    # Try static HTML first
    raw = safe_get_text(soup, ".phone.bold")
    if raw and "x" not in raw:
        normalized = normalize_phone(raw)
        if normalized:
            return normalized

    # Selenium fallback
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Wait body is loaded and remove blockers
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        for _ in range(3):  # repeat just in case JS adds them later
            remove_blocking_elements(driver)
            time.sleep(1)

        # Wait and click show button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".phone_show_link"))
        )
        button = driver.find_element(By.CSS_SELECTOR, ".phone_show_link")
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        button.click()

        # Wait for number popup
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".popup-successful-call-desk"))
        )
        phone = driver.find_element(By.CSS_SELECTOR, ".popup-successful-call-desk").text
        return normalize_phone(phone.strip())

    except Exception as e:
        print(f"[Selenium Fail] Could not extract phone from {url}: {e}")
        return None

    finally:
        try:
            driver.quit()
        except:
            pass


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


async def parse_car_card(url: str) -> dict:
    html = await fetch_page(url)

    soup = BeautifulSoup(html, "html.parser")

    return {
        "url": url,
        "title": safe_get_text(soup, "#heading-cars .head"),
        "price_usd": parse_price(soup),
        "odometer": parse_odometer(soup),
        "username": parse_username(soup),
        "phone_number": parse_phone_number(soup, url),
        "image_url": parse_image_url(soup),
        "images_count": parse_images_count(soup),
        "car_number": parse_car_number(soup),
        "car_vin": parse_vin(soup),
        "datetime_found": datetime.date.today(),
    }
