from pydantic import BaseModel


class HealthComponent(BaseModel):
    status: str
    details: str | None = None


class HealthResponse(BaseModel):
    status: str
    components: dict[str, HealthComponent]
