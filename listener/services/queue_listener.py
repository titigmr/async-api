import asyncio
import signal
from contextvars import Context

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, AbstractRobustConnection

from api.repositories.services_config_repository import ServicesConfigRepository
from listener.core.logger import logger
from listener.services.health_check import HealthCheckServer
from listener.services.message_service import MessageService, MessageServiceError


class QueueListener:
    def __init__(
        self,
        message_service: MessageService,
        service_repository: ServicesConfigRepository,
        broker_kwargs: dict[str, str | int | None],
        health_check_server: HealthCheckServer | None = None,
        concurrency: int = 20,
    ) -> None:
        self.service_repository: ServicesConfigRepository = service_repository
        self.broker_kwargs: dict[str, str | int | None] = broker_kwargs
        self.message_service: MessageService = message_service
        self.health_check_server: HealthCheckServer | None = health_check_server
        self.concurrency: int = concurrency

        self.consumer_task: list[asyncio.Task] = []
        self.stop_event = asyncio.Event()

    async def process_message(
        self,
        message: AbstractIncomingMessage,
        service_name: str,
    ) -> None:
        async with message.process():
            try:  # auto-ack à la fin du bloc
                await self.message_service.process(
                    message=message.body.decode(),
                    service_name=service_name,
                )
            except MessageServiceError as e:
                logger.error(f"Error: {e}")

    def task_done_callback(self, task: asyncio.Task) -> None:
        self.consumer_task.remove(task)

    async def message_handler(self, message: AbstractIncomingMessage, service_name: str) -> None:
        # Non blocking message processing (another task is created)
        task = asyncio.create_task(
            self.process_message(message=message, service_name=service_name),
            context=Context(),
        )
        self.consumer_task.append(task)
        task.add_done_callback(self.task_done_callback)

    async def wait_for_connection(self) -> aio_pika.RobustConnection:
        while True:
            try:
                logger.info("Connecting to rabbitmq...")
                connection: AbstractRobustConnection = await aio_pika.connect_robust(**self.broker_kwargs)
                logger.info("Successfully connected.")
                return connection  # type: ignore
            except Exception as e:
                logger.error(f"Connection failure : {e}. Retry in 5s...")
                await asyncio.sleep(delay=5)

    async def start(self) -> None:
        logger.info(
            f"⏳ Connecting to the output queues (concurrency: {self.concurrency})...",
        )

        health_task = None
        if self.health_check_server:
            logger.info(
                f"Starting health check server on {self.health_check_server.host}:{self.health_check_server.port}",
            )
            health_task = asyncio.create_task(self.health_check_server.start())

        try:
            connection: aio_pika.RobustConnection = await self.wait_for_connection()

            channel: AbstractChannel = await connection.channel()
            await channel.set_qos(prefetch_count=self.concurrency)

            for service in self.service_repository.all_services().values():
                logger.info(
                    f"- Listen service '{service.name}' on response queue '{service.out_queue}'",
                )
                queue = await channel.declare_queue(name=service.out_queue, durable=True)
                await queue.consume(
                    callback=lambda msg, svc=service.name: self.message_handler(message=msg, service_name=svc),
                )
            logger.info("🤗 Done.")

            loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
            loop.add_signal_handler(sig=signal.SIGINT, callback=self.stop)
            loop.add_signal_handler(sig=signal.SIGTERM, callback=self.stop)

            # Wait for a stop signal
            await self.stop_event.wait()
            logger.info("💥 Stop signal received, closing connection.")
            for task in self.consumer_task:
                task.cancel()
                await task
            await connection.close()
        finally:
            if health_task:
                health_task.cancel()
                try:
                    await health_task
                except asyncio.CancelledError:
                    logger.info("Health check server stopped")

    def stop(self) -> None:
        self.stop_event.set()
