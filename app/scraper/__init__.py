from playwright.async_api import async_playwright

from app.core.config import settings
from app.scraper.fetcher import extract_urls_from_page
from app.scraper.fetcher import get_listing_urls
from app.scraper.parser import parse_car_card, parse_and_save_car_data
from app.scraper.utils import fetch_page

BASE_URL = settings.start_url


async def run_scraper():
    page_number = 1
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            while True:
                list_url = f"{BASE_URL}?page={page_number}"
                try:
                    # Create a temp page to load the listing
                    html = await fetch_page(browser, list_url)
                    print(f"[Page {page_number}] HTML завантажено")
                except Exception as e:
                    print(f"Не вдалося завантажити {list_url}: {e}")
                    break

                car_urls = await extract_urls_from_page(html)
                print(f"[DEBUG] Знайдено {len(car_urls)} URL на сторінці {page_number}")

                if not car_urls:
                    print(f"Завершено: сторінка {page_number} пуста")
                    break

                await parse_and_save_car_data(browser, car_urls)

                page_number += 1

            await browser.close()

    except KeyboardInterrupt:
        print("KeyboardInterrupt — парсинг зупинено. Уже зібрані авто збережено.")
    finally:
        print("Scraper завершив роботу.")
