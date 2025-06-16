import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from api.schemas.service import ServiceInfo


def load_json_schema(path: str) -> dict:
    print(f"Loading JSON schema from {Path(path).resolve()}")
    with open(file=Path(path), mode="r") as f:
        return json.load(fp=f)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow",env_file=".env", yaml_file=".env.yaml")
    PROJECT_NAME: str = "Task API"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/tasks"
    BROKER_URL: str = "amqp://guest:guest@rabbitmq//"
    PROJECT_DESCRIPTION: str = "API for managing tasks"
    BROKER_TYPE: str = "rabbitmq"
    SERVICES_CONFIG_FILE: str = "./config/services.yaml"

settings = Settings()

__all__ = ["settings"]
