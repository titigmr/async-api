import unittest

from api.repositories.client_config_repository import ClientConfigRepository, ClientsConfigException

class TestClientConfigRepository(unittest.TestCase):

    def test_initialization_non_existant_file(self):
        self.assertRaises(ClientsConfigException, ClientConfigRepository.load_clients_config, client_file="non_existent_file.yaml")

    def test_initialization_bad_yaml_file(self):
        self.assertRaises(ClientsConfigException, ClientConfigRepository.load_clients_config, client_file="./test/resources/bad_yaml.yaml")

    def test_all_clients(self):
        # Sigleton registration (read config at startup)
        ClientConfigRepository.load_clients_config("./test/resources/clients.yaml")
        print(f"{ClientConfigRepository.CLIENTS}")
        client_config_repository = ClientConfigRepository()
        clients = client_config_repository.all_clients()
        self.assertEqual(len(clients), 2)
        self.assertIn("client1", clients)
        self.assertEqual(clients["client1"].client_id, "ZERJGbnkzjhejuyiyaze")
        self.assertEqual(len(clients["client1"].authorizations), 2)
        self.assertEqual(clients["client1"].authorizations["example1"].service, "example1")
        self.assertEqual(clients["client1"].authorizations["example1"].quotas, 100)
        self.assertEqual(clients["client1"].authorizations["example2"].service, "example2")
        self.assertEqual(clients["client1"].authorizations["example2"].quotas, None)
        
        self.assertEqual(clients["client2"].name, "client2")
        self.assertEqual(clients["client2"].client_id, "aERJGbnkzjhejuyiyaze")
        self.assertEqual(clients["client2"].client_secret, None)
        self.assertEqual(len(clients["client2"].authorizations), 0)

