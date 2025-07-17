import datetime
import json
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.task_repository import TaskRepository
from api.schemas.enum import TaskStatus
from listener.core.logger import logger
from listener.services.notifier_service import NotificationService

if TYPE_CHECKING:
    from api.models import Task


# ---------------------------------
# RabbitMQ Messages
# ---------------------------------
class StartMessage(BaseModel):
    message_type: Literal["started"]
    hostname: str = Field(default=..., description="Hote exécutant la tâche.")


class SuccessMessage(BaseModel):
    message_type: Literal["success"]
    response: dict = Field(default=..., description="Resultat au format json.")


class FailureMessage(BaseModel):
    message_type: Literal["failure"]
    error_message: str = Field(default=..., description="Cause de l'erreur.")


class ProgressMessage(BaseModel):
    message_type: Literal["progress"]
    progress: float = Field(default=..., description="Progression (informatif).")


InnerMessage = Annotated[
    StartMessage | SuccessMessage | FailureMessage | ProgressMessage,
    Field(discriminator="message_type"),
]


class MessageFromWorker(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    data: InnerMessage


# ---------------------------------
# Service Exceptions
# ---------------------------------
class MessageServiceError(Exception):
    pass


# ---------------------------------
# Service
# ---------------------------------
class MessageService:
    def __init__(
        self,
        task_repository: TaskRepository,
        notification_service: NotificationService,
        session: AsyncSession,
    ) -> None:
        self.task_repository = task_repository
        self.notification_service = notification_service
        self.session = session

    def to_onliner_message(self, message: str) -> str:
        """Remove all CR + LF from the json message to display it in one line."""
        raw_message = message.replace("\n", "")
        return raw_message.replace("\r", "")

    async def process(self, message: str, service_name: str) -> None:
        logger.info(f"Start processing '{self.to_onliner_message(message)}'")

        try:
            # Convert the json into MessageFromWorker type
            message_object = self.unmarshall_message(message)

            task_id = message_object.task_id
            data: InnerMessage = message_object.data

            if isinstance(data, StartMessage):
                await self.process_start_message(task_id, service_name, data)
            if isinstance(data, ProgressMessage):
                await self.process_progress_message(task_id, service_name, data)
            if isinstance(data, SuccessMessage):
                await self.process_success_message(task_id, service_name, data)
            if isinstance(data, FailureMessage):
                await self.process_failure_message(task_id, service_name, data)

            logger.info(f"End processing '{self.to_onliner_message(message)}'")

            logger.debug("commit()")
            await self.session.commit()
        except Exception as error:
            logger.debug(f"Error: {error!s}, rollback()")
            await self.session.rollback()
            raise
        finally:
            logger.debug("close connection.")
            await self.session.close()

    def unmarshall_message(self, message: str) -> MessageFromWorker:
        try:
            return MessageFromWorker.model_validate_json(message)
        except Exception as exc:
            msg = f"Not a valid message: '{self.to_onliner_message(message)}'"
            raise MessageServiceError(msg) from exc

    async def process_start_message(self, task_id: str, service_name: str, data: StartMessage) -> None:
        logger.debug("Handling start message")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            msg = f"Task not found, task_id: '{task_id}', service_name: '{service_name}'"
            raise MessageServiceError(msg)

        task.status = TaskStatus.IN_PROGRESS
        task.start_date = datetime.datetime.now()
        task.worker_host = data.hostname
        task.progress = 0.0

    async def process_progress_message(self, task_id: str, service_name: str, data: ProgressMessage) -> None:
        logger.debug("Handling progress message")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            msg = f"Task not found, task_id: '{task_id}', service_name: '{service_name}'"
            raise MessageServiceError(msg)
        task.progress = data.progress

    async def process_success_message(self, task_id: str, service_name: str, data: SuccessMessage) -> None:
        logger.debug("Handling success message")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            msg = f"Task not found, task_id: '{task_id}', service_name: '{service_name}'"
            raise MessageServiceError(msg)

        task.status = TaskStatus.SUCCESS
        task.progress = 100
        task.end_date = datetime.datetime.now()
        task.response = json.dumps(data.response)

        callback_dict: dict = task.callback if task.callback is not None else {}
        if callback_dict:
            message = {
                "task_id": task_id,
                "status": "SUCCESS",
                "submition_date": task.submition_date.isoformat(),
                "start_date": task.start_date.isoformat() if task.start_date is not None else None,
                "end_date": task.end_date.isoformat() if task.end_date is not None else None,
                "progress": 100.0,
                "response": data.response,
            }
            try:
                await self.notification_service.notify(callback_dict, message)
                task.notification_status = "SUCCESS"
            except Exception as e:
                logger.error(f"Notification failure for task_id '{task_id}': {e}")
                task.notification_status = "FAILURE"
        task.notification_status = "SUCCESS"

    async def process_failure_message(self, task_id: str, service_name: str, data: FailureMessage) -> None:
        logger.debug("Handling failure message")
        task: Task | None = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            msg = f"Task not found, task_id: '{task_id}', service_name: '{service_name}'"
            raise MessageServiceError(msg)

        task.status = TaskStatus.FAILURE  # type: ignore
        task.end_date = datetime.datetime.now()  # type: ignore
        task.error_message = data.error_message  # type: ignore

        callback_dict: dict = task.callback  # type: ignore
        if callback_dict is not None:
            message = {
                "task_id": task_id,
                "status": "SUCCESS",
                "submition_date": task.submition_date.isoformat(),
                "start_date": task.start_date.isoformat() if task.start_date is not None else None,
                "end_date": task.end_date.isoformat() if task.end_date is not None else None,
                "progress": task.progress,
                "error_message": data.error_message,
            }
            try:
                await self.notification_service.notify(callback_dict, message)
                task.notification_status = "SUCCESS"  # type: ignore
            except Exception as e:
                logger.error(f"Notification failure for task_id '{task_id}': {e}")
                task.notification_status = "FAILURE"  # type: ignore
