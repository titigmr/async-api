
# import asyncio
# from time import sleep
# from typing import Annotated

# from fastapi import Depends
# from fastapi_injectable import injectable

# from api.core.brokers.rabbitmq import RabbitMQBroker
import asyncio
from time import sleep
from listener.core.di_container import DIContainer
from listener.core.logger import logger

async def main():
    logger.info("----------------------------")
    logger.info("🚀 Starting the listener")
    logger.info("----------------------------")
    container = DIContainer()
    await container.app().start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main()) 
