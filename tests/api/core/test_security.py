

from unittest.mock import Mock
from fastapi.security import HTTPBasicCredentials
import pytest
from api.core.security import auth_guard
from api.schemas.errors import Unauthorized
from api.services.client_service import ClientService


def test_auth_guard_ok():
    pass
    client_service: ClientService = Mock()
    client_service.is_valid_client_id.return_value = True
    
    client = auth_guard(HTTPBasicCredentials(username="toto",password="password"),client_service)
    assert client == "toto"

def test_auth_guard_ko():
    pass
    client_service: ClientService = Mock()
    client_service.is_valid_client_id.return_value = False
    
    with pytest.raises(Unauthorized):
        auth_guard(HTTPBasicCredentials(username="toto",password="password"),client_service)
