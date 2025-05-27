from app.core.brokers.rabbitmq import RabbitMQBroker
from app.core.config import settings


def get_broker():
    """Factory function to get the broker instance based on settings."""
    if settings.BROKER_TYPE == "rabbitmq":
        return RabbitMQBroker()
    else:
        raise ValueError(f"Unknown broker type: {settings.BROKER_TYPE}")


def send_task_to_queue(task_data: dict):
    broker = get_broker()
    broker.add_task(task_data)
