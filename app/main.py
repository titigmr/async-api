from fastapi import FastAPI

from app.api.v1.routes import health, services, tasks
from app.core.config import settings
from app.core.utils import get_version

__version__, __name__ = get_version()

app = FastAPI(title=__name__, version=__version__, summary=settings.PROJECT_DESCRIPTION)

app.include_router(services.router, prefix="/v1", tags=["Services"])
app.include_router(tasks.router, prefix="/v1", tags=["Tasks"])
app.include_router(health.router, tags=["Health"])
