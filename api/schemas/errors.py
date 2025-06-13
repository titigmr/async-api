from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.core.utils import logger


class ErrorDetail(BaseModel):
    number: int = Field(default=..., description="Code d'erreur unique")
    description: str = Field(default=..., description="Description de l'erreur")
    details: str | None = Field(default=None, description="Détails optionnels")


class TaskErrorResponse(BaseModel):
    status: str = Field(
        default="error", description="Statut de la réponse (toujours 'error')"
    )
    error: ErrorDetail = Field(default=..., description="Détails de l'erreur")


class TaskAPIException(Exception):
    status_code: int = 500
    number: int = 500000
    description: str = "Internal server error"

    def __init__(self, details: str | None = None) -> None:
        self.details: str | None = details
        logger.error(
            msg=f"Internal server error: {self.number} - {self.description}",
            extra={"details": self.details},
        )

    def to_response(self) -> JSONResponse:
        error = ErrorDetail(
            number=self.number,
            description=self.description,
            details=self.details,
        )
        response = TaskErrorResponse(error=error)
        return JSONResponse(
            status_code=self.status_code,
            content=response.model_dump(exclude_none=True),
        )


class ServiceNotFound(TaskAPIException):
    status_code = 404
    number = 404001
    description = "Service not found"


class TaskNotFound(TaskAPIException):
    status_code = 404
    number = 404002
    description = "Task not found"


class Forbidden(TaskAPIException):
    status_code = 403
    number = 403001
    description = "Forbidden"


class TooManyRequests(TaskAPIException):
    status_code = 429
    number = 429001
    description = "Too many service requests"


class Unauthorized(TaskAPIException):
    status_code = 401
    number = 401001
    description = "Authentication required"


class InternalServerError(TaskAPIException):
    status_code = 500
    number = 500000
    description = "Internal server error"


class NotImplemented(TaskAPIException):
    status_code = 501
    number = 501001
    description = "Not implemented"


class BodyValidationError(TaskAPIException):
    status_code = 400
    number = 400001
    description = "Body validation error"
