from enum import Enum


class ErrorEnum(str, Enum):
    """Error codes for the application"""

    TASK_NOT_FOUND = "Task not found"
    SERVICE_NOT_FOUND = "Service not found"
    SERVICE_UNAVAILABLE = "Service unavailable, please try again later"


class TaskStatus(str, Enum):
    """Status codes for the application"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"


ERROR_MAP = {
    404001: (404, "Service not found."),
    400001: (400, "Error validating the body with the target service’s json-schema."),
    403001: (403, "Forbidden."),
    429001: (429, "Too many service requests"),
    429002: (429, "Too many service requests for the clientId."),
}