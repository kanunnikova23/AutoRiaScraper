import re
import datetime
from bs4 import BeautifulSoup
from datetime import datetime
from app.scraper.utils import fetch_page


def parse_price(soup: BeautifulSoup) -> int | None:
    price_tag = soup.select_one(".price_value strong")
    if not price_tag:
        return None
    try:
        return int(price_tag
                   .get_text(strip=True)
                   .replace("$", "")
                   .replace(" ", "")
                   .replace("\u202f", ""))
    except ValueError:
        return None


# пробіг авто
def parse_odometer(soup: BeautifulSoup) -> int | None:
    tag = soup.select_one(".base-information.bold .size18")
    if not tag:
        return None
    raw = tag.get_text(strip=True)
    try:
        return int(raw) * 1000  # 13 → 13000
    except ValueError:
        return None


def parse_username(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one(".seller_info_name.bold")
    return tag.get_text(strip=True) if tag else None


def parse_phone_number(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one(".phone.bold")
    if not tag:
        return None
    raw = tag.get_text(strip=True)
    digits = re.sub(r"\D", "", raw)  # замінюємо все, що не цифра(D), на ""
    return digits


#  Основна функція: збирає дані з картки авто
def parse_image_url(soup: BeautifulSoup) -> str | None:
    img_tag = soup.select_one("img.outline.m-auto")
    if not img_tag:
        return None
    return img_tag.get("src")


def parse_images_count(soup: BeautifulSoup) -> int | None:
    link = soup.select_one("a.show-all.link-dotted")
    if not link:
        return None
    text = link.get_text(strip=True)
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def parse_car_number(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one("span.state-num.ua")
    return tag.get_text(strip=True).replace(" ", "")


# VIN
def parse_vin(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one("span.label-vin")
    return tag.get_text(strip=True) if tag else None


async def parse_car_card(url: str) -> dict:
    html = await fetch_page(url)

    soup = BeautifulSoup(html, "html.parser")

    return {
        "url": url,
        "title": soup.select_one("#heading-cars .head").get_text(strip=True) if soup else None,
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
