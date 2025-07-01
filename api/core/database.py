from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from api.core.config import settings

engine: AsyncEngine = create_async_engine(url=settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, class_=AsyncSession)

Base: Any = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
