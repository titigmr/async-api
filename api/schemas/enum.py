from enum import StrEnum


class ErrorEnum(StrEnum):
    """Error codes for the application."""

    TASK_NOT_FOUND = "Task not found"
    SERVICE_NOT_FOUND = "Service not found"
    SERVICE_UNAVAILABLE = "Service unavailable, please try again later"


class TaskStatus(StrEnum):
    """Status codes for the application."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"


class CallbackStatus(StrEnum):
    """Status codes for the callback."""

    SUCCESS = "success"
    FAILURE = "failure"
