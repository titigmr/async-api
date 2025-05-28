import logging
from pathlib import Path

import toml


def get_version():
    pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    try:
        with open(pyproject_path, "r") as f:
            data = toml.loads(f.read())
            return data["project"]["version"], data["project"]["name"]
    except Exception:
        return "0.0.0", ""


def get_logger(name: str = "uvicorn.error") -> logging.Logger:
    """
    Retourne un logger configuré identique à celui d'uvicorn.
    """
    return logging.getLogger(name)


logger = get_logger()
