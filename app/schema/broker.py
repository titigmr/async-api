from abc import ABC, abstractmethod


class Broker(ABC):
    @abstractmethod
    def setup(self):
        """Initialize the broker connection and any necessary setup."""
        pass

    @abstractmethod
    def add_task(self, task):
        """Add a task to the broker."""
        pass

    @abstractmethod
    def ping(self):
        """Check if the broker is reachable."""
        pass
