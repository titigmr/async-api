import http
import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.orm import Session
from app.core.utils import generate_error_response
from app.core.config import ServiceLiteral, settings
from app.core.database import get_db_session
from app.schema import (
    TaskCallback,
    TaskErrorResponse,
    TaskPolling,
    TaskRequest,
    TaskResponse,
)
from app.schema.enum import ErrorEnum
from app.service.task_service import poll_task, submit_task

router = APIRouter(tags=["Tasks"])
callback_router = APIRouter()

logger = logging.getLogger("uvicorn.error")


@callback_router.post("{$callback.url}")
def receive_callback(body: TaskCallback):
    """
    Exemple d'endpoint pour recevoir le callback d'une tâche asynchrone.
    """
    pass


@router.post(
    "/services/{service}/tasks",
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
        ServiceLiteral,
        Path(
            ...,
            description="Nom du service pour lequel créer la tâche. Doit être dans la liste des services autorisés.",
        ),
    ],
    task: Annotated[
        TaskRequest,
        Body(
            ...,
            description="Représente la tâche à créer. Inclut le nom du service, les paramètres, et éventuellement un callback.",
        ),
    ],
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Crée une tâche pour le service demandé.
    """
    if service not in settings.SERVICE_LIST:
        return generate_error_response(404001)
    try:
        task_data = submit_task(db, task, service)
        return TaskResponse(status="success", data=task_data)
    except Exception as error:
        logger.exception(f"Erreur lors de la création de la tâche : {error}")
        return generate_error_response(501001)


@router.get(
    "/services/{service}/tasks/{task_id}",
    response_model=TaskPolling,
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
            ...,
            description="Nom du service pour lequel récupérer la tâche. Doit être dans la liste des services autorisés.",
        ),
    ],
    task_id: Annotated[str, Path(..., description="Identifiant unique de la tâche à récupérer.")],
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Récupère le statut d'une tâche via son identifiant.
    - **task_id** : identifiant unique de la tâche
    """
    try:
        task_info = poll_task(db, task_id, service=service)
        if not task_info:
            return generate_error_response(404001)
        return TaskPolling(status="success", data=task_info)
    except Exception as error:
        logger.exception(f"Erreur lors de la récupération de la tâche : {error}")
        return generate_error_response(500001)
