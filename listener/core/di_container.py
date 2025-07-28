from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import Settings
from api.repositories.services_config_repository import ServicesConfigRepository
from api.repositories.task_repository import TaskRepository
from listener.core.logger import configure_logger, logger
from listener.core.task_aware_async_session import TaskAwareAsyncSession
from listener.services.health_check import HealthCheckServer
from listener.services.message_service import MessageService
from listener.services.notifier_service import NotificationService
from listener.services.notifiers.amqp_notifier import AmqpNotifier
from listener.services.notifiers.http_notifier import HttpNotifier
from listener.services.queue_listener import QueueListener


class DIContainer:
    def __init__(self, settings: Settings) -> None:
        # Singletons

        # Loading setting
        self.settings: Settings = settings

        # Setup log level avec les settings
        logger.info(f"Listener log level: {self.settings.LISTENER_LOG_LEVEL}")
        configure_logger(log_level=self.settings.LISTENER_LOG_LEVEL)

        # Prefetch service config
        logger.info("⏳ Loading services configuration ...")
        logger.info(f"Using services config file: {self.settings.SERVICES_CONFIG_FILE}")
        ServicesConfigRepository.load_services_config(self.settings.SERVICES_CONFIG_FILE)
        for service in ServicesConfigRepository.SERVICES:
            logger.info(f"- Service loaded: {service}")

    def session(self) -> AsyncSession:
        return TaskAwareAsyncSession()  # type: ignore

    def task_repository(self) -> TaskRepository:
        return TaskRepository(self.session())

    def http_notifier(self) -> HttpNotifier:
        return HttpNotifier(self.settings.LISTENER_NOTIFIER_RETRY)

    def amqp_notifier(self) -> AmqpNotifier:
        return AmqpNotifier(self.settings.LISTENER_NOTIFIER_RETRY)

    def notification_service(self) -> NotificationService:
        return NotificationService(
            [
                self.http_notifier(),
                self.amqp_notifier(),
            ],
        )

    def message_service(self) -> MessageService:
        return MessageService(
            self.task_repository(),
            self.notification_service(),
            self.session(),
        )

    def service_repository(self) -> ServicesConfigRepository:
        return ServicesConfigRepository()

    def app(self) -> QueueListener:
        return QueueListener(
            message_service=self.message_service(),
            service_repository=self.service_repository(),
            rabbitmq_url=self.settings.BROKER_URL,
            concurrency=self.settings.LISTENER_CONCURRENCY,
        )
    
    def health_check(self) -> HealthCheckServer:
        server = HealthCheckServer(self.settings.HEALTH_CHECK_HOST,
                                   self.settings.HEALTH_CHECK_PORT)
        return server
