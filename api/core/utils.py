import asyncio
import logging
import sys
from logging import Logger
from pathlib import Path

import toml


def get_version() -> tuple[str, str]:
    pyproject_path: Path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    try:
        with open(file=pyproject_path) as f:
            data: dict[str, str] = toml.loads(s=f.read())
            return data["project"]["version"], data["project"]["name"]  # type: ignore
    except Exception:
        return "0.0.0", ""


class AsyncTaskFormatter(logging.Formatter):
    def format(self, record):
        current_task = asyncio.current_task()
        record.task_name = current_task.get_name() if current_task else "no-task"
        return super().format(record)


def setup_loggers() -> Logger:
    handler = logging.StreamHandler(sys.stdout)
    formatter = AsyncTaskFormatter(
        "%(asctime)s | %(levelname)s | %(task_name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger("uvicorn")
    logger_access = logging.getLogger("uvicorn.access")

    for log in [logger, logger_access]:
        log.handlers = []
        log.addHandler(handler)
    return logger


logger: logging.Logger = logging.getLogger("uvicorn")
