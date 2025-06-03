import logging
from pathlib import Path
from fastapi.responses import JSONResponse
from app.schema import TaskErrorResponse
from app.schema.enum import ERROR_MAP

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


def generate_error_response(error_code: int):
    """
    Génère une réponse JSON pour les erreurs avec le format spécifié.

    Args:
        error_code (int): Code d'erreur spécifique.

    Returns:
        JSONResponse: Réponse JSON contenant le code de statut et le message d'erreur.
    """
    if error_code not in ERROR_MAP:
        raise ValueError(f"Invalid error code: {error_code}")

    status_code, description = ERROR_MAP[error_code]
    return JSONResponse(
        status_code=status_code,
        content=TaskErrorResponse(
            status="error",
            error=TaskErrorResponse.Error(
                number=error_code,
                description=description,
            ),
        ).model_dump(),
    )


logger = get_logger()
