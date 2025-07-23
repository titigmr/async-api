import asyncio
from typing import TYPE_CHECKING

from api.core.config import Settings
from listener.core.di_container import DIContainer
from listener.core.logger import logger

if TYPE_CHECKING:
    from listener.services.queue_listener import QueueListener


async def main() -> None:
    logger.info("----------------------------")
    logger.info("🚀 Starting the listener")
    logger.info("----------------------------")
    container = DIContainer(Settings())
    app: QueueListener = container.app()
    await app.start()
    logger.info("Listener stopped.")


if __name__ == "__main__":
    asyncio.run(main())
