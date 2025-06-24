from modules.engine import Engine
from modules.engine_manager import EngineManager

class CalibrationEngine(Engine):
    """
    A test engine implementation for testing purposes.
    """

    def __init__(self, pixels):
        self.pixels = pixels
        print("Calibration initialized.")

    def on_enable(self):
        print("Calibration enabled.")

    def on_disable(self):
        print("Calibration disabled.")

    @EngineManager.requires_active
    def start_calibration(self):
        self.pixels.fill((255, 0, 0))
        self.pixels.show()
        print("Calibration started.")

    