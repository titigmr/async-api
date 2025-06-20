from typing import Generic, Literal, TypeVar
from pydantic import BaseModel, Field

#---------------------------------
# RabbitMQ Messages
#---------------------------------
class SuccessNotification(BaseModel):
    task_id:  str = Field(default=..., description="Id de la tâche.")
    status:  str = Field(default=..., description="Status de la tâche.")


#---------------------------------
# Service Exceptions
#---------------------------------
T = TypeVar('T')
class AbstractNotifier(Generic[T]):
    def accept(self, type: str):
        pass

    def notify(self, message: SuccessNotification):
        pass

