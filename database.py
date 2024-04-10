import datetime
from sqlalchemy import URL, ForeignKey, DateTime, func, MetaData, Table, Column, String, Integer
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
# class Task(Base):
#     __tablename__ = "task"
#     id: Mapped[ItemId] = mapped_column(primary_key=True)
#     task: Mapped[RawHtml] = mapped_column(nullable=True)
#     hint: Mapped[RawHtml] = mapped_column(nullable=True)
#
#     completions: Mapped[list["Completion"]] = relationship(back_populates="task")
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
        database=database_name
    )

    engine = create_engine(url)
    return engine
def get_session(engine):
    return Session(engine)
if __name__ == "__main__":
    engine = make_engine("LRH_db")
    os.makedirs(SQLITE_DB_PATH, exist_ok=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


    with get_session(engine) as session:
        locations = [
            Location(location_id=1, storeroom_name="Capstone Lab", shelf_name="Work Table")
        ]
        session.add_all(locations)
        # items = [
        #     Item(sku=1, name='Object 1', description='Object 1', reorder_threshold=2, count=10, location_id=1),
        #     Item(sku=2, name='Object 2', description='Object 2', reorder_threshold=1, count=10, location_id=1),
        #     Item(sku=3, name='Object 3', description='Object 3', reorder_threshold=2, count=10, location_id=1),
        #     Item(sku=4, name='Object 4', description='Object 4', reorder_threshold=2, count=10, location_id=1),
        #     Item(sku=5, name='Object 5', description='Object 5', reorder_threshold=2, count=10, location_id=1),
        # ]
        # session.add_all(items)
        session.commit()