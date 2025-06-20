import asyncio
import datetime

from click import DateTime
from api.repositories.task_repository import TaskRepository

from aio_pika.abc import AbstractIncomingMessage

from typing import Annotated, Any, Dict, Literal, Union
from pydantic import BaseModel, Field, Json
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.enum import TaskStatus

class StartMessage(BaseModel):
    message_type: Literal["started"]
    hostname: str = Field(default=..., description="Hote exécutant la tâche.")

class SuccessMessage(BaseModel):
    message_type: Literal["success"]
    response: Json = Field(default=..., description="Resultat au format json.")

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

class MessageServiceError(Exception):
    pass

class MessageService:

    def __init__(self, task_repository: TaskRepository, session: AsyncSession):
        self.task_repository = task_repository
        self.session = session

    async def process(self, message: str, service_name: str):
        try:
            print(f"[x] Traitement de {message}")
            message_object = self.unmarshall_message(message)
            
            task_id = message_object.task_id
            data: InnerMessage = message_object.data
            
            if isinstance(data, StartMessage):
                await self.process_start_message(task_id,service_name,data)


            # if ..
            await self.session.commit()
            print(f"[✓] Fini {message_object}")
        except:
            await self.session.rollback()
        finally:
            await self.session.close()

    def unmarshall_message(self,message: str) -> MessageFromWorker :
        try:
            return MessageFromWorker.model_validate_json(message)
        except Exception as e:
            raise MessageServiceError(f"Not a valid message: '{message}'")

    async def process_start_message(self, task_id: str,service_name: str,data: StartMessage):
        task = await self.task_repository.get_task_by_id(task_id, service_name)
        print(f"{task.status}, {type(task.status)}") # type: ignore
        if task is None:
            raise MessageServiceError(f"Task not found, task_id: '{task_id}', service_name: '{service_name}'")
        
        task.status = TaskStatus.RUNNING  # type: ignore
        task.start_date = datetime.datetime.now() # type: ignore
        task.worker_host = data.hostname  # type: ignore


