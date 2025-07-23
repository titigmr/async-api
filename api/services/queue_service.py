import asyncio
import json

import aio_pika

from api.core.config import settings
from api.core.logger import logger
from api.schemas import QueueTask


class QueueSenderError(Exception):
    pass


class QueueSender:
    def __init__(self) -> None:
        self.broker_url = settings.BROKER_URL
        self.max_retries = settings.API_SENDER_RETRY

    async def ping(self) -> None:
        connection = await aio_pika.connect_robust(self.broker_url)
        if connection.is_closed:
            msg = "Not connected"
            raise QueueSenderError(msg)
        await connection.close()

    async def send_task_to_queue(self, queue: str, task_data: QueueTask, service: str):
        await self.send_task_to_queue_retry(queue, task_data, service, 0)

    async def send_task_to_queue_retry(
        self,
        queue: str,
        task_data: QueueTask,
        service: str,
        retry: int,
    ):
        try:
            connection = await aio_pika.connect_robust(self.broker_url)
            async with connection:
                channel = await connection.channel()
                await channel.declare_queue(queue, durable=True)
                pika_message = aio_pika.Message(
                    body=json.dumps(task_data.model_dump()).encode(),
                )
                await channel.default_exchange.publish(pika_message, routing_key=queue)
                logger.debug(f"Task send successfully on queue '{queue}'.")

        except Exception as e:
            if retry < self.max_retries:
                wait_time = pow(retry + 1, 2)
                logger.debug(
                    f"Failure, about to retry n°{retry + 1}/{self.max_retries} in {wait_time}s...",
                )
                await asyncio.sleep(wait_time)
                await self.send_task_to_queue_retry(
                    queue,
                    task_data,
                    service,
                    retry + 1,
                )
                return
            logger.debug("No more retries")
            raise QueueSenderError(f"Error sending task: {task_data}", e) from e
