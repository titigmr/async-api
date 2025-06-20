import asyncio
from contextvars import Context
from aio_pika.abc import AbstractIncomingMessage
from functools import partial

import aio_pika

from api.repositories.services_config_repository import ServicesConfigRepository
from listener.services.message_service import MessageService, MessageServiceError

async def message_handler(message: AbstractIncomingMessage):
    pass
        # Lance le traitement sans attendre (non bloquant)
        #asyncio.create_task(process_message(message)) 

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
                print(f"Error: {e}")

    def message_handler(self,service_name: str):
        async def inner_message_handler(message: AbstractIncomingMessage):
            # Non blocking message processing (another task is created)
            asyncio.create_task(self.process_message(message=message,service_name=service_name),context=Context())
        return inner_message_handler

    async def start(self):
        connection = await aio_pika.connect_robust(self.rabbit_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=20)

        for service in self.service_repository.all_services().values():
            print(f"Liste for '{service.name}' response on queue '{service.out_queue}'")
            queue = await channel.declare_queue(service.out_queue, durable=True)
            await queue.consume(self.message_handler(service.name))

  


