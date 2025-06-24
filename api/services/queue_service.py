import asyncio
import json
import aio_pika
from api.core.config import settings
from api.schemas import QueueTask
from api.core.utils import logger

class QueueSenderError(Exception):
    pass

class QueueSender:

    def __init__(self):
        self.broker_url = settings.BROKER_URL
        self.max_retries = settings.API_SENDER_RETRY
        pass

    async def ping(self):
        connection = await aio_pika.connect_robust(self.broker_url)
        if connection.is_closed:
            raise QueueSenderError("Not connected")
        await connection.close()
    
    async def send_task_to_queue(self, queue: str, task_data: QueueTask, service: str):
        await self.send_task_to_queue_retry(queue, task_data, service, 0)

    async def send_task_to_queue_retry(self, queue: str,  task_data: QueueTask, service: str, retry: int):
        try:
            connection = await aio_pika.connect_robust(self.broker_url)
            async with connection:
                channel = await connection.channel()
                await channel.declare_queue(queue, durable=True)
                pika_message = aio_pika.Message(body=json.dumps(task_data).encode())
                await channel.default_exchange.publish(pika_message, routing_key=queue)
                logger.debug(f"Task send successfully on queue '{queue}'.")

        except Exception as e:
            if retry < self.max_retries:
                wait_time = pow(retry + 1,2)
                logger.debug(f"Failure, about to retry n°{retry+1}/{self.max_retries} in {wait_time}s...")
                await asyncio.sleep(wait_time)
                await  self.send_task_to_queue_retry(queue, task_data, service, retry + 1)
                return
            logger.debug("No more retries")
            raise QueueSenderError(f"Error sending task: {task_data}",e)


# def get_broker() -> AbstractBroker:
#     """Retourne une instance unique du broker choisi selon la config."""
#     global _broker_instance
#     if _broker_instance is not None:
#         return _broker_instance

#     broker_type: str = settings.BROKER_TYPE.lower()
#     if broker_type == "rabbitmq":
#         # Manual depebdency injection, cause lifespan does not support DI
#         service_repo = ServicesConfigRepository()
#         service_service = ServiceService(service_repository=service_repo)
#         _broker_instance = RabbitMQBroker(service=service_service)
#     else:
#         raise ValueError(f"Broker type '{broker_type}' non supporté.")
#     _broker_instance.setup()
#     return _broker_instance


# def send_task_to_queue(task_data: QueueTask, service: str) -> None:
#     broker: AbstractBroker = get_broker()
#     broker.add_task(task=task_data, service=service)
