from apscheduler.schedulers.asyncio import AsyncIOScheduler  # запускає таски в межах asyncio-циклу
from apscheduler.triggers.cron import CronTrigger  # налаштований по годинах і хвилинах з .env

from app.core.config import settings
from app.scraper import run_scraper  # entry-point зі scraper/__init__.py
from services.db_backup import dump_database


async def scraper_job():
    await run_scraper()


def dump_job():
    dump_database()


def start_scheduler() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.remove_all_jobs()

    # Розбираємо час з налаштувань (формат "HH:MM")
    hour_str, minute_str = settings.scraping_time.split(":")
    trigger = CronTrigger(hour=int(hour_str), minute=int(minute_str))

    # Убираем предыдущие задачи (якщо існували)
    if scheduler.get_job("daily_scrape"):
        scheduler.remove_job("daily_scrape")
    if scheduler.get_job("daily_dump"):
        scheduler.remove_job("daily_dump")

    # Виклик через asyncio.create_task(...) гарантує, що асинхронна run_scraper() працюватиме в бекграунді.

    # Scraper job
    scheduler.add_job(scraper_job, trigger=trigger, id="daily_scrape")

    # Dump job
    scheduler.add_job(dump_job, trigger=trigger, id="daily_dump")

    scheduler.start()

    print(f"Scheduler started — scraping scheduled daily at {settings.scraping_time}")
