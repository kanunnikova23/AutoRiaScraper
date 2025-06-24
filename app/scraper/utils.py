import asyncio
import aiohttp

# Заголовок, щоб симулювати реальний браузер
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}


# Отримання всього HTML вмісту однієї сторінки
async def fetch_page(url: str, retries: int = 3, delay: float = 2.0) -> str:
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=HEADERS) as response:
                    return await response.text()
        except aiohttp.ClientError as e:
            print(f"[Retry {attempt + 1}] Error fetching {url}: {e}")
            await asyncio.sleep(delay)
        raise Exception(f"Failed to fetch {url} after {retries} retries")


