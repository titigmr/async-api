import os
import unittest

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


async_engine = create_async_engine(
  # "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/tasks", pool_size=10, echo=True, max_overflow=10
  "sqlite+aiosqlite:///demo.db", #pool_size=10, echo=True, max_overflow=10
)

TestingAsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)

@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    Base.metadata.create_all(bind=create_engine("sqlite:///demo.db", echo=True))
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
        task_id = "test_task5",
        client_id = "test_client",
        service = "test_service",
        status = TaskStatus.PENDING,
        request = {},
        callback = None,
    )
    task = await repo.create_task_record(task_info)
    assert task is not None
    
