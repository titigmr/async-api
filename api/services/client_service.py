

from typing import Annotated

from fastapi import Depends
from api.repositories.client_config_repository import ClientConfigRepository


class ClientService:
    """Service for managing Prometheus metrics related to tasks.
    This service provides methods to update custom metrics for tasks, including
    pending, running, success, and failure counts, as well as latency histograms.
    It uses the MetricsTaskRepository to fetch task data from the database.
    """

    def __init__(self, client_config_repository: Annotated[ClientConfigRepository,Depends(ClientConfigRepository)]) -> None:
        self.client_config_repository: ClientConfigRepository = client_config_repository
        
    def is_client_allowed_to_use_service(self, client_id: str, service: str) -> bool:
        """
        Check if a client is allowed to use a specific service.
        Returns True if the client is allowed, False otherwise.
        """
        clients = self.client_config_repository.all_clients()
        client = clients.get(client_id)
        
        if not client:
            return False
        
        return service in client.authorizations
