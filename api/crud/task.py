from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import Task


async def create_task_record(db: AsyncSession, task_data: dict) -> Task:
    task = Task(**task_data)
    print(50 * "X", task.start_date)
    try:
        db.add(instance=task)
        await db.commit()
        await db.refresh(instance=task)
        await db.execute(text("SELECT pg_sleep(20);"))
        return task
    except Exception:
        await db.rollback()
        raise


async def get_task_by_id(db: AsyncSession, task_id: str, service: str) -> Task | None:
    return (
        db.query(Task).filter(Task.task_id == task_id, Task.service == service).first()  # type: ignore
    )


async def get_task_position_by_id(
    db: AsyncSession, task_id: str, service: str
) -> int | None:
    return None
