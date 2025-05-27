from fastapi import FastAPI

from app.api.v1.routes import services, tasks
from app.core.config import settings

__version__, __name__ = get_version()

app = FastAPI(
    title=__name__,
    version=__version__,
    summary=settings.PROJECT_DESCRIPTION,
    # servers=settings.API_URLS,
)

app.include_router(services.router, prefix="/api/v1", tags=["Services"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
