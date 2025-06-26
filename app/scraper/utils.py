import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

# Заголовок, щоб симулювати реальний браузер
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
                  "Safari/537.36",
    "Referer": "https://auto.ria.com/uk/car/used/",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
}


# Функція отримання HTML
async def fetch_page(browser, url: str, retries: int = 3, delay: float = 2.0, timeout: int = 20000) -> str:
    page = await browser.new_page()
    for attempt in range(retries):
        try:
            await page.goto(url, timeout=timeout)
            content = await page.content()
            print(f"[Fetch Success] {url} (length: {len(content)})")
            return content
        except PlaywrightTimeoutError as e:
            print(f"[Timeout Retry {attempt + 1}] Timeout fetching {url}: {e}")
        except Exception as e:
            print(f"[Error Retry {attempt + 1}] Failed to fetch {url}: {e}")
        await asyncio.sleep(delay)

    raise Exception(f"Failed to fetch {url} after {retries} retries")
