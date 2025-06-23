from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow",env_file=".env", yaml_file=".env.yaml")
    PROJECT_NAME: str = "Task API"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/tasks"
    BROKER_URL: str = "amqp://guest:guest@rabbitmq//"
    PROJECT_DESCRIPTION: str = "API for managing tasks"
    BROKER_TYPE: str = "rabbitmq"
    SERVICES_CONFIG_FILE: str = "./config/services.yaml"
    CLIENTS_CONFIG_FILE: str = "./config/clients.yaml"
    LOG_LEVEL: str = "INFO"

settings = Settings()

__all__ = ["settings"]
