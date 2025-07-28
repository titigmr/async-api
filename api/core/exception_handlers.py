from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from api.schemas.errors import AppException, InternalServerError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(exc_class_or_status_code=AppException)
    def base_exception_handler(request: Request, exc: AppException) -> JSONResponse:  # noqa: ARG001
        return exc.to_response()

    @app.exception_handler(exc_class_or_status_code=Exception)
    def exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
        return InternalServerError(details="Internal server error").to_response()
