from abc import ABC, abstractmethod
from modules.setup import Setup

class Engine(ABC):
    """
    The engine system is designed to manage individual system that manage the LED effects.
    Each engine must implement the `on_enable` and `on_disable` methods to handle changing the engines. If you use the setup system, you should also implement the `on_setup_changed` method to handle changes in the setup.
    The engine can communicate with the app using its own methods, but they all must have a decorator @EngineManager.requres_active, which will ensure that the engine is active before executing the method and disabling another engine, if necessary.
    """

    @abstractmethod
    def on_enable(self):
        """
        Called when the engine is enabled. **(But not on the startup of the engine)**
        Use __init__ to set up the engine
        """
        pass

    @abstractmethod
    def on_disable(self):
        """Le turn off"""
        pass

    def on_setup_changed(self, setup: Setup):
        """
        Called when the setup is changed, regardless if enabled or not **(And also on the startup of the engine)**
        """
        pass