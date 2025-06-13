from datetime import datetime
from typing import Annotated, Tuple

from fastapi import Depends
from sqlalchemy import Result, Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db_session
from api.models.task import Task
from api.schemas.enum import TaskStatus


class TaskCountByStatusAndServiceView:
    def __init__(self, service: str, status: str, count: int) -> None:
        self.service: str = service
        self.status: str = status
        self.count: int = count

    def __repr__(self):
        return f"TaskCountByStatusAndServiceView(service={self.service}, status={self.status}, count={self.count})"


class PendingAndRunningTaskView:
    def __init__(
        self, service: str, status: str, submition_date: datetime, start_date: datetime
    ) -> None:
        self.service: str = service
        self.status: str = status
        self.submition_date: datetime = submition_date
        self.start_date: datetime = start_date

    def __repr__(self):
        return f"PendingAndRunningTaskView(service={self.service}, status={self.status}, submition_date={self.submition_date}, start_date={self.start_date})"


class MetricsTaskRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self.db: AsyncSession = db

    async def count_tasks_per_status_and_service(
        self,
    ) -> list[TaskCountByStatusAndServiceView]:
        """Get the count of tasks per status and service.

        Returns:
            list[TaskCountByStatusAndServiceView]: A list of task counts grouped by status and service.
        """
        statement: Select[Tuple[str, str, int]] = select(
            Task.service, Task.status, func.count(Task.service)
        ).group_by(Task.service, Task.status)
        rows: Result[Tuple[str, str, int]] = await self.db.execute(statement=statement)
        res = list(
            map(lambda x: TaskCountByStatusAndServiceView(x[0], x[1], x[2]), rows.all())
        )
        return res

    async def running_and_pending_tasks(self) -> list[PendingAndRunningTaskView]:
        rows: Result[Tuple[str, str, datetime, datetime]] = await self.db.execute(
            statement=select(
                Task.service, Task.status, Task.submition_date, Task.start_date
            ).where(
                or_(
                    Task.status == TaskStatus.PENDING, Task.status == TaskStatus.RUNNING
                )
            )
        )
        res = list(
            map(
                lambda x: PendingAndRunningTaskView(
                    service=x[0], status=x[1], submition_date=x[2], start_date=x[3]
                ),
                rows.all(),
            )
        )
        return res
