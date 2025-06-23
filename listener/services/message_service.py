import datetime
import json
from api.repositories.task_repository import TaskRepository

from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, Json, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.enum import TaskStatus
from listener.core.logger import logger
from listener.services.notifier_service import NotificationService

#---------------------------------
# RabbitMQ Messages
#---------------------------------
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

InnerMessage = Annotated[Union[StartMessage, SuccessMessage, FailureMessage, ProgressMessage], Field(discriminator='message_type')]

class MessageFromWorker(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    data: InnerMessage



#---------------------------------
# Service Exceptions
#---------------------------------
class MessageServiceError(Exception):
    pass

#---------------------------------
# Service
#---------------------------------
class MessageService:

    def __init__(self, 
                 task_repository: TaskRepository, 
                 notification_service: NotificationService,
                 session: AsyncSession,
                 ):
        self.task_repository = task_repository
        self.notification_service = notification_service
        self.session = session

    def to_onliner_message(self, message: str) -> str:
        """Remove all CR + LF from the json message to display it in one line.
        """
        raw_message = message.replace("\n","")
        raw_message = raw_message.replace("\r","")
        return raw_message

    async def process(self, message: str, service_name: str):
        logger.info(f"Start processing '{self.to_onliner_message(message)}'")

        try:
            # Convert the json into MessageFromWorker type
            message_object = self.unmarshall_message(message)

            task_id = message_object.task_id
            data: InnerMessage = message_object.data
            
            if isinstance(data, StartMessage):
                await self.process_start_message(task_id,service_name,data)
            if isinstance(data, ProgressMessage):
                await self.process_progress_message(task_id,service_name,data)
            if isinstance(data, SuccessMessage):
                await self.process_success_message(task_id,service_name,data)
            if isinstance(data, FailureMessage):
                await self.process_failure_message(task_id,service_name,data)

            logger.info(f"End processing '{self.to_onliner_message(message)}'")

            logger.debug("commit()")
            await self.session.commit()
        except Exception as e:
            logger.debug("rollback()")
            await self.session.rollback()
            raise e
        finally:
            logger.debug("close connection.")
            await self.session.close()

    def unmarshall_message(self,message: str) -> MessageFromWorker :
        try:
            return MessageFromWorker.model_validate_json(message)
        except Exception as e:
            raise MessageServiceError(f"Not a valid message: '{self.to_onliner_message(message)}'")

    async def process_start_message(self, task_id: str,service_name: str,data: StartMessage):
        logger.debug("Handling start message")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")

        task.status = TaskStatus.RUNNING            # type: ignore
        task.start_date = datetime.datetime.now()   # type: ignore
        task.worker_host = data.hostname            # type: ignore
        task.progress = 0.0                         # type: ignore

    async def process_progress_message(self, task_id: str,service_name: str,data: ProgressMessage):
        logger.debug("Handling progress message")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")
        task.progress = data.progress       # type: ignore

    async def process_success_message(self, task_id: str,service_name: str,data: SuccessMessage):
        logger.debug("Handling success message")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")

        task.status   = TaskStatus.SUCCESS          # type: ignore
        task.end_date = datetime.datetime.now()     # type: ignore
        task.response = json.dumps(data.response)   # type: ignore
        
        callback_dict: dict = task.callback # type: ignore
        if callback_dict is not None:
            message = {
                "task_id": task_id,
                "status": "SUCCESS",
                "submition_date": task.submition_date.isoformat(),
                "start_date": task.start_date.isoformat(),
                "end_date": task.end_date.isoformat(),
                "progress": 100.0,
                "response": data.response
            }
            try:
                await self.notification_service.notify(callback_dict,message)
                task.notification_status = "SUCCESS"  # type: ignore
            except Exception as e:
                logger.error(f"Notification failure for task_id '{task_id}': {e}")
                task.notification_status = "FAILURE" # type: ignore

    async def process_failure_message(self, task_id: str,service_name: str,data: FailureMessage):
        logger.debug("Handling failure message")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")

        task.status   = TaskStatus.FAILURE          # type: ignore
        task.end_date = datetime.datetime.now()     # type: ignore
        task.error_message = data.error_message     # type: ignore

        callback_dict: dict = task.callback # type: ignore
        if callback_dict is not None:
            message = {
                "task_id": task_id,
                "status": "SUCCESS",
                "submition_date": task.submition_date.isoformat(),
                "start_date": task.start_date.isoformat(),
                "end_date": task.end_date.isoformat(),
                "progress": task.progress,
                "error_message": data.error_message 
            }
            try:
                await self.notification_service.notify(callback_dict,message)
                task.notification_status = "SUCCESS"  # type: ignore
            except Exception as e:
                logger.error(f"Notification failure for task_id '{task_id}': {e}")
                task.notification_status = "FAILURE"  # type: ignore
