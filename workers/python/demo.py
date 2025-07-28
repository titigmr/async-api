import asyncio
import logging
import sys
from time import sleep
from typing import Any
from worker import AsyncTaskInterface, AsyncWorkerRunner, Infinite, OnShot, SyncTaskInterface
from loguru import logger

from worker import AsyncWorkerRunner, Infinite, TaskInterface


# --------------------------------
# L'implementation du worker est indépendante du système de logging
# Dans notre exemple, nous voulons utiliser loguru, il nous faut donc
# intercepter les logs du module logging standard et les rediriger vers loguru
# --------------------------------
class InterceptHandler(logging.Handler):
    """Handler pour intercepter les logs du module logging standard et les rediriger vers loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
logger.remove()
logger.add(sys.stdout, level="INFO")


# -------------------------
# Implémentation de la task
# "utilisateur" (Sync)
#-------------------------
class MySyncTask(SyncTaskInterface):
    def execute(self, incoming_message, progress) -> Any:
        task_id = incoming_message.task_id
        body: dict[Any, Any] = incoming_message.body
        logging.info("Task_id: {task_id}")
        if body["must_succeed"]:
            time = body["sleep"]
            logger.info(f"Traitement en cours... ({time}s)")
            sleep(time/2)
            progress(30.0)
            sleep(time/2)
            progress(30.0)
        else:
            # Exception "fonctionnelle", le message ne sera pas retraité, la tâche aura le status failure
            raise Exception("Argh")
        return {"hello": "world"}  # Réponse


#-------------------------
# Implémentation de la task
# "utilisateur" (Async)
#-------------------------
class MyAsyncTask(AsyncTaskInterface):
    async def execute(self, incoming_message, progress) -> Any:
        task_id = incoming_message.task_id
        body: dict[Any,Any] = incoming_message.body

        if body["must_succeed"] == True:
            time = body["sleep"]
            logger.info(f"Traitement en cours... ({time}s)")
            await asyncio.sleep(time/2)
            await progress(30.0)
            await asyncio.sleep(time/2)
            await progress(30.0)
        else:
            # Exception "fonctionnelle", le message ne sera pas retraité, la tâche aura le status failure
            raise Exception("Argh") 
        return { "hello": "world" } # Réponse


async def main() -> None:
    logger.info("Launch")
    runner = AsyncWorkerRunner(
        # Rabbit mq connection
        amqp_url="amqp://kalo:kalo@127.0.0.1:5672",
        # In out queues
        amqp_in_queue="in_queue_python",
        amqp_out_queue="out_queue_python",
        task_provider=lambda:  MyAsyncTask(), # or  lambda:  MySyncTask()
        worker_mode=Infinite(5), # or OnShot(), 
    )
    await runner.start()
    logger.info("Stopped.")

# Main
if __name__ == "__main__":
    asyncio.run(main())
