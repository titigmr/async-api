
from api.core.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.client_config_repository import ClientConfigRepository
from api.repositories.services_config_repository import ServicesConfigRepository
from api.repositories.task_repository import TaskRepository
from api.services.client_service import ClientService
from api.services.service_service import ServiceService
from listener.core.task_aware_async_session import TaskAwareAsyncSession
from listener.services.app import ListenerApp


class DIContainer:

    def __init__(self):
        # Singletons
        self.settings = Settings()

    def session(self) -> AsyncSession :
        return TaskAwareAsyncSession()  # type: ignore

    def task_repository(self):
        return TaskRepository(self.session())
    
    def service_repository(self):
        return ServicesConfigRepository()

    def service_service(self):
        return ServiceService(service_repository=self.service_repository())

    def client_repository(self):
        return ClientConfigRepository()

    def client_service(self):
        return ClientService(client_config_repository=self.client_repository())

    def app(self):
        return ListenerApp(self.task_repository())