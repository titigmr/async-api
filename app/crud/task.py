from sqlalchemy.orm import Session

from app.models import Task


def create_task_record(db: Session, task_data: dict) -> Task:
    task = Task(**task_data)
    db.add(task)
    db.flush()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: str, service: str):
    return db.query(Task).filter(Task.task_id == task_id, Task.service == service).first()


def get_task_position_by_id(db: Session, task_id: str, service: str):
    return None
