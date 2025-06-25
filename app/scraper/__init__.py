from app.core.config import settings
from app.scraper.fetcher import extract_urls_from_page
from app.scraper.fetcher import get_listing_urls
from app.scraper.parser import parse_car_card
from app.scraper.parser import parse_car_card, parse_and_save_car_data
from app.scraper.utils import fetch_page

BASE_URL = settings.start_url


async def run_scraper():
    page = 1
    try:
        while True:
            list_url = f"{BASE_URL}?page={page}"
            try:
                html = await fetch_page(list_url)
                print(f"[Page {page}] HTML завантажено")
            except Exception as e:
                print(f"Не вдалося завантажити {list_url}: {e}")
                break

            car_urls = await extract_urls_from_page(html)
            if not car_urls:
                print(f"Завершено: сторінка {page} пуста")
                break

            for car_url in car_urls:
                await parse_and_save_car_data(car_url)

            page += 1

    except KeyboardInterrupt:
        print("KeyboardInterrupt — парсинг зупинено. Уже зібрані авто збережено.")
    finally:
        print("Scraper завершив роботу.")