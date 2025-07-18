from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from api.schemas.enum import TaskStatus


class Callback(BaseModel):
    url: str | None = Field(
        default=None,
        description="URL ou AMQP DSN à appeler en callback",
    )
    type: Literal["http", "amqp"] | None = Field(
        default=None,
        description="Type de callback (http ou amqp)",
    )
    queue: str | None = Field(
        default=None,
        description="Nom de la file d'attente pour les callbacks AMQP",
    )


class TaskInfo(BaseModel):
    task_id: str
    client_id: str
    service: str
    status: TaskStatus
    request: dict[str, Any]
    callback: Callback | None = None


class TaskDataPending(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    status: TaskStatus = TaskStatus.PENDING
    task_position: int | None = Field(default=None, description="Position de la tâche dans la file d'attente")
    submission_date: datetime | None = Field(default=None, description="Date de soumission de la tâche")


class TaskDataProgress(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    status: TaskStatus = TaskStatus.IN_PROGRESS
    progress: float | None = Field(default=None, description="Progression de la tâche (0.0 à 1.0)")
    submission_date: datetime | None = Field(default=None, description="Date de soumission de la tâche")
    start_date: datetime | None = Field(default=None, description="Date de début de la tâche")


class TaskDataFailed(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    status: TaskStatus = TaskStatus.FAILURE
    error_message: str | None = Field(
        default=...,
        description="Message d'erreur associé à la tâche",
    )
    submission_date: datetime | None = Field(default=None, description="Date de soumission de la tâche")
    start_date: datetime | None = Field(default=None, description="Date de début de la tâche")
    end_date: datetime | None = Field(default=None, description="Date de fin de la tâche")


class TaskDataSuccess(BaseModel):
    task_id: str = Field(default=..., description="Identifiant unique de la tâche")
    status: TaskStatus = TaskStatus.SUCCESS
    result: Any | None = Field(default=None, description="Résultat de la tâche")
    submission_date: datetime | None = Field(default=None, description="Date de soumission de la tâche")
    start_date: datetime | None = Field(default=None, description="Date de début de la tâche")
    end_date: datetime | None = Field(default=None, description="Date de fin de la tâche")


class TaskRequest(BaseModel):
    body: dict = Field(default=..., description="Paramètres à transmettre au service cible")
    callback: None | Callback = Field(default=None, description="Informations de callback optionnelles")


class TaskResponse(BaseModel):
    data: TaskDataSuccess | TaskDataFailed | TaskDataPending | TaskDataProgress = Field(
        default=...,
        description="Données de la tâche",
    )
    status: TaskStatus = Field(default=TaskStatus.SUCCESS, description="Statut de la création de la tâche")


class TaskErrorResponse(BaseModel):
    class Error(BaseModel):
        number: int = Field(default=..., description="Code d'erreur unique")
        description: str = Field(default=..., description="Description de l'erreur")

    status: str = Field(default="error", description="Statut de la réponse (toujours 'error')")
    error: Error = Field(default=..., description="Détails de l'erreur")
