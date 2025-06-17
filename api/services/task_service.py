import uuid
from typing import Annotated, Tuple

from fastapi import Depends
from jsonschema import validate
from sqlalchemy import Row

from api.core.brokers import AbstractBroker
from api.models import Task
from api.repositories.task_repository import TaskRepository
from api.schemas import (
    QueueData,
    QueueTask,
    ServiceInfo,
    TaskData,
    TaskInfo,
    TaskRequest,
)
from api.schemas.enum import TaskStatus
from api.schemas.errors import BodyValidationError
from api.services import ServiceService, send_task_to_queue
from api.services.queue_service import get_broker


class TaskService:
    def __init__(
        self,
        task_repository: Annotated[TaskRepository, Depends(TaskRepository)],
        service_service: Annotated[ServiceService, Depends(ServiceService)],
        broker: Annotated[AbstractBroker, Depends(get_broker)],
    ) -> None:
        self.task_repository: TaskRepository = task_repository
        self.service_service: ServiceService = service_service
        self.broker: AbstractBroker = broker

    def check_service_schema(self, service: str, body: dict) -> None:
        """
        Vérifie que le body est conforme au json_schema du service (si défini).
        Lève BodyValidationError si la validation échoue.
        """
        service_obj: ServiceInfo | None = self.service_service.get_service(service)

        if service_obj and service_obj.json_schema:
            try:
                validate(instance=body, schema=service_obj.json_schema)
            except Exception as e:
                raise BodyValidationError(
                    details=f"Erreur de validation du body avec le json-schema du service '{service_obj.name}': {e}"
                )

    async def poll_task(self, task_id: str, service: str) -> TaskData | None:
        """Poll a task by its ID"""
        task_info: Row[Tuple[Task]] | None = await self.task_repository.get_task_by_id(
            task_id=task_id, service=service
        )
        if task_info:
            task_position: (
                int | None
            ) = await self.task_repository.get_task_position_by_id(
                task_id=str(task_info.task_id), service=service
            )
            return TaskData(
                task_id=str(task_info.task_id),
                task_position=task_position,
                status=TaskStatus(value=task_info.status),
            )

    async def submit_task(self, task: TaskRequest, service: str) -> TaskData:
        """Submit a new task"""
        self.check_service_schema(service=service, body=task.body)
        task_id = str(uuid.uuid4())
        queue_message = QueueTask(
            task_id=task_id, data=QueueData(message_type="submission", body=task.body)
        )
        send_task_to_queue(task_data=queue_message, service=service)

        task_obj = TaskInfo(
            task_id=task_id,
            client_id="default",
            service=service,
            status=TaskStatus.PENDING,
            request=task.body,
            callback=task.callback,
        )
        await self.task_repository.create_task_record(task_data_create=task_obj)
        return TaskData(task_id=task_id, task_position=None, status=TaskStatus.PENDING)
