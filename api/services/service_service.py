from typing import Annotated

from fastapi import Depends
from api.repositories.services_config_repository import ServicesConfigRepository
from api.schemas import ServiceInfo
from api.schemas.errors import ServiceNotFound


class ServiceService:
    def __init__(self, service_repository: Annotated[ServicesConfigRepository, Depends(ServicesConfigRepository)]) -> None:
        self.service_repository: ServicesConfigRepository = service_repository

    def check_service_exists(self,service: str) -> None:
        """
        Vérifie que le service existe dans la liste autorisée.
        Lève ServiceNotFound si ce n'est pas le cas.
        """
        if self.service_repository.all_services().get(service) is None:
            raise ServiceNotFound(details=f"Service '{service}' inconnu.")

    def list_services_names(self) -> list[str]:
        """
        Retourne la liste des noms des services disponibles.
        """
        return list(self.service_repository.all_services().keys())

    def list_all(self) -> list[ServiceInfo]:
        """
        Retourne la liste des noms des services disponibles.
        """
        services = list(self.service_repository.all_services().values())
        print(f"Services loaded: {services}")
        return list(map(lambda c: ServiceInfo(
            name=c.name, quotas=c.quotas, json_schema=c.json_schema, in_queue=c.in_queue, out_queue=c.out_queue
            ), services))

    def get_service(self, service: str) -> ServiceInfo | None:
        """
        Retourne les informations d'un service spécifique.
        Lève ServiceNotFound si le service n'existe pas.
        """
        return self.service_repository.all_services()[service]