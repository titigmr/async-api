import os
from re import S
import unittest

from api.repositories.client_config_repository import ClientConfigRepository, ClientsConfigException
from api.repositories.services_config_repository import ServicesConfigException

class TestClientConfigRepository(unittest.TestCase):

    def test_initialization_non_existant_file(self):
        with self.assertRaises(ClientsConfigException):
            ClientConfigRepository.load_clients_config(client_file="non_existent_file.yaml")

    def test_initialization_bad_yaml_file(self):
        with self.assertRaises(ClientsConfigException):
            ClientConfigRepository.load_clients_config(client_file="./tests/resources/bad_yaml.yaml")

    def test_all_clients(self):
        # Singleton registration (read config at startup)
        os.environ["CLIENT_SECRET_1"] = "bobs_secret"

        ClientConfigRepository.load_clients_config("./tests/resources/clients.yaml")
        client_config_repository = ClientConfigRepository()
        clients = client_config_repository.all_clients()
        
        assert len(clients) == 2
        assert "client1" in clients
        assert clients["client1"].client_id == "ZERJGbnkzjhejuyiyaze"
        assert len(clients["client1"].authorizations) == 2
        assert clients["client1"].authorizations["example1"].service == "example1"
        assert clients["client1"].authorizations["example1"].quotas == 100
        assert clients["client1"].authorizations["example2"].service == "example2"
        assert clients["client1"].authorizations["example2"].quotas is None

        assert clients["client2"].name == "client2"
        assert clients["client2"].client_id == "aERJGbnkzjhejuyiyaze"
        assert clients["client2"].client_secret is None
        assert len(clients["client2"].authorizations) == 0

    def test_all_clients_without_env_secret(self):
        # Assume the environment variable is not set
        del os.environ["CLIENT_SECRET_1"]

        # Test with a non-existing service
        with self.assertRaises(ClientsConfigException):
            ClientConfigRepository.load_clients_config("./tests/resources/clients.yaml")

