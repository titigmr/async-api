from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from api.core.database import Base


class Task(Base):
    __tablename__: str = "task"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    client_id = Column(String, nullable=False)
    service = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    request = Column(JSON, nullable=False)
    error_message = Column(String, nullable=True)
    progress = Column(Float, default=0.0, nullable=False)
    response = Column(String, nullable=True)
    callback = Column(JSON, nullable=True)
    submition_date = Column(
        DateTime, default=datetime.now, nullable=False, server_default=func.now()
    )
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    notification_status = Column(String, nullable=True)
    worker_host = Column(String, nullable=True)
