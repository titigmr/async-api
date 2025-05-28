from pydantic import BaseModel, ConfigDict, model_validator, ValidationError
from typing import Type, TypeVar, Generic, Dict, Any, Optional

InputSchemaType = TypeVar("InputSchemaType", bound=BaseModel)


class ServiceBase(BaseModel, Generic[InputSchemaType]):
    service_name: str
    queue_name_in: str
    queue_name_out: Optional[str] = None
    capacity: Optional[int] = 0
    input_schema: Type[InputSchemaType]
    json_schema: Optional[Dict[str, Any]] = None  # auto-rempli

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def generate_json_schema(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("json_schema") is None:
            schema_class = values.get("input_schema")
            if schema_class:
                values["json_schema"] = schema_class.model_json_schema()
            else:
                raise ValueError("input_schema is required to generate json_schema")
        return values
