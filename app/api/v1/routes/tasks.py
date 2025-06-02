import http
import json
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import ServiceLiteral, settings
from app.core.database import get_db_session
from app.models.task import Task
from app.schema import (
    QueueData,
    QueueTask,
    TaskCallback,
    TaskErrorResponse,
    TaskPolling,
    TaskRequest,
    TaskResponse,
)
from app.schema.enum import ErrorEnum
from app.schema.task import TaskData
from app.service.queue_service import send_task_to_queue
from app.service.task_service import add_task_to_db, get_task_from_db

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
            examples={
                "default": {
                    "summary": "Exemple de création de tâche",
                    "value": {
                        "body": {"param1": "valeur1", "param2": 42},
                        "callback": {},
                    },
                    "callback": {
                        "summary": "Exemple de création de tâche",
                        "value": {
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
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Crée une tâche pour le service demandé.
    """
    if service not in settings.SERVICE_LIST:
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
        queue_message = QueueTask(
            task_id=task_id, data=QueueData(message_type="submission", body=task.body)
        )
        send_task_to_queue(queue_message)

        task_obj = Task(
            task_id=task_id,
            client_id="default",
            service=service,
            status="pending",
            request=task.body,
            callback=task.callback.model_dump() if task.callback else None,
        )
        add_task_to_db(db, json.loads(task_obj.model_dump_json()))
    except Exception as error:
        logger.exception(f"Erreur lors de la création de la tâche : {error}")
        return JSONResponse(
            status_code=500,
            content=TaskErrorResponse(
                error=TaskErrorResponse.Error(
                    number=500_001,
                    description=str(error),
                )
            ).model_dump(),
        )
    return TaskResponse(data=TaskData(task_id=task_id, status="success"))


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

- **task_id** : identifiant unique de la tâche à interroger
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
        task = get_task_from_db(db, task_id, service=service)
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
