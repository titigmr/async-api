import datetime
import json
from api.repositories.task_repository import TaskRepository

from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, Json, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.enum import TaskStatus

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
# Callback types
#---------------------------------
class HttpCallback(BaseModel):
    type: Literal["http"]
    url:  str = Field(default=..., description="Url.")

class HttpsCallback(BaseModel):
    type: Literal["https"]
    url:  str = Field(default=..., description="Url.")
    skip_tls: bool = Field(default=False, description="Disable TLS check.")

Callback = Annotated[Union[HttpCallback, HttpsCallback], Field(discriminator='type')]

#---------------------------------
# Service Exceptions
#---------------------------------
class MessageServiceError(Exception):
    pass

#---------------------------------
# Service
#---------------------------------
class MessageService:

    def __init__(self, task_repository: TaskRepository, session: AsyncSession):
        self.task_repository = task_repository
        self.session = session

    async def process(self, message: str, service_name: str):
        try:
            print(f"[x] Processing {message}")
            message_object = self.unmarshall_message(message)
            print(f">>>>> {message_object}")

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

            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    def unmarshall_message(self,message: str) -> MessageFromWorker :
        try:
            return MessageFromWorker.model_validate_json(message)
        except Exception as e:
            raise MessageServiceError(f"Not a valid message: '{message}'")

    async def process_start_message(self, task_id: str,service_name: str,data: StartMessage):
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")

        task.status = TaskStatus.RUNNING            # type: ignore
        task.start_date = datetime.datetime.now()   # type: ignore
        task.worker_host = data.hostname            # type: ignore
        task.progress = 0.0                         # type: ignore

    async def process_progress_message(self, task_id: str,service_name: str,data: ProgressMessage):
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")
        task.progress = data.progress       # type: ignore

    async def process_success_message(self, task_id: str,service_name: str,data: SuccessMessage):
        print("success")
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")

        task.status   = TaskStatus.SUCCESS          # type: ignore
        task.end_date = datetime.datetime.now()     # type: ignore
        task.response = json.dumps(data.response)   # type: ignore
        
        # Nous voulons que la base soit commit avant d'appeler le callback
        callback_string: dict = task.callback # type: ignore
        await self.session.commit()

        # Todo: Callback
        if callback_string is not None:
            callback = self.unmarshall_callback(callback_string)
            print(f"{type(callback)}")

    async def process_failure_message(self, task_id: str,service_name: str,data: FailureMessage):
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")

        task.status   = TaskStatus.FAILURE          # type: ignore
        task.end_date = datetime.datetime.now()     # type: ignore
        task.error_message = data.error_message     # type: ignore
        # Nous voulons que la base soit commit avant d'appeler le callback
        await self.session.commit()

    def unmarshall_callback(self,callback_dict: dict) -> Callback :
        try:
            adapter = TypeAdapter(Callback)
            return adapter.validate_python(callback_dict)
        except Exception as e:
            raise MessageServiceError(f"Not a valid callback: '{callback_dict}'")