from abc import ABC, abstractmethod


class AbstractBroker(ABC):
    @abstractmethod
    def setup(self) -> None:
        """Initialize the broker connection and any necessary setup."""
        pass

    @abstractmethod
    def add_task(self, task, service: str) -> None:
        """Add a task to the broker."""
        pass

    @abstractmethod
    def ping(self) -> None:
        """Check if the broker is reachable."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the broker connection."""
        pass
