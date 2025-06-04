import http
import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.database import get_db_session
from app.schema import (
    TaskCallback,
    TaskData,
    TaskErrorResponse,
    TaskRequest,
    TaskResponse,
)
from app.schema.enum import ErrorEnum, TaskStatus
from app.schema.errors import InternalServerError, ServiceNotFound, TaskNotFound
from app.service import check_service_exists, poll_task, submit_task

router = APIRouter(tags=["Tasks"])
callback_router = APIRouter()

logger: logging.Logger = logging.getLogger(name="uvicorn.error")


@callback_router.post(path="{$callback.url}")
def receive_callback(body: TaskCallback) -> None:  # NOQA
    """
    Exemple d'endpoint pour recevoir le callback d'une tâche asynchrone.
    """
    pass


@router.post(
    path="/services/{service}/tasks",
    status_code=status.HTTP_201_CREATED,
    callbacks=callback_router.routes,
    response_model=TaskResponse,
    responses={
        404: {
            "model": TaskErrorResponse,
            "description": ErrorEnum.SERVICE_NOT_FOUND.value,
        },
        500: {
            "model": TaskErrorResponse,
            "description": http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
        },
    },
    summary="Créer une tâche asynchrone",
    description="""
Crée une tâche asynchrone pour un service donné.

- **service** : nom du service à appeler (doit être dans la liste autorisée)
- **body** : paramètres à transmettre au service cible (dépend du service)
- **callback** : URL à appeler une fois la tâche terminée (optionnel)
""",
)
async def create_task(
    service: Annotated[
        str,
        Path(
            default=...,
            description="Nom du service pour lequel créer la tâche. Doit être dans la liste des services autorisés.",
            enum=settings.SERVICE_LIST,
        ),
    ],
    task: Annotated[
        TaskRequest,
        Body(
            default=...,
            description="Représente la tâche à créer. Inclut le nom du service, les paramètres, et éventuellement un callback.",
        ),
    ],
    db: Annotated[Session, Depends(dependency=get_db_session)],
) -> JSONResponse | TaskResponse:
    """
    Crée une tâche pour le service demandé.
    """
    try:
        try:
            check_service_exists(service=service)
        except ServiceNotFound as error:
            return error.to_response()
        task_data: TaskData = submit_task(db=db, task=task, service=service)
        return TaskResponse(status=TaskStatus.SUCCESS, data=task_data)
    except ServiceNotFound as error:
        return error.to_response()
    except Exception as error:
        logger.exception(msg=f"Erreur lors de la création de la tâche : {error}")
        return InternalServerError(details=str(error)).to_response()


@router.get(
    path="/services/{service}/tasks/{task_id}",
    response_model=TaskResponse,
    responses={
        404: {
            "model": TaskErrorResponse,
            "description": ErrorEnum.TASK_NOT_FOUND.value,
        },
        500: {
            "model": TaskErrorResponse,
            "description": http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
        },
    },
    summary="Récupérer le statut d'une tâche",
    description="""
Permet de récupérer le statut d'une tâche asynchrone via son identifiant.

- **task_id** : identifiant unique de la tâche à interroger
""",
)
async def get_task(
    service: Annotated[
        str,
        Path(
            default=...,
            description="Nom du service pour lequel récupérer la tâche. Doit être dans la liste des services autorisés.",
        ),
    ],
    task_id: Annotated[
        str,
        Path(default=..., description="Identifiant unique de la tâche à récupérer."),
    ],
    db: Annotated[Session, Depends(dependency=get_db_session)],
) -> TaskResponse | JSONResponse:
    """
    Récupère le statut d'une tâche via son identifiant.
    - **task_id** : identifiant unique de la tâche
    """
    try:
        task_info: TaskData | None = poll_task(db=db, task_id=task_id, service=service)
        if not task_info:
            return TaskNotFound(
                details=f"Tâche '{task_id}' introuvable pour le service '{service}'."
            ).to_response()
        return TaskResponse(status=TaskStatus.PENDING, data=task_info)
    except Exception as error:
        logger.exception(msg=f"Erreur lors de la récupération de la tâche : {error}")
        return InternalServerError(details=str(error)).to_response()
