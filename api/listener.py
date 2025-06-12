import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.core.brokers.base import Broker
from api.core.utils import logger
from api.services import get_broker, list_services_names


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(msg="[Consumer] Consumer started")
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    broker: Broker = get_broker()
    running = True

    async def consume_queue(service_name: str):
        while running:
            try:
                logger.info(
                    msg=f"[Consumer] Listening for tasks on queue: {service_name}"
                )
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(
                    msg=f"[Consumer] Erreur dans le consumer {service_name}: {e}"
                )
                await asyncio.sleep(2)

    # Lance un consumer par service
    tasks: list[asyncio.Task] = [
        loop.create_task(coro=consume_queue(service_name=service))
        for service in list_services_names()
    ]

    try:
        yield
    finally:
        logger.info(msg="[Consumer] Consumer stopped")
        running = False
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
