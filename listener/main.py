
# import asyncio
# from time import sleep
# from typing import Annotated

# from fastapi import Depends
# from fastapi_injectable import injectable

# from api.core.brokers.rabbitmq import RabbitMQBroker
import asyncio
from time import sleep
from listener.core.di_container import DIContainer

async def main():
    container = DIContainer()
    print("started.")
    await container.app().start()
    print("started.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main()) 
