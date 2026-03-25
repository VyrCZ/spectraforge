from modules.engine import Engine
from modules.engine_manager import EngineManager
import os
import time
import base64
from modules.setup import SetupType, Setup
from modules.log_manager import Log
from datetime import datetime
from PIL import Image
import math
import json

class CalibrationEngine(Engine):
    """
    A test engine implementation for testing purposes.
    """

    IMAGE_DIR_ROOT = "calibration/images/"
    SETUP_DIR_ROOT = "config/setups/"
    VIEWS = ["front", "right", "back", "left"]

    def __init__(self, renderer, take_photo_callback, send_image_callback, setup_done_callback):
        self.renderer = renderer
        self.pixel_count = 200  # Default pixel count, should be set by the setup
        self.take_photo_callback = take_photo_callback
        self.send_image_callback = send_image_callback
        self.setup_done_callback = setup_done_callback
        self.calibration_color = (255, 255, 255)  # Red color for calibration
        self.current_setup = None
        self.image_dir = os.path.join(self.IMAGE_DIR_ROOT, datetime.now().strftime("%Y-%m-%d")) # fallback, just in case
        self.current_view = 0  # For 3D: current view index (0=front, 1=right, 2=back, 3=left)
        self.center_3d = (0, 0)  # Center point for 3D coordinate conversion, computed from first image

    def on_enable(self):
        Log.info("CalibrationEngine", "CalibrationEngine enabled.")

    def on_disable(self):
        Log.info("CalibrationEngine", "CalibrationEngine disabled.")

    @EngineManager.requires_active
    def new_setup(self, setup_name, setup_type: SetupType, led_count):
        """
        Initialize the calibration engine with a new setup.
        """
        self.current_setup = Setup(setup_name, setup_type, [])
        self.image_dir = os.path.join(self.IMAGE_DIR_ROOT, self.current_setup.get_formatted_name())
        self.pixel_count = led_count
        self.center_3d = (0, 0)  # Reset center for each new setup

    @EngineManager.requires_active
    def start_shooting(self):
        """
        Start the photo shooting process.
        Returns True when ready to start.
        """
        self.current_index = -1
        self.current_view = 0
        Log.info("CalibrationEngine", "Starting shooting process.")
        self.next_pixel()
    
    @EngineManager.requires_active
    def next_pixel(self):
        """
        Show the next pixel in the calibration process.
        """
        if self.current_index >= len(self.renderer):
            Log.info("CalibrationEngine", "All renderer have been shown.")
            return
        self.current_index += 1
        self.current_view = 0
        self.renderer.fill((0, 0, 0))
        self.renderer[self.current_index] = self.calibration_color
        self.renderer.show()
        # give time to the camera to focus
        time.sleep(0.5)
        Log.debug("CalibrationEngine", f"Showing pixel {self.current_index}.")
        if self.current_setup.type == SetupType.THREE_DIMENSIONAL:
            self.take_photo_callback(self.current_view)
        else:
            self.take_photo_callback()

    @EngineManager.requires_active
    def receive_photo_data(self, data):
        """
        Save an image of the pixel shown at the given index.
        """

        Log.debug("CalibrationEngine", f"Received photo data for pixel index: {self.current_index}")

        image_data = data.get("image")

        if not image_data:
            raise ValueError("Image cannot be empty.")
                # Decode the Base64 string
        image_bytes = base64.b64decode(image_data.split(",")[1])

        if self.current_setup.type == SetupType.THREE_DIMENSIONAL:
            # Save image into view-specific subdirectory
            view_dir = os.path.join(self.image_dir, self.VIEWS[self.current_view])
            if not os.path.exists(view_dir):
                os.makedirs(view_dir)
            file_path = os.path.join(view_dir, f"{self.current_index}.png")
            with open(file_path, "wb") as image_file:
                image_file.write(image_bytes)
            # Advance to the next view, or to the next pixel when all views are done
            self.current_view += 1
            if self.current_view < len(self.VIEWS):
                self.take_photo_callback(self.current_view)
            elif self.current_index < self.pixel_count - 1:
                self.next_pixel()
            else:
                self.start_editing()
        else:
            # make sure the image directory exists
            if not os.path.exists(self.image_dir):
                os.makedirs(self.image_dir)

            # Save the image to a file
            file_path = os.path.join(self.image_dir, f"{self.current_index}.png")
            with open(file_path, "wb") as image_file:
                image_file.write(image_bytes)

            #if self.current_index < len(self.renderer):
            if self.current_index < self.pixel_count - 1: # testing
                self.next_pixel()
            else:
                self.start_editing()

    def start_editing(self):
        """
        Start the editing process for the captured images.
        """
        self.current_index = -1
        self.send_next_image()

    def _find_brightest_pixel(self, img):
        """Find the brightest pixel location and value in a grayscale PIL image."""
        width, height = img.size
        pixels = img.load()
        max_val = -1
        max_loc = (width // 2, height // 2)
        for x in range(width):
            for y in range(height):
                if pixels[x, y] > max_val:
                    max_val = pixels[x, y]
                    max_loc = (x, y)
        return max_loc, max_val

    def calculate_led_position(self, file_name):
        """
        Tries to calculate the pixel position of the LED in the image.
        """
        image_path = os.path.join(self.image_dir, file_name)
        image = Image.open(image_path).convert("L")
        renderer = image.load()
        width, height = image.size

        brightest_value = 0
        for x in range(width):
            for y in range(height):
                if renderer[x, y] > brightest_value:
                    brightest_value = renderer[x, y]

        brightest_renderer = []
        for x in range(width):
            for y in range(height):
                if renderer[x, y] == brightest_value:
                    brightest_renderer.append((x, y))

        if not brightest_renderer:
            return width // 2, height // 2

        sum_x = sum(p[0] for p in brightest_renderer)
        sum_y = sum(p[1] for p in brightest_renderer)
        center_x = int(sum_x / len(brightest_renderer))
        center_y = int(sum_y / len(brightest_renderer))

        DISTANCE_THRESHOLD = 30
        filtered_renderer = []
        for x, y in brightest_renderer:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance <= DISTANCE_THRESHOLD:
                filtered_renderer.append((x, y))

        if filtered_renderer:
            sum_x = sum(p[0] for p in filtered_renderer)
            sum_y = sum(p[1] for p in filtered_renderer)
            center_x = int(sum_x / len(filtered_renderer))
            center_y = int(sum_y / len(filtered_renderer))
        
        return center_x, center_y

    def calculate_led_position_3d(self, led_index):
        """
        Calculate 3D world coordinates from the 4 view images for the given LED index.
        Uses the brightest pixel from the best-lit view for each axis, mirroring the
        coordinate convention from calibration/find_light_positions.py.
        """
        bright_locs = []
        bright_vals = []

        for view_name in self.VIEWS:
            path = os.path.join(self.image_dir, view_name, f"{led_index}.png")
            img = Image.open(path).convert("L")
            # Initialize center lazily from the first image.
            # The y-coordinate defaults to the bottom of the frame (h), matching the
            # legacy find_light_positions.py convention where the object base is the origin.
            if self.center_3d == (0, 0):
                w, h = img.size
                self.center_3d = (w // 2, h)
            loc, val = self._find_brightest_pixel(img)
            bright_locs.append(loc)
            bright_vals.append(val)

        cx, cy = self.center_3d

        # X (and Y) from front (view 0) or back (view 2), pick brighter
        if bright_vals[0] >= bright_vals[2]:
            px, py = bright_locs[0]
            world_x = px - cx
            world_y = py - cy
        else:
            px, py = bright_locs[2]
            world_x = cx - px
            world_y = py - cy

        # Z from right (view 1) or left (view 3), pick brighter
        if bright_vals[1] >= bright_vals[3]:
            pz, _ = bright_locs[1]
            world_z = pz - cx
        else:
            pz, _ = bright_locs[3]
            world_z = cx - pz

        return world_x, world_y, world_z

    def _world_to_image_3d(self, world_pos, view):
        """Convert 3D world coordinates to 2D image pixel coordinates for a given view."""
        x, y, z = world_pos
        cx, cy = self.center_3d
        if view == 0:    # front
            return (x + cx, y + cy)
        elif view == 1:  # right
            return (z + cx, y + cy)
        elif view == 2:  # back
            return (cx - x, y + cy)
        elif view == 3:  # left
            return (cx - z, y + cy)
        return (cx, cy)

    def send_next_image(self):
        # get the led position from the image, then convert the image to base64
        self.current_index += 1
        if self.current_setup.type == SetupType.THREE_DIMENSIONAL:
            self._send_next_image_3d()
        else:
            x, y = self.calculate_led_position(f"{self.current_index}.png")
            base64_image = base64.b64encode(open(os.path.join(self.image_dir, f"{self.current_index}.png"), "rb").read()).decode('utf-8')
            image_data = f"data:image/png;base64,{base64_image}"
            self.send_image_callback(image_data, x, y)

    def _send_next_image_3d(self):
        """Send all 4 view images and the initial 3D position estimate to the frontend."""
        led_index = self.current_index
        x, y, z = self.calculate_led_position_3d(led_index)

        images = {}
        for view_name in self.VIEWS:
            path = os.path.join(self.image_dir, view_name, f"{led_index}.png")
            b64 = base64.b64encode(open(path, "rb").read()).decode('utf-8')
            images[view_name] = f"data:image/png;base64,{b64}"

        self.send_image_callback(
            images["front"], x, y,
            z=z,
            extra_images=images,
            center=self.center_3d
        )

    @EngineManager.requires_active
    def receive_image_position(self, x, y, z=None):
        Log.debug("CalibrationEngine", f"Received position data for pixel {self.current_index}: ({x}, {y}, {z})")
        if self.current_setup.type == SetupType.THREE_DIMENSIONAL:
            if z is None:
                raise ValueError("Z coordinate is required for 3D setups.")
            self.current_setup.coords.append((x, y, z))
        else:
            self.current_setup.coords.append((x, y))
        if self.current_index < self.pixel_count - 1:
            self.send_next_image()
        else:
            self.finish_setup()

    def finish_setup(self):
        setup_data = {
            "type": str(self.current_setup.type.value),
            "coordinates": self.current_setup.coords
        }
        setup_file_path = os.path.join(self.SETUP_DIR_ROOT, f"{self.current_setup.get_formatted_name()}.json")
        with open(setup_file_path, "w") as setup_file:
            json.dump(setup_data, setup_file, indent=4)
        Log.info("CalibrationEngine", f"Calibration is done, setup {self.current_setup.get_formatted_name()} saved.")
        self.setup_done_callback()