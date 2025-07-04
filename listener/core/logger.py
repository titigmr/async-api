import asyncio
import logging
import sys


class AsyncTaskFormatter(logging.Formatter):
    def format(self, record):
        try:
            current_task = asyncio.current_task()
            record.task_name = current_task.get_name() if current_task else "none"
        except Exception:
            record.task_name = "none"
        return super().format(record)


def get_logger(name: str = "listener") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = AsyncTaskFormatter(
            "%(asctime)s | %(levelname)s | %(task_name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel("DEBUG")
    return logger


logger: logging.Logger = get_logger()
