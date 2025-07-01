from fastapi import FastAPI, Request

from api.schemas.errors import AppException, InternalServerError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def base_exception_handler(request: Request, exc: AppException):
        return exc.to_response()

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        return InternalServerError(details="Internal server error").to_response()
