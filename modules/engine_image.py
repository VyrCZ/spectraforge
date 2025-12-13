from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import modules.mathutils as mu
import modules.display_utils as du # Import the new util

from PIL import Image

class ImageEngine(Engine):
    """
    Engine dedicated to displaying static images.
    """
    def __init__(self, renderer, setup):
        Log.info("ImageEngine", "ImageEngine initialized.")
        self.renderer = renderer
        self.on_setup_changed(setup)

    def on_setup_changed(self, setup):
        self.setup = setup
        self.coords = setup.coords
        self.bounds = mu.Bounds(setup.coords)

    def on_enable(self):
        Log.info("ImageEngine", "Enabled.")

    def on_disable(self):
        Log.info("ImageEngine", "Disabled.")
        # Optional: Clear LEDs on disable
        # self.renderer.clear()
        # self.renderer.show()

    @EngineManager.requires_active
    def display_image(self, path: str, mode: str = "fill", sample_radius: int = 1):
        try:
            img = Image.open(path).convert("RGB")
            du.map_image_to_leds(img, self.renderer, self.coords, self.bounds, mode, sample_radius)
            self.renderer.show()
            Log.info("ImageEngine", f"Displayed: {path}")
        except Exception as e:
            Log.error("ImageEngine", f"Failed to load image: {e}")