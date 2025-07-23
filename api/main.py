# Configuration des logs en premier pour intercepter uvicorn
from fastapi import FastAPI

from api.api.v1.routes import metrics, services, status, tasks
from api.core.config import settings
from api.core.exception_handlers import register_exception_handlers
from api.core.logger import logger
from api.core.utils import get_version
from api.repositories.client_config_repository import ClientConfigRepository
from api.repositories.services_config_repository import ServicesConfigRepository

__version__, __name__ = get_version()

logger.info("----------------------------")
logger.info("🚀 Starting async API")
logger.info("----------------------------")

logger.info("----------------------------")
logger.info("⏳ Loading services configuration ...")
logger.info(f"Using services config file: {settings.SERVICES_CONFIG_FILE}")
ServicesConfigRepository.load_services_config(settings.SERVICES_CONFIG_FILE)
for service in ServicesConfigRepository.SERVICES:
    logger.info(f"- Service loaded: {service}")
logger.info("🤗 Done.")

logger.info("----------------------------")
logger.info("⏳ Loading clients configuration ...")
logger.info(f"Using clients config file: {settings.CLIENTS_CONFIG_FILE}")
ClientConfigRepository.load_clients_config(settings.CLIENTS_CONFIG_FILE)
for client in ClientConfigRepository.CLIENTS:
    logger.info(f"- client loaded: {client}")
logger.info("🤗 Done.")

logger.info("----------------------------")
logger.info("⏳ Registering API routes ...")
app = FastAPI(
    title=__name__,
    version=__version__,
    summary=settings.PROJECT_DESCRIPTION,
)
register_exception_handlers(app)

app.include_router(router=services.router, prefix="/v1", tags=["Services"])
app.include_router(router=tasks.router, prefix="/v1", tags=["Tasks"])
app.include_router(router=metrics.router, prefix="/internal", tags=["Metrics"])
app.include_router(router=status.router, prefix="/internal", tags=["Status"])
logger.info("🤗 Done.")
logger.info("----------------------------")
