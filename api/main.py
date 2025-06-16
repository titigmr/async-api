from fastapi import FastAPI

from api.api.v1.routes import metrics, services, status, tasks
from api.core.config import settings
from api.core.utils import get_version
from api.core.utils import logger
from api.repositories.services_config_repository import ServicesConfigRepository

__version__, __name__ = get_version()

app = FastAPI(
    title=__name__,
    version=__version__,
    # lifespan=lifespan,
    summary=settings.PROJECT_DESCRIPTION,
)

logger.info("----------------------------")
logger.info("🚀 Starting async API")
logger.info("----------------------------")

logger.info("----------------------------")
logger.info("⏳ Loading services configuration ...")
print(f"Using services config file: {settings}")
ServicesConfigRepository.load_services_config(settings.SERVICES_CONFIG_FILE)
for service in ServicesConfigRepository.SERVICES:
    logger.info(f"- Service loaded: {service}")
logger.info("🤗 Done.")

logger.info("----------------------------")
logger.info("⏳ Registering API routes ...")
app.include_router(router=services.router, prefix="/v1", tags=["Services"])
app.include_router(router=tasks.router, prefix="/v1", tags=["Tasks"])
app.include_router(router=metrics.router, prefix="/internal", tags=["Metrics"])
app.include_router(router=status.router, prefix="/internal",tags=["Status"])
logger.info("🤗 Done.")

logger.info("----------------------------")


