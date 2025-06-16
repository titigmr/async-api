from api.core.brokers import AbstractBroker, RabbitMQBroker
from api.core.config import settings
from api.schemas import QueueTask
from api.services.service_service import ServiceService
from api.repositories.services_config_repository import ServicesConfigRepository

_broker_instance = None


def get_broker() -> AbstractBroker:
    """Retourne une instance unique du broker choisi selon la config."""
    global _broker_instance
    if _broker_instance is not None:
        return _broker_instance

    broker_type: str = settings.BROKER_TYPE.lower()
    if broker_type == "rabbitmq":
        # Manual depebdency injection, cause lifespan does not support DI
        service_repo = ServicesConfigRepository()
        service_service = ServiceService(service_repository=service_repo)
        _broker_instance = RabbitMQBroker(service=service_service)
    else:
        raise ValueError(f"Broker type '{broker_type}' non supporté.")
    _broker_instance.setup()
    return _broker_instance


def send_task_to_queue(task_data: QueueTask, service: str) -> None:
    broker: AbstractBroker = get_broker()
    broker.add_task(task=task_data, service=service)
