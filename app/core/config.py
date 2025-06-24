from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field


# Клас конфігурації, який автоматично зчитує значення з .env
class Settings(BaseSettings):
    start_url: str = Field(..., alias="START_URL")  # URL, з якого починається скрапінг
    database_url: str = Field(..., alias="DATABASE_URL")  # Повний URL для підключення до бд
    scraping_time: str = Field(..., alias="SCRAPING_TIME")  # Час, у який щодня буде запускатися скрапінг

    # Налаштування для Pydantic Settings
    # Значення потрібно брати з файлу .env
    model_config = {
        "env_file": str(Path(__file__).parent.parent.parent / ".env"),
        "env_prefix": "",
        "extra": "ignore",
    }


# Створення єдиного екземпляру класу Settings, який буде імпортуватися по всьому проєкту
settings = Settings()

print("SETTINGS LOADED:", settings.model_dump())  # DEBUG
