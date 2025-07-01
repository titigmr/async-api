from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_file=".env", yaml_file=".env.yaml")
    PROJECT_NAME: str = "Task API"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/tasks"
    BROKER_URL: str = "amqp://guest:guest@rabbitmq//"
    PROJECT_DESCRIPTION: str = "API for managing tasks"
    SERVICES_CONFIG_FILE: str = "./config/services.yaml"
    CLIENTS_CONFIG_FILE: str = "./config/clients.yaml"
    API_SENDER_RETRY: int = 3  # 0, 1:1s, 2:4s, 3:9s, ...

    LISTENER_LOG_LEVEL: str = "INFO"
    LISTENER_CONCURRENCY: int = 20
    LISTENER_NOTIFIER_RETRY: int = 3  # 0, 1:1s, 2:4s, 3:9s, ...


settings = Settings()

__all__ = ["settings"]
