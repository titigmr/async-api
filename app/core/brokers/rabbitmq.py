from kombu import Connection, Producer, Queue

from app.core.config import settings
from app.schema import QueueTask
from app.schema.broker import Broker


class RabbitMQBroker(Broker):
    def __init__(self):
        self.services = settings.SERVICE_LIST
        self.queues = {
            service: Queue(name=f"task_{service}", routing_key=service)
            for service in self.services
        }
        self.connection = None
        self.producer = None

    def setup(self):
        """Initialize the connection and producer."""
        self.connection = Connection(settings.BROKER_URL)
        self.producer = Producer(self.connection)

    def ping(self):
        """Teste la connexion réelle au broker RabbitMQ."""
        if not self.connection:
            self.setup()
        self.connection.connect()
        self.connection.release()

    def add_task(self, task: QueueTask):
        """Add a task to the specified service queue."""
        if not self.producer:
            self.setup()
        queue = task.service
        if queue not in self.queues:
            raise ValueError(f"Service {queue} is not registered in the broker.")
        self.producer.publish(
            task,
            exchange=queue.exchange,
            routing_key=queue.routing_key,
            serializer="json",
            declare=[queue],
        )
