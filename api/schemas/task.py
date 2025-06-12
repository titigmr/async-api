from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from pydantic.networks import AmqpDsn, HttpUrl

from api.schemas.enum import TaskStatus


class TaskData(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Statut actuel de la tâche (pending, in_progress, success, failure, etc.)",
    )
    task_position: int | None = Field(
        default=None, description="Position de la tâche dans la file d'attente"
    )
    submission_date: datetime | None = Field(
        default=None, description="Date de soumission de la tâche"
    )


class Callback(BaseModel):
    url: AmqpDsn | HttpUrl | None = Field(
        default=None, description="URL ou AMQP DSN à appeler en callback"
    )
    type: Literal["http", "amqp"] | None = Field(
        default=None, description="Type de callback (http ou amqp)"
    )


class TaskRequest(BaseModel):
    body: dict = Field(
        default=..., description="Paramètres à transmettre au service cible"
    )
    callback: None | Callback = Field(
        default=None, description="Informations de callback optionnelles"
    )


class TaskResponse(BaseModel):
    data: TaskData = Field(default=..., description="Données de la tâche créée")
    status: TaskStatus = Field(
        default=TaskStatus.SUCCESS, description="Statut de la création de la tâche"
    )


class TaskErrorResponse(BaseModel):
    class Error(BaseModel):
        number: int = Field(default=..., description="Code d'erreur unique")
        description: str = Field(default=..., description="Description de l'erreur")

    status: str = Field(
        default="error", description="Statut de la réponse (toujours 'error')"
    )
    error: Error = Field(default=..., description="Détails de l'erreur")
