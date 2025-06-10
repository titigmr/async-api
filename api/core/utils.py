import logging
from pathlib import Path

import toml


def get_version() -> tuple[str, str]:
    pyproject_path: Path = (
        Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    )
    try:
        with open(file=pyproject_path, mode="r") as f:
            data: dict[str, str] = toml.loads(s=f.read())
            return data["project"]["version"], data["project"]["name"]  # type: ignore
    except Exception:
        return "0.0.0", ""


def get_logger(name: str = "uvicorn") -> logging.Logger:
    """
    Retourne un logger configuré identique à celui d'uvicorn.
    """
    return logging.getLogger(name=name)


logger: logging.Logger = get_logger()
