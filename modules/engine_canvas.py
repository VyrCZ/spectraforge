from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.log_manager import Log

class CanvasEngine(Engine):

    def __init__(self, renderer):
        # the color changes are stored in the state, not directly put into the renderer, so the state can be restored
        self.renderer = renderer
        self.state = [(0, 0, 0)] * len(renderer)

    def on_enable(self):
        for pix in range(len(self.renderer)):
            self.renderer[pix] = self.state[pix]
        self.renderer.show()
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
        if len(pixel_list) != len(self.renderer):
            Log.warn("CanvasEngine", "Pixel list length does not match the canvas size, not updating.")
            return
        Log.debug("CanvasEngine", pixel_list)
        self.state = pixel_list
        for pix in range(len(self.renderer)):
            self.renderer[pix] = self.state[pix]
        self.renderer.show()
        Log.debug("CanvasEngine", "renderer updated.")
    