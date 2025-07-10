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
        for pix in range(len(self.pixels)):
            self.pixels[pix] = self.state[pix]
        self.pixels.show()
        Log.info("CanvasEngine", "CanvasEngine enabled.")

    def on_disable(self):
        Log.info("CanvasEngine", "CanvasEngine disabled.")

    @EngineManager.requires_active
    def get_pixels(self):
        return self.state
    
    @EngineManager.requires_active
    def set_pixels(self, pixel_list):
        """
        Set the pixel colors in the canvas.
        (You have to set the whole pixel list, not just a part of it.)
        :param pixel_list: List of tuples representing RGB colors for each pixel.
        """
        if len(pixel_list) != len(self.pixels):
            Log.warn("CanvasEngine", "Pixel list length does not match the canvas size, not updating.")
            return
        Log.debug("CanvasEngine", pixel_list)
        self.state = pixel_list
        for pix in range(len(self.pixels)):
            self.pixels[pix] = self.state[pix]
        self.pixels.show()
        Log.debug("CanvasEngine", "Pixels updated.")
    