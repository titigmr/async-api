import uuid
from typing import Annotated

from fastapi import Depends
from jsonschema import validate

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
from api.schemas.errors import BodyValidationError, Forbidden, ServiceNotFound, TooManyClientsRequests, TooManyRequests
from api.services import QueueSender, ServiceService
from api.services.client_service import ClientService


class TaskService:
    def __init__(
        self,
        task_repository: Annotated[TaskRepository, Depends(TaskRepository)],
        service_service: Annotated[ServiceService, Depends(ServiceService)],
        client_service: Annotated[ClientService, Depends(ClientService)],
        queue_sender: Annotated[QueueSender, Depends(QueueSender)],
    ) -> None:
        self.task_repository: TaskRepository = task_repository
        self.service_service: ServiceService = service_service
        self.client_service: ClientService = client_service
        self.queue_sender: QueueSender = queue_sender

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

    async def poll_task(self, task_id: str, service: str, client_id: str) -> TaskData | None:
        """Poll a task by its ID"""
        # Check service exits
        if not self.service_service.get_service(service_name=service):
            raise ServiceNotFound

        # Check client authorization on service
        client_authorization = self.client_service.get_client_authorization_for_service(
            client_id=client_id, service=service
        )
        if client_authorization is None:
            raise Forbidden

        task_info: Task | None = await self.task_repository.get_task_by_id(
            task_id=task_id, service=service
        )
        if task_info:
            task_position: int | None = await self.task_repository.get_task_position_by_id(
                task_id=str(task_info.task_id), service=service
            )
            print(f"Type submission date: {type(task_info.submition_date)}, date: {task_info.submition_date}")
            return TaskData(
                task_id=task_info.task_id,
                task_position=task_position,
                submission_date=task_info.submition_date,
                status=TaskStatus(value=task_info.status),
            )

    async def submit_task(self, task: TaskRequest, service: str, client_id: str) -> TaskData:
        """Submit a new task"""
        # Check service exits
        service_info = self.service_service.get_service(service_name=service)
        if service_info is None:
            raise ServiceNotFound

        # Check client authorization on service
        client_authorization = self.client_service.get_client_authorization_for_service(
            client_id=client_id, service=service
        )
        if client_authorization is None:
            raise Forbidden

        # Check quotas (service)
        service_quotas = service_info.quotas
        if service_quotas is not None:
            if await self.task_repository.count_pending_tasks_for_service(service=service) >= service_quotas:
                raise TooManyRequests

        # Check quotas (client/service)
        client_quotas_for_service = client_authorization.quotas
        if client_quotas_for_service is not None:
            if (
                await self.task_repository.count_pending_tasks_for_service_and_client(
                    service=service, client_id=client_id
                )
                >= client_quotas_for_service
            ):
                raise TooManyClientsRequests

        # Check schema
        self.check_service_schema(service=service, body=task.body)

        task_id = str(uuid.uuid4())
        queue_message = QueueTask(task_id=task_id, data=QueueData(message_type="submission", body=task.body))
        await self.queue_sender.send_task_to_queue(
            queue=service_info.in_queue, task_data=queue_message, service=service
        )

        task_obj = TaskInfo(
            task_id=task_id,
            client_id=client_id,
            service=service,
            status=TaskStatus.PENDING,
            request=task.body,
            callback=task.callback,
        )
        await self.task_repository.create_task_record(task_data_create=task_obj)
        task_position = await self.task_repository.get_task_position_by_id(task_id=task_id, service=service)
        return TaskData(task_id=task_id, task_position=task_position, status=TaskStatus.PENDING)
