from typing import List

from fastapi import APIRouter

from api.schemas import ServiceInfo
from api.services import list_services_config

router = APIRouter()


@router.get(
    path="/services",
    summary="Lister les services disponibles",
    description="Retourne la liste des services disponibles pour la création de tâches.",
    response_model=List[ServiceInfo],
)
def get_services() -> list[ServiceInfo]:
    """
    Retourne la liste des services disponibles avec leur json_schema.
    """
    return list_services_config()
