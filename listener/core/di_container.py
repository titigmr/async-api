from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import Settings
from api.repositories.services_config_repository import ServicesConfigRepository
from api.repositories.task_repository import TaskRepository
from listener.core.logger import configure_logger, logger
from listener.core.task_aware_async_session import TaskAwareAsyncSession
from listener.services.message_service import MessageService
from listener.services.notifier_service import NotificationService
from listener.services.notifiers.amqp_notifier import AmqpNotifier
from listener.services.notifiers.http_notifier import HttpNotifier
from listener.services.queue_listener import QueueListener


class DIContainer:
    def __init__(self, settings: Settings) -> None:
        # Singletons

        # Loading setting
        self.settings = settings

        # Setup log level avec les settings
        configure_logger(self.settings.LISTENER_LOG_LEVEL)

        # Prefetch service config
        logger.info("----------------------------")
        logger.info("⏳ Loading services configuration ...")
        logger.info(f"Using services config file: {self.settings.SERVICES_CONFIG_FILE}")
        ServicesConfigRepository.load_services_config(self.settings.SERVICES_CONFIG_FILE)
        for service in ServicesConfigRepository.SERVICES:
            logger.info(f"- Service loaded: {service}")
        logger.info("🤗 Done.")

    def session(self) -> AsyncSession:
        return TaskAwareAsyncSession()  # type: ignore

    def task_repository(self):
        return TaskRepository(self.session())

    def http_notifier(self):
        return HttpNotifier(self.settings.LISTENER_NOTIFIER_RETRY)

    def amqp_notifier(self):
        return AmqpNotifier(self.settings.LISTENER_NOTIFIER_RETRY)

    def notification_service(self):
        return NotificationService(
            [
                self.http_notifier(),
                self.amqp_notifier(),
            ],
        )

    def message_service(self):
        return MessageService(
            self.task_repository(),
            self.notification_service(),
            self.session(),
        )

    def service_repository(self):
        return ServicesConfigRepository()

    def app(self) -> QueueListener:
        return QueueListener(
            self.message_service(),
            self.service_repository(),
            self.settings.BROKER_URL,
            self.settings.LISTENER_CONCURRENCY,
        )
