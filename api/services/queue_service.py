from api.core.brokers import AbstractBroker, RabbitMQBroker
from api.core.config import settings
from api.schemas import QueueTask

_broker_instance = None


def get_broker() -> AbstractBroker:
    """Retourne une instance unique du broker choisi selon la config."""
    global _broker_instance
    if _broker_instance is not None:
        return _broker_instance

    broker_type: str = settings.BROKER_TYPE.lower()
    if broker_type == "rabbitmq":
        _broker_instance = RabbitMQBroker()
    else:
        raise ValueError(f"Broker type '{broker_type}' non supporté.")
    _broker_instance.setup()
    return _broker_instance


def send_task_to_queue(task_data: QueueTask, service: str) -> None:
    broker: AbstractBroker = get_broker()
    broker.add_task(task=task_data, service=service)
