from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.log_manager import Log

class CanvasEngine(Engine):
    """
    A test engine implementation for testing purposes.
    """

    def __init__(self, pixels):
        # the color changes are stored in the state, not directly put into the pixels, so the state can be restored
        self.pixels = pixels
        self.state = [(0, 0, 0)] * len(pixels)

    def on_enable(self):
        self.pixels = self.state
        Log.info("CanvasEngine", "CanvasEngine enabled.")

    def on_disable(self):
        Log.info("CanvasEngine", "CanvasEngine disabled.")

    @EngineManager.requires_active
    def get_pixels(self):
        return self.state
    
    @EngineManager.requires_active
    def set_pixels(self, pixel_dict):
        """
        Set the pixel colors in the canvas.
        pixel_dict format: 
        {
            pixel_index: (r, g, b),
            ...
        }
        """

        for index, color in pixel_dict.items():
            if 0 <= index < len(self.state):
                self.state[index] = color
            else:
                Log.warn("CanvasEngine", f"Pixel index {index} out of bounds. Ignoring.")
        self.pixels = self.state
        self.pixels.show()
        Log.debug("CanvasEngine", "Pixels updated.")

    @EngineManager.requires_active
    def clear_canvas(self):
        """
        Clear the canvas by setting all pixels to black.
        """
        self.state = [(0, 0, 0)] * len(self.pixels)
        self.pixels = self.state
        self.pixels.show()
        Log.debug("CanvasEngine", "Canvas cleared.")
    