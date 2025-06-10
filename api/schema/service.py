from typing import Any

from pydantic import BaseModel, Field


class ServiceInfo(BaseModel):
    name: str = Field(default=..., description="Nom du service")
    json_schema: dict[str, Any] | None = Field(
        default=None, description="JsonSchema du service (optionnel)"
    )
