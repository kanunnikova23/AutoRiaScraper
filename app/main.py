from app.db.session import async_engine
from app.db.models import Base
import asyncio


# Створення таблиць у БД (якщо їх ще нема)
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def main():
    print("AutoRiaScraper - перший запуск")
    asyncio.run(init_db())  # асинхронна ініціалізація БД


# Цей блок виконується тільки якщо файл запускається напряму
# (а не імпортується як модуль в інші частини проєкту)
if __name__ == "__main__":
    main()
