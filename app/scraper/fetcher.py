import aiohttp
from bs4 import BeautifulSoup

from app.core.config import settings
from app.scraper.utils import fetch_page

# Базова URL-адреса пошуку, зчитується з .env
BASE_URL = settings.start_url


# Витягти всі посилання на авто з однієї HTML-сторінки
async def extract_urls_from_page(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for tag in soup.select("section.ticket-item a.address"):
        href = tag.get("href")
        if href and "auto.ria.com" in href:
            links.append(href.split("?")[0])  # очищення від параметрів

    return links


# пройти всі сторінки + зібрати всі посилання
# гортаємо сторінки з оголошеннями до того моменту, поки не закінчаться
async def get_listing_urls() -> list[str]:
    all_urls = []
    page = 1
    async with aiohttp.ClientSession() as session:
        while True:
            # Зібрати HTML для конкретної сторінки
            url = f"{BASE_URL}?page={page}"
            html = await fetch_page(session, url)

            # Витягти URL-ки з цієї сторінки
            urls = await extract_urls_from_page(html)

            if not urls:
                break  # якщо немає нових — кінець

            all_urls.extend(urls)
            page += 1  # перейти до наступної сторінки

    return all_urls
