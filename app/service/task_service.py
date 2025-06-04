import json
import uuid

from sqlalchemy.orm import Session

from app.crud.task import create_task_record, get_task_by_id
from app.models import Task
from app.schema import QueueData, QueueTask, TaskData, TaskRequest
from app.schema.enum import TaskStatus
from app.service import send_task_to_queue


def poll_task(db: Session, task_id: str, service: str) -> TaskData | None:
    """Poll a task by its ID"""
    task_info: Task | None = get_task_by_id(db=db, task_id=task_id, service=service)
    if task_info:
        return TaskData(
            task_id=task_info.task_id,
            task_position=None,
            status=TaskStatus(value=task_info.status),
        )


def submit_task(db: Session, task: TaskRequest, service: str) -> TaskData:
    """Submit a new task"""
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
    create_task_record(db=db, task_data=json.loads(s=task_obj.model_dump_json()))
    return TaskData(task_id=task_id, task_position=None, status=TaskStatus.PENDING)
