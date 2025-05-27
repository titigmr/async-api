from kombu import Connection, Exchange, Producer, Queue

from app.core.config import settings
from app.schema.broker import Broker


class RabbitMQBroker(Broker):
    def __init__(self):
        self.exchange = Exchange("tasks", type="direct")
        self.queue = Queue(
            name="task_queue", exchange=self.exchange, routing_key="task"
        )
        self.connection = None
        self.producer = None

    def setup(self):
        self.connection = Connection(settings.BROKER_URL)
        self.producer = Producer(self.connection)

    def add_task(self, task):
        if not self.producer:
            self.setup()
        print(task)
        self.producer.publish(
            task, exchange=self.exchange, routing_key="task", serializer="json"
        )
