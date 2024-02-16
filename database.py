import datetime

from sqlalchemy import ForeignKey, DateTime, func
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
RawHtml = str
ItemId = int


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[ItemId] = mapped_column(primary_key=True)

    completions: Mapped[list["Completion"]] = relationship(back_populates="user")


class Task(Base):
    __tablename__ = "task"
    id: Mapped[ItemId] = mapped_column(primary_key=True)
    task: Mapped[RawHtml] = mapped_column(nullable=True)
    hint: Mapped[RawHtml] = mapped_column(nullable=True)

    completions: Mapped[list["Completion"]] = relationship(back_populates="task")


class Completion(Base):
    __tablename__ = "completion"
    user_id: Mapped[ItemId] = mapped_column(ForeignKey("user.id"), primary_key=True)
    task_id: Mapped[ItemId] = mapped_column(ForeignKey("task.id"), primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="completions")
    task: Mapped["Task"] = relationship(back_populates="completions")


engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}/database.db", echo=False)


def get_session():
    return Session(engine)


if __name__ == "__main__":
    os.makedirs(SQLITE_DB_PATH, exist_ok=True)
    Base.metadata.create_all(engine)
    with get_session() as session:
        tasks = [
            Task(task="Task 1", hint="Hint for Task 1"),
            Task(task="Task 2", hint="Hint for Task 2"),
            Task(task="Task 3", hint="Hint for Task 3"),
            Task(task="Task 4", hint="Hint for Task 4"),
            Task(task="Task 5", hint="Hint for Task 5"),
        ]
        session.add_all(tasks)
        session.commit()