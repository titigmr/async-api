from pydantic import BaseModel


class ReadyComponent(BaseModel):
    status: str
    details: str | None = None


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    components: dict[str, ReadyComponent]
