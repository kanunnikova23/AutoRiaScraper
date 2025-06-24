from app.scraper.fetcher import get_listing_urls
from app.scraper.parser import parse_car_card
from app.db.session import get_async_session
from app.db.crud import create_car  # CRUD метод для збереження
import asyncio


async def run_scraper():
    urls = await get_listing_urls()
    async with get_async_session() as session:
        for url in urls:
            try:
                car_data = await parse_car_card(url)
                await create_car(session, car_data)
            except Exception as e:
                print(f" Помилка при обробці {url}: {e}")


asyncio.run(run_scraper())
