from abc import ABC, abstractmethod


"""
The engine system is designed to manage individual system that manage the LED effects.
Each engine must implement the `on_enable` and `on_disable` methods to handle enabling and disabling the engine.
The engine can communicate with the app using its own methods, but they all must have a decorator @EngineManager.requres_active, which will ensure that the engine is active before executing the method and disabling another engine, if necessary.
"""
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