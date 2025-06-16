from typing import Any

from pydantic import BaseModel, Field


class ServiceInfo(BaseModel):
    name: str = Field(default=..., description="Nom du service")
    quotas: int | None = Field(default=None, description="Quota du service (optionnel)")
    in_queue : str | None = Field(default=None, description="Queue d'entrée du service")
    out_queue : str | None = Field(default=None, description="Queue de sortie du service")
    json_schema: dict[str, Any] | None = Field(
        default=None, description="JsonSchema du service (optionnel)"
    )
