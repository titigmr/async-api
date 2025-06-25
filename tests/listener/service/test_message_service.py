

import datetime
from unittest.mock import Mock
import pytest

from api.models.task import Task
from api.repositories.task_repository import TaskRepository
from api.schemas.enum import TaskStatus
from listener.services.message_service import MessageService, MessageServiceError, StartMessage
from listener.services.notifier_service import NotificationException, NotificationService
from sqlalchemy.ext.asyncio import AsyncSession 

@pytest.fixture(scope="function")
def message_service() -> MessageService:
    task_repository: TaskRepository = Mock()
    notification_service: NotificationService = Mock()
    session: AsyncSession  = Mock()
    svc = MessageService(
        task_repository, 
        notification_service,
        session,
    )

    task_found = Task(task_id = "task_found")
    task_found_with_callback =  Task(task_id = "task_found_with_callback",callback="{\"type\":\"foo\"}", submition_date = datetime.datetime.now(), start_date = datetime.datetime.now())
    async def get_task_by_id(task_id, service_name):
        if task_id == "task_found":
            return task_found
        if task_id == "task_found_with_callback":
            return task_found_with_callback
        return None
    task_repository.get_task_by_id.side_effect = get_task_by_id

    async def rollback(): pass
    session.rollback.side_effect = rollback
    async def close(): pass
    session.close.side_effect = close
    async def commit(): pass
    session.commit.side_effect = commit
    return svc

#---------------------
# START
#---------------------
@pytest.mark.asyncio
async def test_process_start_message_error_unmarshall(message_service):
    with pytest.raises(MessageServiceError):
        await message_service.process("{\"value\":\"bob\"}","svc_name")
    message_service.session.rollback.assert_called()
    message_service.session.close.assert_called()

@pytest.mark.asyncio
async def test_process_start_message_task_not_found(message_service):
    with pytest.raises(MessageServiceError):
        await message_service.process("{\"task_id\":\"task_not_found\", \"data\": {\"message_type\":\"started\",\"hostname\":\"muhost\"}}","svc_name")
    message_service.session.rollback.assert_called()
    message_service.session.close.assert_called()

@pytest.mark.asyncio
async def test_process_start_message_task_ok(message_service):
    await message_service.process("{\"task_id\":\"task_found\", \"data\": {\"message_type\":\"started\",\"hostname\":\"myhost\"}}","svc_name")
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()
    task = await message_service.task_repository.get_task_by_id("task_found","svc")
    assert task.status == "running"
    assert task.start_date is not None
    assert task.worker_host == "myhost"
    assert task.progress == 0

#---------------------
# PROGRESS
#---------------------
@pytest.mark.asyncio
async def test_process_progress_message_task_not_found(message_service):
    with pytest.raises(MessageServiceError):
        await message_service.process("{\"task_id\":\"task_not_found\", \"data\": {\"message_type\":\"progress\",\"progress\":42}}","svc_name")
    message_service.session.rollback.assert_called()
    message_service.session.close.assert_called()

@pytest.mark.asyncio
async def test_process_progress_message_task_ok(message_service):
    await message_service.process("{\"task_id\":\"task_found\", \"data\": {\"message_type\":\"progress\",\"progress\":42}}","svc_name")
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()
    task = await message_service.task_repository.get_task_by_id("task_found","svc")
    assert task.progress == 42

#---------------------
# SUCCESS
#---------------------
@pytest.mark.asyncio
async def test_process_success_message_task_not_found(message_service):
    with pytest.raises(MessageServiceError):
        await message_service.process("{\"task_id\":\"task_not_found\", \"data\": {\"message_type\":\"success\",\"response\":{}}}","svc_name")
    message_service.session.rollback.assert_called()
    message_service.session.close.assert_called()

@pytest.mark.asyncio
async def test_process_success_message_task_ok(message_service):
    await message_service.process("{\"task_id\":\"task_found\", \"data\": {\"message_type\":\"success\",\"response\":{}}}","svc_name")
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()

@pytest.mark.asyncio
async def test_process_success_message_with_callback_ok(message_service):
    async def notification_ok(callback, message): pass
    #async def notification_ko(callback, message): raise NotificationException 

    message_service.notification_service.notify.side_effect = notification_ok

    await message_service.process("{\"task_id\":\"task_found_with_callback\", \"data\": {\"message_type\":\"success\",\"response\":{\"value\": 42}}}","svc_name")
    
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()

    task = await message_service.task_repository.get_task_by_id("task_found_with_callback","svc")
    assert task.status == TaskStatus.SUCCESS
    assert task.response == "{\"value\": 42}"
    assert task.notification_status == "SUCCESS"

@pytest.mark.asyncio
async def test_process_success_message_with_callback_ko(message_service):
    #async def notification_ok(callback, message): pass
    async def notification_ko(callback, message): raise NotificationException 

    message_service.notification_service.notify.side_effect = notification_ko

    await message_service.process("{\"task_id\":\"task_found_with_callback\", \"data\": {\"message_type\":\"success\",\"response\":{\"value\": 42}}}","svc_name")
    
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()

    task = await message_service.task_repository.get_task_by_id("task_found_with_callback","svc")
    assert task.status == TaskStatus.SUCCESS
    assert task.response == "{\"value\": 42}"
    assert task.notification_status == "FAILURE"

#---------------------
# FAILURE
#---------------------
@pytest.mark.asyncio
async def test_process_failure_message_task_not_found(message_service):
    with pytest.raises(MessageServiceError):
        await message_service.process("{\"task_id\":\"task_not_found\", \"data\": {\"message_type\":\"failure\",\"error_message\":\"Arghh!\"}}","svc_name")
    message_service.session.rollback.assert_called()
    message_service.session.close.assert_called()

@pytest.mark.asyncio
async def test_process_failure_message_task_ok(message_service):
    await message_service.process("{\"task_id\":\"task_found\", \"data\": {\"message_type\":\"failure\",\"error_message\":\"Arghh!\"}}","svc_name")
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()

@pytest.mark.asyncio
async def test_process_failure_message_with_callback_ok(message_service):
    async def notification_ok(callback, message): pass
    #async def notification_ko(callback, message): raise NotificationException 

    message_service.notification_service.notify.side_effect = notification_ok

    await message_service.process("{\"task_id\":\"task_found_with_callback\", \"data\": {\"message_type\":\"failure\",\"error_message\":\"Arghh!\"}}","svc_name")
    
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()

    task = await message_service.task_repository.get_task_by_id("task_found_with_callback","svc")
    assert task.status == TaskStatus.FAILURE
    assert task.error_message == "Arghh!"
    assert task.notification_status == "SUCCESS"

@pytest.mark.asyncio
async def test_process_failure_message_with_callback_ko(message_service):
    #async def notification_ok(callback, message): pass
    async def notification_ko(callback, message): raise NotificationException 

    message_service.notification_service.notify.side_effect = notification_ko

    await message_service.process("{\"task_id\":\"task_found_with_callback\", \"data\": {\"message_type\":\"failure\",\"error_message\":\"Arghh!\"}}","svc_name")
    
    message_service.session.commit.assert_called()
    message_service.session.close.assert_called()

    task = await message_service.task_repository.get_task_by_id("task_found_with_callback","svc")
    assert task.status == TaskStatus.FAILURE
    assert task.error_message == "Arghh!"
    assert task.notification_status == "FAILURE"