import os
import unittest
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import create_engine


from api.core.database import AsyncSessionLocal, Base
from api.repositories.task_repository import TaskRepository
from api.schemas.enum import TaskStatus
from api.schemas.task import TaskInfo

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base




@pytest_asyncio.fixture(scope="function", autouse=True)
async def async_db_session():
    async_engine = create_async_engine(
    "sqlite+aiosqlite:///demo.db", echo=True
    )

    TestingAsyncSessionLocal = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession,
    )
    Base.metadata.create_all(bind=create_engine(f"sqlite:///demo.db", echo=True))
    connection = await async_engine.connect()
    trans = await connection.begin()
    async_session = TestingAsyncSessionLocal(bind=connection)

    yield async_session

    if trans.is_valid:
        await trans.rollback()
    await async_session.close()
    await connection.close()
    os.remove("demo.db")

@pytest.mark.asyncio
async def test_should_create_new_task(async_db_session):
    repo = TaskRepository(async_db_session)
    task_info = TaskInfo (
        task_id = "test_task",
        client_id = "test_client",
        service = "test_service",
        status = TaskStatus.PENDING,
        request = {},
        callback = None,
    )
    task = await repo.create_task_record(task_info)
    assert task is not None
    
@pytest.mark.asyncio
async def test_get_task_by_id(async_db_session):
    repo = TaskRepository(async_db_session)
    task_info1 = TaskInfo (
        task_id = "test_task1", client_id = "test_client1", service = "test_service1", status = TaskStatus.PENDING, request = {}, callback = None
    )
    task_info2 = TaskInfo (
        task_id = "test_task2", client_id = "test_client2", service = "test_service2", status = TaskStatus.PENDING, request = {}, callback = None
    )
    await repo.create_task_record(task_info1)
    await repo.create_task_record(task_info2)

    task = await repo.get_task_by_id("test_task2","test_service2")
    assert task is not None
    assert str(task.client_id) == "test_client2"

@pytest.mark.asyncio
async def test_get_task_position_by_id(async_db_session):
    repo = TaskRepository(async_db_session)
    task_info = TaskInfo (
        task_id = f"test_task_run", client_id = "test_task_run", service = "svc", status = TaskStatus.RUNNING, request = {}, callback = None
    )
    await repo.create_task_record(task_info)
    for i in range(0,3):
        task_info = TaskInfo (
            task_id = f"test_task{i}", client_id = "test_task{i}", service = "svc", status = TaskStatus.PENDING, request = {}, callback = None
        )
        await repo.create_task_record(task_info)

    added = TaskInfo (
        task_id = "test_added", client_id = "test_added", service = "svc", status = TaskStatus.PENDING, request = {}, callback = None
    )
    await repo.create_task_record(added)

    position = await repo.get_task_position_by_id("test_added","svc")
    assert position is not None
    assert position == 4

@pytest.mark.asyncio
async def test_count_pending_tasks_for_service(async_db_session):
    repo = TaskRepository(async_db_session)
    # 3 PENDING
    for i in range(0,3):
        task_info = TaskInfo (
            task_id = f"test_task{i}", client_id = "test_task{i}", service = "svc", status = TaskStatus.PENDING, request = {}, callback = None
        )
        await repo.create_task_record(task_info)
    # 1 RUNNING
    task_running = TaskInfo (
        task_id = f"test_task_running", client_id = "test_task_running", service = "svc", status = TaskStatus.RUNNING, request = {}, callback = None
    )
    await repo.create_task_record(task_running)
    # 1 Another service
    task_other = TaskInfo (
        task_id = f"test_task_task_other", client_id = "test_task_running", service = "task_other", status = TaskStatus.RUNNING, request = {}, callback = None
    )
    await repo.create_task_record(task_other)

    nbr = await repo.count_pending_tasks_for_service("svc")
    assert nbr == 3


@pytest.mark.asyncio
async def test_count_pending_tasks_for_service_and_client(async_db_session):
    repo = TaskRepository(async_db_session)
    # 3 PENDING (client à tester)
    for i in range(0,3):
        task_info = TaskInfo (
            task_id = f"test_task{i}", client_id = "client", service = "svc", status = TaskStatus.PENDING, request = {}, callback = None
        )
        await repo.create_task_record(task_info)
    # 4 PENDING (un autre client)
    for i in range(0,3):
        task_info = TaskInfo (
            task_id = f"other_test_task{i}", client_id = "other_client", service = "svc", status = TaskStatus.PENDING, request = {}, callback = None
        )
        await repo.create_task_record(task_info)
    # 1 RUNNING
    task_running = TaskInfo (
        task_id = f"test_task_running", client_id = "client", service = "svc", status = TaskStatus.RUNNING, request = {}, callback = None
    )
    await repo.create_task_record(task_running)
    # 1 Another service
    task_other = TaskInfo (
        task_id = f"client_other_svc", client_id = "client", service = "task_other", status = TaskStatus.RUNNING, request = {}, callback = None
    )
    await repo.create_task_record(task_other)

    nbr = await repo.count_pending_tasks_for_service_and_client("svc","client")
    assert nbr == 3
