from typing import Any, Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.core.config import settings

engine: Engine = create_engine(url=settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base: Any = declarative_base()

# Base.metadata.create_all(bind=engine)


def get_db_session() -> Generator[Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
