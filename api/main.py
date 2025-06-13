from fastapi import FastAPI

from api.api.v1.routes import metrics, services, status, tasks
from api.core.config import settings
from api.core.utils import get_version

__version__, __name__ = get_version()

app = FastAPI(
    title=__name__,
    version=__version__,
    # lifespan=lifespan,
    summary=settings.PROJECT_DESCRIPTION,
)

app.include_router(router=services.router, prefix="/v1", tags=["Services"])
app.include_router(router=tasks.router, prefix="/v1", tags=["Tasks"])
app.include_router(router=metrics.router, tags=["Metrics"])
app.include_router(router=status.router, tags=["Status"])
