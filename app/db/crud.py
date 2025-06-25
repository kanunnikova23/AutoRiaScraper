from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Car
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


# Збереження однієї машини в базу даних
async def create_car(session: AsyncSession, car_data: dict) -> None:
    # Ініціалізуємо модель Car з даними словника
    new_car = Car(**car_data)

    # Додаємо об'єкт у поточну сесію
    session.add(new_car)
    try:
        await session.commit()
        print(f"[DB] Saved car: {car_data['title']}")
    except IntegrityError:
        # Якщо дублювання (наприклад, url вже є), відкат змін
        await session.rollback()
        print(f"[DB] Duplicate skipped: {car_data['url']}")


async def is_duplicate(session, url: str) -> bool:
    result = await session.execute(select(Car.id).where(Car.url == url))
    return result.scalar_one_or_none() is not None
