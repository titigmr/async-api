from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    task_id: str = Field(index=True, nullable=False, unique=True)
    client_id: str = Field(nullable=False)
    service: str = Field(nullable=False)
    status: str = Field(default="pending", nullable=False)
    request: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    error_message: Optional[str] = Field(default=None)
    progress: float = Field(default=0.0, nullable=False)
    response: Optional[str] = Field(default=None)
    callback: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    submition_date: datetime = Field(default_factory=datetime.now, nullable=False)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    notification_status: Optional[str] = Field(default=None)
    worker_host: Optional[str] = Field(default=None)
