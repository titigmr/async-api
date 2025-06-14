import http
import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from starlette.responses import JSONResponse

from api.schemas import (
    TaskCallback,
    TaskData,
    TaskErrorResponse,
    TaskRequest,
    TaskResponse,
)
from api.schemas.enum import ErrorEnum, TaskStatus
from api.schemas.errors import (
    InternalServerError,
    ServiceNotFound,
    TaskAPIException,
    TaskNotFound,
)
from api.services import ServiceService, TaskService

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
            enum=ServiceService.list_services_names(),
        ),
    ],
    task: Annotated[
        TaskRequest,
        Body(
            default=...,
            description="Représente la tâche à créer. Inclut le nom du service, les paramètres, et éventuellement un callback.",
        ),
    ],
    service_service: Annotated[ServiceService, Depends(ServiceService)],
    task_service: Annotated[TaskService, Depends(TaskService)],
) -> JSONResponse | TaskResponse:
    """
    Crée une tâche pour le service demandé.
    """
    try:
        try:
            service_service.check_service_exists(service=service)
        except ServiceNotFound as error:
            return error.to_response()
        task_data: TaskData = await task_service.submit_task(task=task, service=service)
        return TaskResponse(status=TaskStatus.SUCCESS, data=task_data)
    except TaskAPIException as error:
        return error.to_response()
    except Exception as error:
        logger.error(msg=f"Internal server error: {error}")
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
            enum=ServiceService.list_services_names(),
        ),
    ],
    task_id: Annotated[
        str,
        Path(default=..., description="Identifiant unique de la tâche à récupérer."),
    ],
    task_service: Annotated[TaskService, Depends(TaskService)],
) -> TaskResponse | JSONResponse:
    """
    Récupère le statut d'une tâche via son identifiant.
    - **task_id** : identifiant unique de la tâche
    """
    try:
        task_info: TaskData | None = await task_service.poll_task(
            task_id=task_id, service=service
        )
        if not task_info:
            return TaskNotFound().to_response()
        return TaskResponse(status=TaskStatus.PENDING, data=task_info)
    except Exception as error:
        return InternalServerError(details=str(error)).to_response()
