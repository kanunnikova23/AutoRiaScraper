import re
import datetime
from bs4 import BeautifulSoup
from datetime import datetime
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
    tag = soup.select_one(".seller_info_name.bold")
    return tag.get_text(strip=True) if tag else None
    return safe_get_text(soup, ".seller_info_name.bold")
def parse_phone_number(soup: BeautifulSoup, url: str) -> str | None:
    # Try static HTML first
    raw = safe_get_text(soup, ".phone.bold")


def parse_phone_number(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one(".phone.bold")
    if not tag:
        return None
    raw = tag.get_text(strip=True)
    digits = re.sub(r"\D", "", raw)  # замінюємо все, що не цифра(D), на ""
    return digits



def parse_image_url(soup: BeautifulSoup) -> str | None:
    return safe_get_text(soup, "img.outline.m-auto", attr="src")


def parse_images_count(soup: BeautifulSoup) -> int | None:
    text = safe_get_text(soup, "a.show-all.link-dotted")
    match = re.search(r"\d+", text) if text else None
    return int(match.group()) if match else None


def parse_car_number(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one("span.state-num.ua")
    return tag.get_text(strip=True).replace(" ", "")


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
        "phone_number": parse_phone_number(soup),
        "image_url": parse_image_url(soup),
        "images_count": parse_images_count(soup),
        "car_number": parse_car_number(soup),
        "car_vin": parse_vin(soup),
        "datetime_found": datetime.date.today(),
    }
