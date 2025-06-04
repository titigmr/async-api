from app.core.brokers.rabbitmq import RabbitMQBroker
from app.schema.queue import QueueTask

_broker_instance: RabbitMQBroker | None = None


def get_broker() -> RabbitMQBroker:
    """Retourne toujours la même instance de broker (singleton simple)."""
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = RabbitMQBroker()
        _broker_instance.setup()
    return _broker_instance


def send_task_to_queue(task_data: QueueTask, service: str) -> None:
    broker: RabbitMQBroker = get_broker()
    broker.add_task(task=task_data, service=service)
