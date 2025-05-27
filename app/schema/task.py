from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field
from pydantic.networks import AmqpDsn, HttpUrl


class TaskData(BaseModel):
    task_id: str = Field(..., description="Identifiant unique de la tâche")
    status: str = Field(
        ...,
        description="Statut actuel de la tâche (pending, in_progress, success, failure, etc.)",
    )
    task_position: int | None = Field(
        None, description="Position de la tâche dans la file d'attente"
    )
    submission_date: datetime | None = Field(
        None, description="Date de soumission de la tâche"
    )


class Callback(BaseModel):
    url: AmqpDsn | HttpUrl | None = Field(
        None, description="URL ou AMQP DSN à appeler en callback"
    )
    type: Literal["http", "amqp"] | None = Field(
        None, description="Type de callback (http ou amqp)"
    )


class TaskRequest(BaseModel):
    service: str = Field(..., description="Nom du service à appeler")
    body: Any = Field(..., description="Paramètres à transmettre au service cible")
    callback: None | Callback = Field(
        default=None, description="Informations de callback optionnelles"
    )


class TaskResponse(BaseModel):
    data: TaskData = Field(..., description="Données de la tâche créée")
    status: Literal["pending", "failure", "in_progress", "success"] = Field(
        "success", description="Statut de la création de la tâche"
    )


class TaskErrorResponse(BaseModel):
    class Error(BaseModel):
        number: int = Field(..., description="Code d'erreur unique")
        description: str = Field(..., description="Description de l'erreur")

    status: str = Field("error", description="Statut de la réponse (toujours 'error')")
    error: Error = Field(..., description="Détails de l'erreur")


class TaskPolling(BaseModel):
    status: str = Field(..., description="Statut de la requête")
    data: TaskData = Field(..., description="Données de la tâche")
