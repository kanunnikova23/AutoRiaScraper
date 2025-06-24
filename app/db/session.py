from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# Створюємо асинхронний engine на базі URL з .env
async_engine = create_async_engine(
    settings.database_url,
    echo=False  # Вивід SQL-запитів у консоль (вкл. тільки для дебагу)
)

# Створення асинхронної фабрики сесій
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False  # не скидає дані після commit
)


# Dependency: функція для отримання сесії
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
