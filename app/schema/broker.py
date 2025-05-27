from abc import ABC, abstractmethod


class Broker(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def add_task(self, task):
        pass
