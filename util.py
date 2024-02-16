from flask import request
from sqlalchemy import select
from datetime import datetime, timedelta

import database as db


def make_new_user():
    user_id = -1
    with db.get_session() as session:
        new_user = db.User()
        session.add(new_user)
        session.commit()
        user_id = new_user.id
    return user_id


def get_make_user(req: request):
    try:
        user_id = int(req.cookies.get("scvgr_user_id", "-1"))
    except:
        print("invalid cookie! handle this error better")
        return (-1, False)

    if user_id < 0:
        # missing or invalid user id, make a new user
        return (make_new_user(), True)
    else:
        return (user_id, False)


def get_incomplete_tasks(user_id: int):
    results = []
    with db.get_session() as session:
        stmt = select(db.Task.task, db.Task.hint).where(
            ~db.Task.completions.any(db.Completion.user_id == user_id)
        )
        results = session.execute(stmt).all()
    return results


def get_complete_tasks(user_id: int):
    results = []
    with db.get_session() as session:
        stmt = select(db.Task.task, db.Task.hint).where(
            db.Task.completions.any(db.Completion.user_id == user_id)
        )
        results = session.execute(stmt).all()
    return results


def complete_task(user_id: int, task_id: int):
    with db.get_session() as session:
        stmt = (
            select(db.Completion)
            .where(db.Completion.user_id == user_id)
            .where(db.Completion.task_id == task_id)
        )
        if session.execute(stmt).first():
            print(f"User {user_id} already completed task {task_id}!")
            return False
        c = db.Completion(user_id=user_id, task_id=task_id)
        session.add(c)
        session.commit()
    return True


def did_just_scan(user_id: int):
    with db.get_session() as session:
        stmt = (
            select(db.Completion)
            .where(db.Completion.user_id == user_id)
            .order_by(
                db.Completion.timestamp.desc(),
            )
        )
        comp = session.execute(stmt).first()
        if comp is None:
            return False
        return datetime.utcnow() - comp[0].timestamp < timedelta(minutes=1)