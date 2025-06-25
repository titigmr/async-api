from doctest import Example
from typing import TypeVar
import unittest

import pytest

from api.repositories.services_config_repository import ServicesConfigException, ServicesConfigRepository

def test_initialization_non_existant_file():
    with pytest.raises(ServicesConfigException):
        ServicesConfigRepository.load_services_config(svc_file="non_existent_file.yaml")

def test_initialization_bad_yaml_file():
    with pytest.raises(ServicesConfigException):
        ServicesConfigRepository.load_services_config(svc_file="./tests/resources/bad_yaml.yaml")

def test_all_services():
    # Sigleton registration (read config at startup)
    ServicesConfigRepository.load_services_config("./tests/resources/services.yaml")
    service_config_repository = ServicesConfigRepository()
    services = service_config_repository.all_services()
    assert len(services) == 2, "There should be 2 services loaded"
    assert services["example"] is not None
    assert services["example2"] is not None
    # Example
    example = services["example"]
    assert example.name == "example"
    assert example.quotas == 1000
    assert example.json_schema is not None
    assert example.json_schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert example.in_queue == "the_in_queue"
    assert example.out_queue == "the_out_queue"
    
    # Example2
    example2 = services["example2"]
    assert example2.name == "example2"
    assert example2.quotas is None
    assert example2.json_schema is None
    assert example2.in_queue == "example2_in_queue"
    assert example2.out_queue == "example2_out_queue"
    
def test_initialization_bad_shema_file():
    with pytest.raises(ServicesConfigException):
        ServicesConfigRepository.load_services_config(svc_file="./tests/resources/services_bad_schema.yaml")

