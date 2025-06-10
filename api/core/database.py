from typing import Any, Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from api.core.config import settings
from api.models.task import SQLModel

engine: Engine = create_engine(url=settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

SQLModel.metadata.create_all(bind=engine)


def get_db_session() -> Generator[Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
