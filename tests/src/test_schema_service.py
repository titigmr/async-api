import pytest
from pydantic import BaseModel, ValidationError
from src.schemas.service import ServiceBase


class MyInputSchema(BaseModel):
    id: int
    name: str


def test_service_base_initialization():
    service = ServiceBase[MyInputSchema](
        service_name="TestService",
        queue_name_in="queue_in",
        input_schema=MyInputSchema,
    )

    assert service.service_name == "TestService"
    assert service.queue_name_in == "queue_in"
    assert service.queue_name_out is None
    assert service.capacity == 0
    assert issubclass(service.input_schema, BaseModel)
    assert service.json_schema == {
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "name": {"title": "Name", "type": "string"},
        },
        "required": ["id", "name"],
        "title": "MyInputSchema",
        "type": "object",
    }


def test_service_base_invalid_schema():
    with pytest.raises(ValidationError):
        ServiceBase(
            service_name="BadService",
            queue_name_in="queue_in",
            json_schema=str,
        )
