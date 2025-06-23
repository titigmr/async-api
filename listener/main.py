import asyncio
from listener.core.di_container import DIContainer
from listener.core.logger import logger

async def main():
    logger.info("----------------------------")
    logger.info("🚀 Starting the listener")
    logger.info("----------------------------")
    container = DIContainer()
    app = container.app()
    await app.start()
    logger.info("Listener stopped.")

if __name__ == "__main__": 
    asyncio.run(main())