from sqlalchemy.orm import Session
from app.schema import QueueTask, QueueData, TaskRequest, TaskData
from app.service.queue_service import send_task_to_queue
from app.crud.task import create_task_record, get_task_by_id
from app.models import Task
from app.schema.enum import TaskStatus
import uuid
import json


def poll_task(db: Session, task_id: str, service: str)-> TaskData:
    """Poll a task by its ID"""
    task_info = get_task_by_id(db, task_id, service=service)
    return TaskData(**task_info)


def submit_task(db: Session, task: TaskRequest, service: str) -> TaskData:
    """Submit a new task"""
    task_id = str(uuid.uuid4())
    queue_message = QueueTask(task_id=task_id, data=QueueData(message_type="submission", body=task.body))
    send_task_to_queue(queue_message)

    task_obj = Task(
        task_id=task_id,
        client_id="default",
        service=service,
        status="pending",
        request=task.body,
        callback=task.callback.model_dump() if task.callback else None,
    )
    create_task_record(db, json.loads(task_obj.model_dump_json()))
    return TaskData(task_id=task_id, task_position=None, status=TaskStatus.PENDING.value)
