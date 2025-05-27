import http
import logging
import uuid
from typing import Annotated

from core.config import settings
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schema import (
    TaskCallback,
    TaskErrorResponse,
    TaskPolling,
    TaskRequest,
    TaskResponse,
)
from app.schema.enum import ErrorEnum
from app.service.queue_service import send_task_to_queue
from app.service.task_service import add_task_to_db, get_task_from_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])
callback_router = APIRouter()

# Configuration du logger pour voir les erreurs dans les logs uvicorn
logger = logging.getLogger("uvicorn.error")


@callback_router.post("{$callback.url}")
def receive_callback(body: TaskCallback):
    """
    Exemple d'endpoint pour recevoir le callback d'une tâche asynchrone.
    """
    pass


@router.post(
    "/",
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
    task: Annotated[
        TaskRequest,
        Body(
            ...,
            description="Représente la tâche à créer. Inclut le nom du service, les paramètres, et éventuellement un callback.",
            examples={
                "default": {
                    "summary": "Exemple de création de tâche",
                    "value": {
                        "service": "mon_service",
                        "body": {"param1": "valeur1", "param2": 42},
                        "callback": {},
                    },
                    "callback": {
                        "summary": "Exemple de création de tâche",
                        "value": {
                            "service": "mon_service",
                            "body": {"param1": "valeur1", "param2": 42},
                            "callback": {
                                "url": "https://monapp/callback",
                                "type": "http",
                            },
                        },
                    },
                }
            },
        ),
    ],
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Crée une tâche pour le service demandé.
    - **service** : nom du service à appeler
    - **body** : paramètres à passer au service
    - **callback** : URL de rappel optionnelle
    """
    if task.service not in settings.SERVICE_LIST:
        return JSONResponse(
            status_code=404,
            content=TaskErrorResponse(
                error=TaskErrorResponse.Error(
                    number=404_001,
                    description=ErrorEnum.SERVICE_NOT_FOUND.value,
                )
            ).model_dump(),
        )
    task_id = str(uuid.uuid4())
    try:
        background_tasks.add_task(send_task_to_queue, task.model_dump_json())
        add_task_to_db(db, task.model_dump())
    except Exception as e:
        logger.exception(f"Erreur lors de la création de la tâche : {e}")
        return JSONResponse(
            status_code=500,
            content=TaskErrorResponse(
                error=TaskErrorResponse.Error(
                    number=500_001,
                    description=http.HTTPStatus.INTERNAL_SERVER_ERROR.description,
                )
            ).model_dump_(),
        )
    return TaskResponse(task_id=task_id, status="success")


@router.get(
    "/{task_id}",
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

- **task_id** : identifiant unique de la tâche à interroger
""",
)
async def get_task(
    task_id: Annotated[
        str, Path(..., description="Identifiant unique de la tâche à récupérer.")
    ],
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Récupère le statut d'une tâche via son identifiant.
    - **task_id** : identifiant unique de la tâche
    """
    try:
        task = get_task_from_db(db, task_id)
        if not task:
            return JSONResponse(
                status_code=404,
                content=TaskErrorResponse(
                    error=TaskErrorResponse.Error(
                        number=404_001,
                        description=ErrorEnum.SERVICE_NOT_FOUND.value,
                    )
                ).model_dump(),
            )
        return TaskPolling(
            status="success",
            data=TaskPolling.TaskData(
                task_id=task.task_id,
                status=task.status,
                submission_date=task.submission_date,
            ),
        )
    except Exception as error:
        logger.exception(f"Erreur lors de la récupération de la tâche : {error}")
        return JSONResponse(
            status_code=500,
            content=TaskErrorResponse(
                error=TaskErrorResponse.Error(
                    number=500_001,
                    description=http.HTTPStatus.INTERNAL_SERVER_ERROR.description,
                )
            ).model_dump(),
        )
