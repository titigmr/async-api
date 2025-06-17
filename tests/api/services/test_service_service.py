from typing import TypeVar
import unittest
from unittest.mock import Mock

from api.repositories.services_config_repository import ServicesConfig, ServicesConfigRepository
from api.services.service_service import ServiceService

class TestServiceServices(unittest.TestCase):
    def setUp(self):
        self.services_config_repo_mock: ServicesConfigRepository = Mock()
        self.service_service = ServiceService(self.services_config_repo_mock)

        self.services_config_repo_mock.all_services.return_value = {
            "example": ServicesConfig(name="example", quotas=1000, json_schema={"$schema": "http://json-schema.org/draft-07/schema#"}, in_queue="example_in_queue", out_queue="example_out_queue"),
            "example2": ServicesConfig(name="example2", quotas=None, json_schema=None, in_queue="the_in_queue", out_queue="the_out_queue"),
        }

    def test_check_service_exists(self):

        # Test with an existing service
        self.service_service.check_service_exists("example")
        
        # Test with a non-existing service
        with self.assertRaises(Exception):
            self.service_service.check_service_exists("non_existing_service")

    def test_list_services_names(self):
        services = self.service_service.list_services_names()
        self.assertIn("example", services)
        self.assertIn("example2", services)

    def test_list_all(self):
        services = self.service_service.list_all()
        self.assertEqual(len(services), 2)

        example = next((i for i in services if i.name == "example"), None)
        example2 = next((i for i in services if i.name == "example2"), None)

        assert example is not None
        assert example2 is not None

        assert example.name == "example"
        assert example2.name == "example2"
        assert example.json_schema is not None 
        assert example2.json_schema is None 

