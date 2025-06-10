from fastapi import FastAPI

from api.api.v1.routes import health, services, tasks
from api.core.config import settings
from api.core.utils import get_version

__version__, __name__ = get_version()

app = FastAPI(title=__name__, version=__version__, summary=settings.PROJECT_DESCRIPTION)

app.include_router(services.router, prefix="/v1", tags=["Services"])
app.include_router(tasks.router, prefix="/v1", tags=["Tasks"])
app.include_router(health.router, tags=["Health"])
