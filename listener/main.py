import asyncio
from typing import TYPE_CHECKING

from api.core.config import Settings
from listener.core.di_container import DIContainer
from listener.core.logger import logger

if TYPE_CHECKING:
    from listener.services.health_check import HealthCheckServer
    from listener.services.queue_listener import QueueListener


async def main() -> None:
    logger.info("🚀 Starting the listener")
    settings = Settings()
    container = DIContainer(settings=settings)
    queue_listener: QueueListener = container.queue_listener()
    health_check_server: HealthCheckServer = container.health_check_server()
    await health_check_server.start()

    try:
        await queue_listener.start()
    finally:
        logger.info("Stopping health check server")
        await health_check_server.stop()
    logger.info("Listener stopped.")


if __name__ == "__main__":
    asyncio.run(main())
