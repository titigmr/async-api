from typing import Any, Dict

from pydantic import BaseModel, Field


class QueueData(BaseModel):
    messageType: str = Field(..., description="Type du message (ex: submission)")
    body: Dict[str, Any] = Field(..., description="Payload de la tâche")


class QueueTaskSubmission(BaseModel):
    taskId: str = Field(..., description="Identifiant unique de la tâche")
    data: QueueData = Field(..., description="Données de la tâche à soumettre")
