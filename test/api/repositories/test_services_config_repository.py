import unittest

from api.repositories.services_config_repository import ServicesConfigException, ServicesConfigRepository

class TestServicesConfigRepository(unittest.TestCase):

    def test_initialization_non_existant_file(self):
        self.assertRaises(ServicesConfigException, ServicesConfigRepository.load_services_config, svc_file="non_existent_file.yaml")

    def test_initialization_bad_yaml_file(self):
        self.assertRaises(ServicesConfigException, ServicesConfigRepository.load_services_config, svc_file="./test/resources/bad_yaml.yaml")

    def test_all_services(self):
        # Sigleton registration (read config at startup)
        ServicesConfigRepository.load_services_config("./test/resources/services.yaml")
        print(f"{ServicesConfigRepository.SERVICES}")
        service_config_repository = ServicesConfigRepository()
        services = service_config_repository.all_services()
        self.assertEqual(len(services), 2)
        self.assertIn("example", services)
        self.assertIn("example2", services)
        self.assertEqual(services["example"].quotas, 1000)
        self.assertEqual(services["example2"].quotas, None)
        self.assertEqual(services["example"].json_schema.get("$schema"),"http://json-schema.org/draft-07/schema#")
        self.assertEqual(services["example2"].json_schema, None)
        self.assertEqual(services["example"].in_queue, "the_in_queue")
        self.assertEqual(services["example2"].in_queue, "example2_in_queue")
        self.assertEqual(services["example"].out_queue, "the_out_queue")
        self.assertEqual(services["example2"].out_queue, "example2_out_queue")

    def test_initialization_bad_shema_file(self):
        self.assertRaises(ServicesConfigException, ServicesConfigRepository.load_services_config, svc_file="./test/resources/services_bad_schema.yaml")


if __name__ == '__main__':
  unittest.main()