from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.core.config import settings

engine: AsyncEngine = create_async_engine(url=settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, class_=AsyncSession
)

# SQLModel.metadata.create_all(bind=engine)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
