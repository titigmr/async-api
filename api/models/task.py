from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Float, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from api.core.database import Base


class Task(Base):
    __tablename__: str = "task"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String, nullable=False)
    service: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(default="pending", nullable=False)
    request: Mapped[dict] = mapped_column(JSON, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(nullable=True)
    progress: Mapped[float] = mapped_column(default=0.0, nullable=False)
    response: Mapped[Optional[str]] = mapped_column(nullable=True)
    callback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    submition_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False, server_default=func.now()
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    notification_status: Mapped[Optional[str]] = mapped_column(nullable=True)
    worker_host: Mapped[Optional[str]] = mapped_column(nullable=True)
