from enum import Enum


class ErrorEnum(str, Enum):
    TASK_NOT_FOUND: str = "Task not found"
    SERVICE_NOT_FOUND: str = "Service not found"
    SERVICE_UNAVAILABLE: str = "Service unavailable, please try again later"
    EXCEEDED_QUOTA: str = "Too many service requests for the user"
    FORBIDDEN: str = "Forbidden, insufficient permissions"
