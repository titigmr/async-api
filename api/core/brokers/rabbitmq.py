import json
from typing import Any

from kombu import Connection, Producer, Queue
from kombu.exceptions import KombuError

from api.core.brokers import AbstractBroker
from api.core.config import settings
from api.core.utils import logger
from api.schemas import QueueTask
from api.services.service_service import ServiceService


class RabbitMQBroker(AbstractBroker):
    def __init__(self, service: ServiceService) -> None:
        self.services: list[str] = [s for s in service.list_services_names()]
        self.queues: dict[str, Queue] = {
            service: Queue(name=service, routing_key=service)
            for service in self.services
        }
        self.connection: Connection | None = None
        self.producer: Producer | None = None

    def setup(self) -> None:
        """Initialise la connexion, le channel et déclare toutes les queues."""
        if self.connection and self.connection.connected:
            return
        self.connection = Connection(hostname=settings.BROKER_URL)
        self.connection.connect()
        logger.info(msg=f"Connected to RabbitMQ at {settings.BROKER_URL}")
        channel: Any = self.connection.channel()
        self.producer = Producer(channel=channel)

        for queue in self.queues.values():
            bound_queue: Queue = queue(channel=channel)
            bound_queue.declare()
        logger.info(msg=f"Registered queues: {list(self.queues.keys())}")

    def close(self) -> None:
        """Ferme proprement la connexion et le channel."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Connection to RabbitMQ closed.")
            except KombuError as e:
                logger.error(f"Error while closing RabbitMQ connection: {e}")

    def ping(self) -> None:
        """Teste la connexion réelle au broker RabbitMQ."""
        if not self.connection:
            self.setup()
        if self.connection:
            self.connection.ensure_connection()
            self.connection.release()

    def add_task(self, task: QueueTask, service: str) -> None:
        self.ensure_connection()
        queue: str = service
        if queue not in self.queues:
            raise ValueError(f"Service {queue} is not registered in the broker.")
        if self.producer is None:
            raise ValueError("Producer is not initialized. Call setup() first.")
        bound_queue: Queue = self.queues[queue](self.producer.channel)
        bound_queue.declare()
        self.producer.publish(
            body=json.loads(s=task.model_dump_json()),
            serializer="json",
            routing_key=queue,
        )

    def ensure_connection(self) -> None:
        if not self.connection or not self.connection.connected:
            logger.warning(msg="RabbitMQ connection lost, reconnecting...")
            self.setup()
