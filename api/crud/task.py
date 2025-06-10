from sqlalchemy.orm import Session

from api.models import Task


def create_task_record(db: Session, task_data: dict) -> Task:
    task = Task(**task_data)
    try:
        db.add(instance=task)
        db.commit()
        db.refresh(instance=task)
        return task
    except Exception:
        db.rollback()
        raise


def get_task_by_id(db: Session, task_id: str, service: str) -> Task | None:
    return (
        db.query(Task).filter(Task.task_id == task_id, Task.service == service).first()
    )  # type: ignore


def get_task_position_by_id(db: Session, task_id: str, service: str) -> int | None:
    return None
