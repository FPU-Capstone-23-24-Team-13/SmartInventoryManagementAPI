import datetime
from sqlalchemy import URL, ForeignKey, inspect, DateTime, func, MetaData, Table, Column, String, Integer
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import create_engine

import os


SQLITE_DB_PATH = "running"

# Provide some more useful metadata when debugging, like:
# what does this string contain again? oh, raw html.
ItemSKU = str
ItemName = str
ItemDescription = str
ReorderThreshold = int
ItemCount = int

LocationId = str
StoreroomName = str
ShelfName = str

SensorId = str
class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"
    sku: Mapped[ItemSKU] = mapped_column(primary_key=True)
    name: Mapped[ItemName] = mapped_column()
    description: Mapped[ItemDescription] = mapped_column()
    reorder_threshold: Mapped[ReorderThreshold] = mapped_column()
    count: Mapped[ItemCount] = mapped_column()
    location_id: Mapped[LocationId] = mapped_column(ForeignKey("locations.location_id"), nullable=True)  # Define foreign key
    sensor_id: Mapped[SensorId] = relationship("Sensor")

class Location(Base):
    __tablename__ = "locations"
    location_id: Mapped[LocationId] = mapped_column(primary_key=True)
    storeroom_name: Mapped[StoreroomName] = mapped_column()
    shelf_name: Mapped[ShelfName] = mapped_column()
    items: Mapped[list["Item"]] = relationship()
class Sensor(Base):
    __tablename__ = "sensors"
    sensor_id: Mapped[SensorId] = mapped_column(primary_key=True)
    sku: Mapped[ItemSKU] = mapped_column(ForeignKey("items.sku"), nullable=True)
def make_engine(database_name):
    url = URL.create(
        drivername="postgresql",
        username="Andrew",
        password="Capstone",
        port=5432,
        database=database_name,
        host='config-postgres-1',
    )

    engine = create_engine(url)
    return engine
def get_session(engine):
    return Session(engine)

def start_db():
    engine = make_engine("LRH_db")
    os.makedirs(SQLITE_DB_PATH, exist_ok=True)
    with engine.connect() as connection:
        inspector = inspect(connection)
        existing_tables = inspector.get_table_names()

        if 'items' not in existing_tables or 'locations' not in existing_tables or 'sensors' not in existing_tables:
            Base.metadata.create_all(engine)
            with get_session(engine) as session:
                locations = [
                    Location(location_id=1, storeroom_name="Capstone Lab", shelf_name="Work Table")
                ]
                session.add_all(locations)
                session.commit()
        else:
            print("Tables already exist. Skipping table creation.")
