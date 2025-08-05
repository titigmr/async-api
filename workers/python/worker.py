import asyncio
import json
import logging
import signal
from collections.abc import Awaitable, Callable
from contextvars import Context
from dataclasses import dataclass
from socket import gethostname
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

logger = logging.getLogger(__name__)


@dataclass
class IncomingMessage:
    task_id: str
    body: dict


class AsyncTaskInterface:
    async def execute(self, _incoming_message: IncomingMessage, progress: Callable[[float], Awaitable]) -> Any:  # noqa: ANN401
        pass


class SyncTaskInterface:
    def execute(self, _incoming_message: IncomingMessage, progress: Callable[[float], None]) -> Any:  # noqa: ANN401
        pass


type TaskInterface = AsyncTaskInterface | SyncTaskInterface


class OnShot:
    pass


@dataclass
class Infinite:
    concurrency: int = 1


type WorkerMode = OnShot | Infinite


# --------------------------------------
# Typed exceptions
# --------------------------------------


class SendException(Exception):
    pass


class IncomingMessageException(Exception):
    pass


class TaskException(Exception):
    pass


@dataclass
class HealthCheckConfig:
    host: str
    port: int


class HealthCheckServer:
    def __init__(self, config: HealthCheckConfig) -> None:
        self.host: str = config.host
        self.port: int = config.port

    async def start(self) -> None:
        server: asyncio.Server = await asyncio.start_server(
            client_connected_cb=self.handler_health_check,
            host=self.host,
            port=self.port,
        )
        await server.start_serving()

    @staticmethod
    async def handler_health_check(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            await reader.readuntil(b"\r\n\r\n")
        except asyncio.IncompleteReadError:
            writer.close()
            await writer.wait_closed()
            return

        body = '{"status": "ok"}'
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )

        writer.write(response.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()


class AsyncWorkerRunner:
    def __init__(
        self,
        amqp_url: str,
        amqp_in_queue: str,
        amqp_out_queue: str,
        task_provider: Callable[[], TaskInterface],
        worker_mode: WorkerMode,
        *,
        health_check_config: HealthCheckConfig | None = None,
    ) -> None:
        self.amqp_url = amqp_url
        self.amqp_in_queue = amqp_in_queue
        self.amqp_out_queue = amqp_out_queue

        if isinstance(worker_mode, OnShot):
            self.one_shot = True
            self.nbr_async_task = 1
        if isinstance(worker_mode, Infinite):
            self.one_shot = False
            self.nbr_async_task = worker_mode.concurrency

        self.consumer_task: list[asyncio.Task] = []
        self.stop_event = asyncio.Event()
        self.task_provider = task_provider
        self.health_check_config: HealthCheckConfig | None = health_check_config

    async def start(self) -> None:
        logger.info("🛜 Connecting to rabbitmq...")
        connection = await self.wait_for_connection()
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=self.nbr_async_task)
        queue = await channel.declare_queue(self.amqp_in_queue, durable=True)
        logger.info("🤗 Successfully connected..")

        await queue.consume(self.message_handler)

        # Setup signal handler
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.stop)
        loop.add_signal_handler(signal.SIGTERM, self.stop)

        # HealthCheck
        if self.health_check_config is not None:
            server = HealthCheckServer(self.health_check_config)
            await server.start()

        # Wait for a stop signal
        await self.stop_event.wait()
        logger.info("💥 Stop signal received, closing connection.")
        for task in self.consumer_task:
            task.cancel()
            await task
        await connection.close()

    def task_done_callback(self, task: asyncio.Task) -> None:
        self.consumer_task.remove(task)

    async def message_handler(self, message: AbstractIncomingMessage) -> None:
        # Non blocking message processing (another task is created)
        task = asyncio.create_task(
            self.process_message(message),
            context=Context(),
        )
        # nbr_consumers = len(self.consumer_task)
        self.consumer_task.append(task)
        task.add_done_callback(self.task_done_callback)

    @staticmethod
    def remove_new_line(message: str) -> str:
        return message.replace("\r", "").replace("\n", "")

    def parse_incomming_message(self, message: str) -> IncomingMessage:
        try:
            dict_body = json.loads(message)
        except Exception as e:
            raise IncomingMessageException(f"Invalid json format '{self.remove_new_line(message)}'") from e
        if "task_id" not in dict_body:
            raise IncomingMessageException(f"No task id in message '{self.remove_new_line(message)}'")
        if ("data" not in dict_body) or (not isinstance(dict_body["data"], dict)):
            raise IncomingMessageException(f"No valid data field in '{self.remove_new_line(message)}'")
        if "body" not in dict_body["data"]:
            raise IncomingMessageException(f"No data.body field in '{self.remove_new_line(message)}'")
        return IncomingMessage(task_id=dict_body["task_id"], body=dict_body["data"]["body"])

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        task_id = None
        try:
            str_body = message.body.decode()
            incoming_message = self.parse_incomming_message(str_body)
            task_id = incoming_message.task_id

            await self.send_start_message(task_id)
            result = await self.launch_task(task_id=task_id, incoming_message=incoming_message)

            await self.send_success_message(task_id, result)
            await message.ack()
        except IncomingMessageException as e:
            # Impossible de lire le message d'entrée... on est obligé d'ack
            logger.info(f"Unable to read incoming message: {e}")
            await message.ack()
        except SendException as e:
            # Impossible d'envoyer les messages de réponse... on nack implicite
            logger.info(f"Unable to send message: {e}")
        except asyncio.CancelledError:
            # Sigterm ou SigInt en plein traitement... on nack implicite
            logger.info("Sigterm or SigInt, auto nack message")
        except TaskException as e:
            logger.info(f"Fonctional error: {e}")
            try:
                await self.send_failure_message(task_id, str(e))  # type: ignore
                await message.ack()
            except SendException as e:
                # Impossible d'envoyer les messages de réponse... on nack implicite
                logger.info("Unable to send message...")
        if self.one_shot:
            self.stop()

    async def launch_task(self, task_id: str, incoming_message: IncomingMessage) -> Any:  # noqa: ANN401
        result = None
        try:
            # Progress callback function async
            async def progress_callback_async(progress: float) -> None:
                try:
                    await self.send_progress_message(task_id=task_id, progress=progress)
                except SendException:
                    logger.info("Unable to send  progress... {e}")

            # Progress callback function sync

            def progress_callback_sync(progress: float) -> None:
                try:
                    asyncio.run(self.send_progress_message(task_id=task_id, progress=progress))
                except SendException:
                    logger.info("Unable to send progress... {e}")

            task = self.task_provider()
            if isinstance(task, AsyncTaskInterface):
                logger.info("Running async task...")
                result = await task.execute(incoming_message, progress_callback_async)
            else:
                logger.info("Running sync task...")
                result = await asyncio.to_thread(lambda: task.execute(incoming_message, progress_callback_sync))
            return result
        except Exception as e:
            raise TaskException(e) from e

    async def send_start_message(self, task_id: str) -> None:
        try:
            message = {
                "task_id": task_id,
                "data": {
                    "message_type": "started",
                    "hostname": gethostname(),
                },
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded)
        except Exception as e:
            raise SendException(e) from e

    async def send_success_message(self, task_id: str, result: Any) -> None:  # noqa: ANN401
        try:
            message = {
                "task_id": task_id,
                "data": {
                    "message_type": "success",
                    "response": result,
                },
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded)
        except Exception as e:
            raise SendException(e) from e

    async def send_progress_message(self, task_id: str, progress: float) -> None:
        try:
            message = {
                "task_id": task_id,
                "data": {
                    "message_type": "progress",
                    "progress": progress,
                },
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded)
        except Exception as e:
            raise SendException(e) from e

    async def send_failure_message(self, task_id: str, error_message: str) -> None:
        try:
            message = {
                "task_id": task_id,
                "data": {
                    "message_type": "failure",
                    "error_message": error_message,
                },
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded)
        except Exception as e:
            raise SendException(e) from e

    async def send_message(self, message: bytes) -> None:
        connection = await self.wait_for_connection()
        channel = await connection.channel()
        await channel.declare_queue(self.amqp_out_queue, durable=True)
        pika_message = aio_pika.Message(body=message)
        await channel.default_exchange.publish(pika_message, routing_key=self.amqp_out_queue)
        logger.info(f"Message {message} send on '{self.amqp_out_queue}'.")
        await channel.close()
        await connection.close()

    def stop(self) -> None:
        self.stop_event.set()

    async def wait_for_connection(self) -> aio_pika.RobustConnection:
        while True:
            try:
                connection: AbstractRobustConnection = await aio_pika.connect_robust(url=self.amqp_url)
                return connection  # type: ignore
            except Exception as e:
                logger.info(f"Connection failure : {e}. Retry in 5s...")
                await asyncio.sleep(5)
