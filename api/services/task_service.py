import uuid

from jsonschema import validate

from api.core.database import AsyncSession
from api.crud.task import create_task_record, get_task_by_id
from api.models import Task
from api.schemas import QueueData, QueueTask, ServiceInfo, TaskData, TaskRequest
from api.schemas.enum import TaskStatus
from api.schemas.errors import BodyValidationError
from api.services import list_services_config, send_task_to_queue


def check_service_schema(service: str, body: dict) -> None:
    """
    Vérifie que le body est conforme au json_schema du service (si défini).
    Lève BodyValidationError si la validation échoue.
    """
    service_obj: ServiceInfo | None = next(
        (s for s in list_services_config() if s.name == service), None
    )
    if service_obj and service_obj.json_schema:
        try:
            validate(instance=body, schema=service_obj.json_schema)
        except Exception as e:
            raise BodyValidationError(
                details=f"Erreur de validation du body avec le json-schema du service '{service_obj.name}': {e}"
            )


async def poll_task(db: AsyncSession, task_id: str, service: str) -> TaskData | None:
    """Poll a task by its ID"""
    task_info: Task | None = await get_task_by_id(
        db=db, task_id=task_id, service=service
    )
    if task_info:
        return TaskData(
            task_id=task_info.task_id,
            task_position=None,
            status=TaskStatus(value=task_info.status),
        )


async def submit_task(db: AsyncSession, task: TaskRequest, service: str) -> TaskData:
    """Submit a new task"""
    check_service_schema(service=service, body=task.body)
    task_id = str(uuid.uuid4())
    queue_message = QueueTask(
        task_id=task_id, data=QueueData(message_type="submission", body=task.body)
    )
    send_task_to_queue(task_data=queue_message, service=service)

    task_obj = Task(
        task_id=task_id,
        client_id="default",
        service=service,
        status=TaskStatus.PENDING.value,
        request=task.body,
        callback=task.callback.model_dump() if task.callback else None,
    )
    await create_task_record(db=db, task_data=task_obj.model_dump())
    return TaskData(task_id=task_id, task_position=None, status=TaskStatus.PENDING)
