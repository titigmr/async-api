from typing import Annotated, Tuple

from fastapi import Depends
from sqlalchemy import Result, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db_session
from api.models import Task
from api.schemas import TaskInfo
from api.schemas.enum import TaskStatus


class TaskRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self.db: AsyncSession = db

    async def create_task_record(self, task_data_create: TaskInfo) -> Task:
        task = Task(**task_data_create.model_dump())
        try:
            self.db.add(instance=task)
            await self.db.commit()
            await self.db.refresh(instance=task)
            # await self.db.execute(text("SELECT pg_sleep(1);"))
            return task
        except Exception:
            await self.db.rollback()
            raise

    async def get_task_by_id(self, task_id: str, service: str) -> Task | None:
        stmt: Select[Tuple[Task]] = select(Task).where(
            (Task.task_id == task_id) & (Task.service == service)
        )
        result: Result[Tuple[Task]] = await self.db.execute(statement=stmt)
        return result.scalar_one_or_none()

    async def get_task_position_by_id(self, task_id: str, service: str) -> int | None:
        stmt_task: Select[Tuple[Task]] = select(Task).where(
            (Task.task_id == task_id) & (Task.service == service)
        )
        result_task: Result[Tuple[Task]] = await self.db.execute(statement=stmt_task)
        task: Task | None = result_task.scalar_one_or_none()
        if not task or str(task.status) != TaskStatus.PENDING:
            return None

        stmt_count: Select[Tuple[int]] = select(func.count()).where(
            (Task.service == service)
            & (Task.status == TaskStatus.PENDING)
            & (Task.submition_date < task.submition_date)
        )
        result_count: Result[Tuple[int]] = await self.db.execute(statement=stmt_count)
        position: int | None = result_count.scalar_one_or_none()
        if position is None:
            return 1
        return position + 1

    async def count_pending_tasks_for_service(self, service: str) -> int:
        result: Result[Tuple[int]] = await self.db.execute(
            statement=select(func.count()).where(
                (Task.service == service)
                & (Task.status == TaskStatus.PENDING)
            )
        )
        position: int | None = result.scalar_one_or_none()
        if position is None:
            return 0
        else:
            return position
        
    async def count_pending_tasks_for_service_and_client(self, service: str, client_id: str) -> int:
        result: Result[Tuple[int]] = await self.db.execute(
            statement=select(func.count()).where(
                (Task.service == service)
                & (Task.status == TaskStatus.PENDING)
                & (Task.client_id == client_id)
            )
        )
        position: int | None = result.scalar_one_or_none()
        if position is None:
            return 0
        else:
            return position
