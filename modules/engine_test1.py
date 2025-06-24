from modules.engine import Engine
from modules.engine_manager import EngineManager

class EngineTest1(Engine):
    """
    A test engine implementation for testing purposes.
    """

    def __init__(self):
        print("EngineTest1 initialized.")

    def on_enable(self):
        print("EngineTest1 enabled.")

    def on_disable(self):
        print("EngineTest1 disabled.")

    @EngineManager.requires_active
    def test_function(self):
        print("Test function, yo")

    