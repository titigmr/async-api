
import asyncio
from contextvars import Context
import json
import signal
from socket import gethostname
from typing import Any, Awaitable, Callable
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
import logging

logger = logging.getLogger(__name__)

#--------------------------------------
# User Interface
#--------------------------------------
class IncomingMessage:
    def __init__(self, task_id: str, body: Any  ):
        self.task_id = task_id
        self.body = body

class TaskInterface:
    async def execute(self, _incoming_message: IncomingMessage, progress: Callable[[float], Awaitable]) -> Any:
        pass

#--------------------------------------
# Typed exceptions
#--------------------------------------
class SendException(Exception):
    pass

class IncomingMessageException(Exception):
    pass

class TaskException(Exception):
    pass

#--------------------------------------
# Runner component
#--------------------------------------
class AsyncWorkerRunner:

    def __init__(self, 
                 amqp_url: str, 
                 amqp_in_queue: str,
                 amqp_out_queue: str,
                 task_provider: Callable[[], TaskInterface ],
                 one_shot: bool = True,
                 nbr_async_task: int = 1,
                 ) -> None:
        self.amqp_url = amqp_url
        self.amqp_in_queue = amqp_in_queue
        self.amqp_out_queue = amqp_out_queue
        self.one_shot = one_shot
        self.nbr_async_task = nbr_async_task
        self.consumer_task: list[asyncio.Task] = []
        self.stop_event = asyncio.Event()
        self.task_provider = task_provider
        
    async def start(self) -> None:
        connection = await self.wait_for_connection()
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=self.nbr_async_task)
        queue = await channel.declare_queue(self.amqp_in_queue, durable=True)
        await queue.consume(self.message_handler)
        logger.info("🤗 Done.")

        # Setup signal handler
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.stop)
        loop.add_signal_handler(signal.SIGTERM, self.stop)

        # Wait for a stop signal
        await self.stop_event.wait()
        logger.info("💥 Stop signal received, closing connection.")
        for task in self.consumer_task:
            task.cancel()
            await task
        await connection.close()

    def task_done_callback(self, task):
        self.consumer_task.remove(task)

    async def message_handler(self,message: AbstractIncomingMessage):
        # Non blocking message processing (another task is created)
        task = asyncio.create_task(
            self.process_message(message),
            context=Context(),
        )
        nbr_consumers = len(self.consumer_task)
        self.consumer_task.append(task)
        task.add_done_callback(self.task_done_callback)
        logger.info(f"consumer_task len: {nbr_consumers}")

    def parse_incomming_message(self,message: str) -> IncomingMessage:
        try:
            dict_body = json.loads(message)
        except Exception as e:
            raise IncomingMessageException(f"Invalid json format '{message}'") 
        if not "task_id" in dict_body:
            raise IncomingMessageException(f"No task id in message '{message}'")
        if (not "data" in dict_body) or (not isinstance(dict_body["data"], dict)):
            raise IncomingMessageException(f"No valid data field in '{message}'")
        if not "body" in dict_body["data"]:
            raise IncomingMessageException(f"No data.body field in '{message}'")
        return IncomingMessage(task_id=dict_body["task_id"],body=dict_body["data"]["body"])

    async def process_message(self, message: AbstractIncomingMessage):
        task_id = None
        try:            
            str_body = message.body.decode()
            incoming_message = self.parse_incomming_message(str_body)
            task_id = incoming_message.task_id

            await self.send_start_message(task_id)
            result = None
            try:
                task = self.task_provider()
                async def progress_callback(progress: float):
                    try:
                        await self.send_progress_message(task_id=task_id, progress=progress)
                    except SendException as e :
                        logger.info("Impossible d'envoyer le progress... {e}")
                    
                result = await task.execute(incoming_message, progress_callback)
            except Exception as e:
                raise TaskException(e)
            
            await self.send_sucess_message(task_id, result)
            await message.ack()
        except IncomingMessageException as e:
            # Impossible de lire le message d'entrée... on est obligé d'ack
            logger.info(f"Unable to read incoming message: {e}")
            await message.ack()
        except SendException as e:
            # Impossible d'envoyer les messages de réponse... on nack implicite
            logger.info(f"Unable to send message: {e}")
        except asyncio.CancelledError as e:
            # Sigterm ou SigInt en plein traitement... on nack implicite
            logger.info(f"Sigterm or SigInt, auto nack message")
        except TaskException as e:
            logger.info(f"Fonctional error: {e}")
            try:
                await self.send_failure_message(task_id, str(e)) # type: ignore
                await message.ack()
            except SendException as e:
                # Impossible d'envoyer les messages de réponse... on nack implicite
                logger.info(f"Unable to send message...")
        if self.one_shot:
            self.stop()
    
    async def send_start_message(self, task_id: str) -> None:
        try:
            message = {
                "task_id" : task_id,
                "data" : {
                    "message_type" : "started",
                    "hostname" : gethostname()
                }
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded) 
        except Exception as e:
            raise SendException(e)
    
    async def send_sucess_message(self, task_id: str, result: Any) -> None:
        try:
            message = {
                "task_id" : task_id,
                "data" : {
                    "message_type" : "success",
                    "response" : result,
                }
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded) 
        except Exception as e:
            raise SendException(e)

    async def send_progress_message(self, task_id: str, progress: float) -> None:
        try:
            message = {
                "task_id" : task_id,
                "data" : {
                    "message_type" : "progress",
                    "progress" : progress,
                }
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded) 
        except Exception as e:
            raise SendException(e)
        
    async def send_failure_message(self, task_id: str, error_message: str) -> None:
        try:
            message = {
                "task_id" : task_id,
                "data" : {
                    "message_type" : "failure",
                    "error_message" : error_message,
                }
            }
            json_encoded = json.dumps(message).encode()
            await self.send_message(json_encoded) 
        except Exception as e:
            raise SendException(e)
        
    async def send_message(self, message: bytes):
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
                logger.info("Connecting to rabbitmq...")
                connection = await aio_pika.connect_robust(self.amqp_url)
                logger.info("Successfully connected.")
                return connection  # type: ignore
            except Exception as e:
                logger.info(f"Connection failure : {e}. Retry in 5s...")
                await asyncio.sleep(5)

#-------------------------
# Usage
#-------------------------
class MyTask(TaskInterface):
    async def execute(self, incoming_message, progress) -> Any:
        task_id = incoming_message.task_id
        body: dict[Any,Any] = incoming_message.body

        if body["must_succeed"] == True:
            time = body["sleep"]
            logger.info(f"Traitement en cours... ({time}s)")
            await asyncio.sleep(time/3)
            await progress(30.0)
            await asyncio.sleep(time/3)
            await progress(60.0)
            await asyncio.sleep(time/3)
        else:
            raise Exception("Argh") 
        return { "hello": "world" }

async def main() -> None:
    logger.info("Launch")
    runner = AsyncWorkerRunner(
        # Rabbit mq connection
        "amqp://kalo:kalo@127.0.0.1:5672",
        # In out queues
        "in_queue_python","out_queue_python",
        lambda:  MyTask(),
        True, 1)
    await runner.start()
    logger.info("Stopped.")

if __name__ == "__main__":
    logging.basicConfig(level= logging.INFO)
    asyncio.run(main())



# TODO: Oneshot -> nbr task == 1
# Logger 

