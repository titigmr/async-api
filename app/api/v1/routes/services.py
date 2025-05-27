from core.config import settings
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/",
    summary="Lister les services disponibles",
    description="Retourne la liste des services disponibles pour la création de tâches.",
    response_model=list[str],
)
async def list_services():
    """
    Retourne la liste des services disponibles.
    """
    return settings.SERVICE_LIST
