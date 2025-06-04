from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    SERVICE_LIST: list[str] = ["transcription", "ocr", "capture_audio"]
    PROJECT_NAME: str = "Task API"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/tasks"
    BROKER_URL: str = "amqp://guest:guest@rabbitmq//"
    PROJECT_DESCRIPTION: str = "API for managing tasks"
    BROKER_TYPE: str = "rabbitmq"
    BROKER_URL: str = "amqp://guest:guest@localhost:5672//"


settings = Settings()


__all__ = ["settings"]
