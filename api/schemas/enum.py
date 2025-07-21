from enum import Enum


class ErrorEnum(Enum):
    """Error codes for the application."""

    TASK_NOT_FOUND = "Task not found"
    SERVICE_NOT_FOUND = "Service not found"
    SERVICE_UNAVAILABLE = "Service unavailable, please try again later"


class TaskStatus(Enum):
    """Status codes for the application."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"


class CallbackStatus(Enum):
    """Status codes for the callback."""

    SUCCESS = "success"
    FAILURE = "failure"
