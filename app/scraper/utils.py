import aiohttp

# Заголовок, щоб симулювати реальний браузер
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}


# Отримання всього HTML вмісту однієї сторінки
async def fetch_page(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            return await response.text()
