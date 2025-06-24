from sqlalchemy import Column, String, Integer, Date
from app.db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


# Модель для таблиці автомобілів, яка парситься з AutoRia
class Car(Base):
    __tablename__ = "cars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, unique=True, nullable=False)
    title = Column(String)
    price_usd = Column(Integer)
    odometer = Column(Integer)
    username = Column(String)
    phone_number = Column(String)
    image_url = Column(String)
    images_count = Column(Integer)
    car_number = Column(String, unique=False, nullable=True)
    car_vin = Column(String, unique=False, nullable=True)
    datetime_found = Column(Date, nullable=False)
