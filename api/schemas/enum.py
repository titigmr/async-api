from enum import Enum


class ErrorEnum(str, Enum):

    """Error codes for the application."""

    TASK_NOT_FOUND = "Task not found"
    SERVICE_NOT_FOUND = "Service not found"
    SERVICE_UNAVAILABLE = "Service unavailable, please try again later"


class TaskStatus(str, Enum):

    """Status codes for the application."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
