from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, Json


class TaskCallback(BaseModel):
    task_id: str = Field(..., description="Identifiant unique de la tâche")
    status: str = Field(..., description="Statut de la tâche (success, failure, etc.)")
    submission_date: datetime = Field(..., description="Date de soumission de la tâche")
    start_date: datetime = Field(..., description="Date de début de la tâche")
    end_date: datetime = Field(..., description="Date de fin de la tâche")
    progress: float = Field(
        ..., examples=[0.1, 1.0], description="Progression de la tâche en pourcentage"
    )
    response: Json[Any] = Field(..., description="Réponse du service cible")
