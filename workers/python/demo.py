import asyncio
import logging
import sys
from typing import Any
from worker import AsyncWorkerRunner, Infinite, OnShot, TaskInterface
from loguru import logger

#--------------------------------
# L'implementation du worker est indépendante du système de logging
# Dans notre exemple, nous voulons utiliser loguru, il nous faut donc
# intercepter les logs du module logging standard et les rediriger vers loguru
#--------------------------------
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
logger.add(sys.stdout,level="INFO")


#-------------------------
# Implémentation de la task
# "utilisateur"
#-------------------------
class MyTask(TaskInterface):
    async def execute(self, incoming_message, progress) -> Any:
        task_id = incoming_message.task_id
        body: dict[Any,Any] = incoming_message.body

        if body["must_succeed"] == True:
            time = body["sleep"]
            logger.info(f"Traitement en cours... ({time}s)")
            await asyncio.sleep(time/3) # Facultatif
            await progress(30.0)
            await asyncio.sleep(time/3) # Facultatif
            await progress(60.0)
            await asyncio.sleep(time/3) # Facultatif
        else:
            # Exception "fonctionnelle", le message ne sera pas retraité, la tâche aura le status failure
            raise Exception("Argh") 
        return { "hello": "world" } # Réponse

async def main() -> None:
    logger.info("Launch")
    runner = AsyncWorkerRunner(
        # Rabbit mq connection
        "amqp://kalo:kalo@127.0.0.1:5672",
        # In out queues
        "in_queue_python","out_queue_python",
        lambda:  MyTask(),
        Infinite(1), # or OnShot(), 
    )
    await runner.start()
    logger.info("Stopped.")

if __name__ == "__main__":
    asyncio.run(main())


