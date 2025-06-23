from sqlalchemy import Column, String, Integer, DateTime
from app.db import Base
from datetime import datetime


# Модель для таблиці автомобілів, яка парситься з AutoRia
class Car(Base):
    __tablename__ = "cars"

    url = Column(String, primary_key=True)
    title = Column(String)
    price_usd = Column(Integer)
    odometer = Column(Integer)
    username = Column(String)
    phone_number = Column(String)
    image_url = Column(String)
    images_count = Column(Integer)
    car_number = Column(String)
    car_vin = Column(String)
    datetime_found = Column(DateTime, default=datetime.now())
