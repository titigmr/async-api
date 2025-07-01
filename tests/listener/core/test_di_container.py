# Nothing to do... just test the creation of the root
# application
from api.core.config import Settings
from listener.core.di_container import DIContainer
from listener.services.queue_listener import QueueListener


def test_di_container() -> None:
    app = DIContainer(Settings()).app()
    assert isinstance(app, QueueListener)
