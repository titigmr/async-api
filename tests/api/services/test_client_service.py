
import unittest
from unittest.mock import Mock

from api.repositories.client_config_repository import ClientAuthorization, ClientConfig, ClientConfigRepository
from api.services.client_service import ClientService


class TestServiceServices(unittest.TestCase):
    def setUp(self):
        self.client_config_repo_mock: ClientConfigRepository = Mock()
        self.service_service = ClientService(self.client_config_repo_mock)

        data = {
            "client1_id": ClientConfig(
                client_id="client1_id",
                client_secret="client1_secret",
            ),
            "client2_id": ClientConfig(
                client_id="client2_id",
                client_secret=None, # No secret for client2 -> Can connect without secret
            ),
            "client3_id": ClientConfig(
                client_id="client3_id",
                client_secret="client3_secret",
                authorizations={
                    "example_service": ClientAuthorization(service="example_service", quotas=100),
                    "another_service": ClientAuthorization(service="another_service", quotas=None), 
                }
            ),
            "client4_id": ClientConfig(
                client_id="client4_id",
                client_secret="client3_secret",
                authorizations={
                    "all": ClientAuthorization(service="all", quotas=100),
                }
            ),
        }

        self.client_config_repo_mock.all_services.return_value = data
        self.client_config_repo_mock.get_client.side_effect = lambda client_id: data.get(client_id, None)

    def test_is_valid_client_id_with_secret(self):
        
        # Test with a valid client ID and secret
        assert self.service_service.is_valid_client_id("client1_id", "client1_secret")

        # Test with client with no creds
        assert self.service_service.is_valid_client_id("client2_id", None)
        assert self.service_service.is_valid_client_id("client2_id", "bob")

        # Test with an invalid client ID
        assert not self.service_service.is_valid_client_id("invalid_client_id", "bob")

        # Test with a bad secret
        assert not self.service_service.is_valid_client_id("client1_id", "bad_secret")
    
    def test_get_client_authorization_for_service(self):
        # Existing client without authorization
        authorization = self.service_service.get_client_authorization_for_service("client1_id", "example_service")
        assert authorization is None
        
        # Test with an invalid client ID
        authorization = self.service_service.get_client_authorization_for_service("invalid_client_id", "example_service")
        assert authorization is None

        # Test with an invalid client ID
        authorization = self.service_service.get_client_authorization_for_service("client3_id", "example_service")
        assert authorization is not None
        assert authorization.service == "example_service"
        assert authorization.quotas == 100

        authorization = self.service_service.get_client_authorization_for_service("client3_id", "another_service")
        assert authorization is not None
        assert authorization.service == "another_service"
        assert authorization.quotas == None

        # All access
        authorization = self.service_service.get_client_authorization_for_service("client4_id", "another_service")
        assert authorization is not None
        assert authorization.service == "all"
        assert authorization.quotas == 100

