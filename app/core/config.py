from pydantic_settings import BaseSettings


# Клас конфігурації, який автоматично зчитує значення з .env
class Settings(BaseSettings):
    start_url: str  # URL, з якого починається скрапінг
    database_url: str  # Повний URL для підключення до бд
    scraping_time: str  # Час, у який щодня буде запускатися скрапінг

    # Налаштування для Pydantic Settings
    # Значення потрібно брати з файлу .env
    class Config:
        env_file = ".env"


# Створення єдиного екземпляру класу Settings, який буде імпортуватися по всьому проєкту
settings = Settings()
