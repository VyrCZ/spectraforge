from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.log_manager import Log

class EngineTest1(Engine):
    """
    A test engine implementation for testing purposes.
    """

    def __init__(self):
        Log.info("EngineTest1", "EngineTest1 initialized.")

    def on_enable(self):
        Log.info("EngineTest1", "EngineTest1 enabled.")

    def on_disable(self):
        Log.info("EngineTest1", "EngineTest1 disabled.")

    @EngineManager.requires_active
    def test_function(self):
        Log.info("EngineTest1", "Test function, yo")

    