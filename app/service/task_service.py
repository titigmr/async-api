from sqlalchemy.orm import Session

from app.crud.task import create_task_record, get_task_by_id


def get_task_from_db(db: Session, task_id: str):
    return get_task_by_id(db, task_id)


def add_task_to_db(db: Session, task_data: dict):
    return create_task_record(db, task_data)
