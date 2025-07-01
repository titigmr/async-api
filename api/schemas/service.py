from typing import Any

from pydantic import BaseModel, Field

from api.repositories.services_config_repository import ServicesConfig


class ServiceInfo(BaseModel):
    name: str = Field(default=..., description="Nom du service")
    quotas: int | None = Field(default=None, description="Quota du service (optionnel)")
    in_queue: str = Field(default=..., description="Queue d'entrée du service")
    out_queue: str = Field(default=..., description="Queue de sortie du service")
    json_schema: dict[str, Any] | None = Field(default=None, description="JsonSchema du service (optionnel)")


def service_info_from_service_config(service_config: ServicesConfig) -> ServiceInfo:
    """Convertit un objet ServicesConfig en ServiceInfo."""
    return ServiceInfo(
        name=service_config.name,
        quotas=service_config.quotas,
        json_schema=service_config.json_schema,
        in_queue=service_config.in_queue,
        out_queue=service_config.out_queue,
    )
