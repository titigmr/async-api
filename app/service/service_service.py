from app.core.config import settings
from app.schema.errors import ServiceNotFound


def check_service_exists(service: str) -> None:
    """
    Vérifie que le service existe dans la liste autorisée.
    Lève ServiceNotFound si ce n'est pas le cas.
    """
    if service not in settings.SERVICE_LIST:
        raise ServiceNotFound(details=f"Service '{service}' inconnu.")
