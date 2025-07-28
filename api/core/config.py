from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        yaml_file=".env.yaml",
    )
    PROJECT_NAME: str = "Task API"

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "tasks"
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_SCHEME: str = "postgresql+asyncpg"

    BROKER_HOST: str = "rabbitmq"
    BROKER_PORT: int = 5672
    BROKER_USERNAME: str = "guest"
    BROKER_PASSWORD: str = "guest"
    BROKER_VHOST: str = "/"
    BROKER_SCHEME: str = "amqp"

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/tasks"
    BROKER_URL: str = "amqp://guest:guest@rabbitmq//"

    PROJECT_DESCRIPTION: str = "API for managing tasks"
    SERVICES_CONFIG_FILE: str = "./config/services.yaml"
    CLIENTS_CONFIG_FILE: str = "./config/clients.yaml"
    API_SENDER_RETRY: int = 3  # 0, 1:1s, 2:4s, 3:9s, ...
    API_LOG_LEVEL: str = "INFO"
    LISTENER_LOG_LEVEL: str = "INFO"
    LISTENER_CONCURRENCY: int = 20
    LISTENER_NOTIFIER_RETRY: int = 3  # 0, 1:1s, 2:4s, 3:9s, ...

    @property
    def database_url_from_components(self) -> str:
        """Construct database URL from individual components using sqlalchemy.URL"""
        url_obj = URL.create(
            drivername=self.DB_SCHEME,
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )
        return str(url_obj)

    @property
    def broker_url_from_components(self) -> str:
        """Construct broker URL from individual components"""
        if self.BROKER_VHOST == "/":
            vhost = ""
        elif self.BROKER_VHOST.startswith("/"):
            vhost = self.BROKER_VHOST
        else:
            vhost = f"/{self.BROKER_VHOST}"
        return f"{self.BROKER_SCHEME}://{self.BROKER_USERNAME}:{self.BROKER_PASSWORD}@{self.BROKER_HOST}:{self.BROKER_PORT}{vhost}"


settings = Settings()

__all__ = ["settings"]
