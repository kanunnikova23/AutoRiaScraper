from app.db.session import async_engine
from app.db.models import Base
import asyncio

from app.scraper import run_scraper
from scheduler.job import start_scheduler


# Створення таблиць у БД (якщо їх ще нема)
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    print("AutoRiaScraper - перший запуск")
    await create_tables()  # асинхронна ініціалізація БД
    print("База підʼєднана та таблиці створені")

    # стартуємо планувальник і залишаємо event loop працювати
    try:
        start_scheduler()
    except Exception as e:
        print(f" Scheduler failed to start: {e}")

    await run_scraper()

    # Утримуємо головний цикл живим
    await asyncio.Event().wait()



# Цей блок виконується тільки якщо файл запускається напряму
# (а не імпортується як модуль в інші частини проєкту)
if __name__ == "__main__":
    asyncio.run(main())

