from api.core.config import settings
from api.schemas import ServiceInfo
from api.schemas.errors import ServiceNotFound


def check_service_exists(service: str) -> None:
    """
    Vérifie que le service existe dans la liste autorisée.
    Lève ServiceNotFound si ce n'est pas le cas.
    """
    if service not in [s.name for s in settings.SERVICES]:
        raise ServiceNotFound(details=f"Service '{service}' inconnu.")


def list_services_names() -> list[str]:
    """
    Retourne la liste des noms des services disponibles.
    """
    return [s.name for s in settings.SERVICES]


def list_services_config() -> list[ServiceInfo]:
    """
    Retourne la configuration complète (nom + json_schema) de chaque service.
    """
    return [
        ServiceInfo(name=s.name, json_schema=s.json_schema) for s in settings.SERVICES
    ]
