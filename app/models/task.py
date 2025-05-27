from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    client_id = Column(String, nullable=False)
    service = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    request = Column(JSON, nullable=False)
    error_message = Column(String, nullable=True)
    progress = Column(Float, nullable=False, default=0.0)
    response = Column(String, nullable=True)
    callback = Column(JSON, nullable=True)
    submition_date = Column(DateTime, nullable=False, default=datetime.now())
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    notification_status = Column(String, nullable=True)
    worker_host = Column(String, nullable=True)
