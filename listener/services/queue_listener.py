import asyncio
from contextvars import Context
from aio_pika.abc import AbstractIncomingMessage

import aio_pika

from api.repositories.services_config_repository import ServicesConfigRepository
from listener.core.logger import logger
from listener.services.message_service import MessageService, MessageServiceError

class QueueListener:

    def __init__(self, 
                 message_service: MessageService,
                 service_repository: ServicesConfigRepository, 
                 rabbitmq_url: str):
        self.service_repository = service_repository
        self.rabbit_url = rabbitmq_url
        self.message_service = message_service
        pass

    async def process_message(self,message: AbstractIncomingMessage,service_name: str):
        async with message.process(): 
            try: # auto-ack à la fin du bloc
                await self.message_service.process(message.body.decode(), service_name=service_name)
            except MessageServiceError as e:
                logger.error(f"Error: {e}")

    def message_handler(self,service_name: str):
        async def inner_message_handler(message: AbstractIncomingMessage):
            # Non blocking message processing (another task is created)
            asyncio.create_task(self.process_message(message=message,service_name=service_name),context=Context())
        return inner_message_handler

    async def start(self):

        logger.info("----------------------------")
        logger.info("⏳ Connecting to the output queues...")

        connection = await aio_pika.connect_robust(self.rabbit_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=20)

        for service in self.service_repository.all_services().values():
            logger.info(f"- Listen service '{service.name}' on response queue '{service.out_queue}'")
            queue = await channel.declare_queue(service.out_queue, durable=True)
            await queue.consume(self.message_handler(service.name))

        logger.info("🤗 Done.")

  


