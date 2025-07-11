from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.log_manager import Log

class LightshowEngine(Engine):
    """
    A test engine implementation for testing purposes.
    """

    def __init__(self):
        Log.info("LightshowEngine", "LightshowEngine initialized.")

    def on_enable(self):
        Log.info("LightshowEngine", "LightshowEngine enabled.")

    def on_disable(self):
        Log.info("LightshowEngine", "LightshowEngine disabled.")

    