from typing import Any, Dict

from pydantic import BaseModel, Field


class QueueData(BaseModel):
    message_type: str = Field(
        default=..., description="Type du message (ex: submission)"
    )
    body: Dict[str, Any] = Field(default=..., description="Payload de la tâche")


class QueueTask(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    data: QueueData = Field(default=..., description="Données de la tâche à soumettre")
