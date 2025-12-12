from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import modules.mathutils as mu

from typing import Tuple, List, Optional
from PIL import Image

class VideoEngine(Engine):
    """
    A video engine implementation for image and video processing.
    Maps an input image onto the convex polygon defined by setup.coords
    using a 'Cover' (Fill) strategy to eliminate black bars.
    """

    def __init__(self, renderer, setup):
        Log.info("EngineVideo", "EngineVideo initialized.")
        self.renderer = renderer
        self.on_setup_changed(setup)

    def on_setup_changed(self, setup):
        Log.debug("EngineVideo", f"Setup changed to {setup.name}")
        self.setup = setup
        self.coords = setup.coords  # list[tuple[float, float, float]]
        # Calculate bounds immediately
        self.bounds = mu.Bounds(setup.coords)

    def on_enable(self):
        Log.info("EngineVideo", "EngineVideo enabled.")

    def on_disable(self):
        Log.info("EngineVideo", "EngineVideo disabled.")

    @EngineManager.requires_active
    def display_img(self, path: str, mode: str = "cover"):
        """
        Loads an image and maps it to the LEDs.
        
        Args:
            path: Path to the image file.
            mode: "cover" (default) crops edges to fill all LEDs. 
                  "contain" ensures the whole image is visible but may leave edges black.
        """
        Log.info("EngineVideo", f"Displaying image: {path} (mode={mode})")

        if not self.coords:
            Log.warn("EngineVideo", "No coordinates defined in setup.")
            return

        # 1. Load Image
        try:
            # Convert to RGB to ensure getpixel returns (r,g,b)
            img = Image.open(path).convert("RGB")
        except Exception as e:
            Log.error("EngineVideo", f"Failed to load image: {e}")
            return

        img_w, img_h = img.size

        # 2. Get Physical Bounds & Dimensions
        x_min, x_max = self.bounds.min_x, self.bounds.max_x
        y_min, y_max = self.bounds.min_y, self.bounds.max_y

        led_width = x_max - x_min
        led_height = y_max - y_min
        
        # Avoid division by zero if point cloud is a straight line or single point
        if led_width == 0: led_width = 1.0
        if led_height == 0: led_height = 1.0

        led_center_x = (x_min + x_max) / 2.0
        led_center_y = (y_min + y_max) / 2.0
        
        img_center_x = img_w / 2.0
        img_center_y = img_h / 2.0

        # 3. Calculate Scale Factor
        # Calculate how much we need to scale the image to match physical width/height
        scale_w = img_w / led_width
        scale_h = img_h / led_height

        # Select scaling strategy
        if mode == "cover":
            # Scale based on the dimension that needs MORE scaling to fill the bounds
            # (This crops the other dimension)
            scale = max(scale_w, scale_h)
        else:
            # "contain" - Scale based on dimension that fits fully inside
            scale = min(scale_w, scale_h)

        # 4. Map LEDs
        leds = self.renderer.leds
        count = min(len(leds), len(self.coords))

        for i in range(count):
            # Unpack coordinates (ignoring Z if present)
            coord = self.coords[i]
            x, y = coord[0], coord[1]

            # A. Center the LED coordinate (Physical Space)
            x_rel = x - led_center_x
            y_rel = y - led_center_y

            # B. Apply Scale and Flip Y
            # Standard convention: 
            # Physical Y is UP (+), Image Y is DOWN (+).
            # To map Top-Physical to Top-Image, we negate the relative Y.
            u_centered = x_rel * scale
            v_centered = -y_rel * scale 

            # C. Shift to Image Coordinates
            u = int(img_center_x + u_centered)
            v = int(img_center_y + v_centered)

            # D. Clamp to valid image bounds
            u = max(0, min(u, img_w - 1))
            v = max(0, min(v, img_h - 1))

            # E. Set Color
            leds[i] = img.getpixel((u, v))
            self.renderer.show()

        Log.debug("EngineVideo", f"Mapped {count} LEDs.")