from abc import ABC, abstractmethod

class Engine(ABC):
    """
    Abstract base class for an engine.
    """

    @abstractmethod
    def on_enable(self):
        pass

    @abstractmethod
    def on_disable(self):
        pass