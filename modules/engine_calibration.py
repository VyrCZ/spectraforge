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

    def __init__(self, pixels, take_photo_callback, send_image_callback, setup_done_callback):
        self.pixels = pixels
        self.pixel_count = 200  # Default pixel count, should be set by the setup
        self.take_photo_callback = take_photo_callback
        self.send_image_callback = send_image_callback
        self.setup_done_callback = setup_done_callback
        self.calibration_color = (255, 255, 255)  # Red color for calibration
        self.current_setup = None
        self.image_dir = os.path.join(self.IMAGE_DIR_ROOT, datetime.now().strftime("%Y-%m-%d")) # fallback, just in case

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

    @EngineManager.requires_active
    def start_shooting(self):
        """
        Start the photo shooting process.
        Returns True when ready to start.
        """
        self.current_index = -1
        Log.info("CalibrationEngine", "Starting shooting process.")
        self.next_pixel()
    
    @EngineManager.requires_active
    def next_pixel(self):
        """
        Show the next pixel in the calibration process.
        """
        if self.current_index >= len(self.pixels):
            Log.info("CalibrationEngine", "All pixels have been shown.")
            return
        self.current_index += 1
        self.pixels.fill((0, 0, 0))
        self.pixels[self.current_index] = self.calibration_color
        self.pixels.show()
        # give time to the camera to focus
        time.sleep(0.5)
        Log.debug("CalibrationEngine", f"Showing pixel {self.current_index}.")
        self.take_photo_callback()

    @EngineManager.requires_active
    def receive_photo_data(self, data):
        """
        Save an image of the pixel shown at the given index.
        """

        Log.debug("CalibrationEngine", f"Received photo data for pixel index: {self.current_index}")
        # make sure the image directory exists
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        image_data = data.get("image")

        if not image_data:
            raise ValueError("Image cannot be empty.")
                # Decode the Base64 string
        image_bytes = base64.b64decode(image_data.split(",")[1])

        # Save the image to a file
        file_path = os.path.join(self.image_dir, f"{self.current_index}.png")
        with open(file_path, "wb") as image_file:
            image_file.write(image_bytes)

        #if self.current_index < len(self.pixels):
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

    def calculate_led_position(self, file_name):
        """
        Tries to calculate the pixel position of the LED in the image.
        """
        image_path = os.path.join(self.image_dir, file_name)
        image = Image.open(image_path).convert("L")
        pixels = image.load()
        width, height = image.size

        brightest_value = 0
        for x in range(width):
            for y in range(height):
                if pixels[x, y] > brightest_value:
                    brightest_value = pixels[x, y]

        brightest_pixels = []
        for x in range(width):
            for y in range(height):
                if pixels[x, y] == brightest_value:
                    brightest_pixels.append((x, y))

        if not brightest_pixels:
            return width // 2, height // 2

        sum_x = sum(p[0] for p in brightest_pixels)
        sum_y = sum(p[1] for p in brightest_pixels)
        center_x = int(sum_x / len(brightest_pixels))
        center_y = int(sum_y / len(brightest_pixels))

        DISTANCE_THRESHOLD = 30
        filtered_pixels = []
        for x, y in brightest_pixels:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance <= DISTANCE_THRESHOLD:
                filtered_pixels.append((x, y))

        if filtered_pixels:
            sum_x = sum(p[0] for p in filtered_pixels)
            sum_y = sum(p[1] for p in filtered_pixels)
            center_x = int(sum_x / len(filtered_pixels))
            center_y = int(sum_y / len(filtered_pixels))
        
        return center_x, center_y
        

    def send_next_image(self):
        # get the led position from the image, then convert the image to base64
        self.current_index += 1
        x, y = self.calculate_led_position(f"{self.current_index}.png")
        base64_image = base64.b64encode(open(os.path.join(self.image_dir, f"{self.current_index}.png"), "rb").read()).decode('utf-8')
        image_data = f"data:image/png;base64,{base64_image}"
        self.send_image_callback(image_data, x, y)

    @EngineManager.requires_active
    def receive_image_position(self, x, y):
        Log.debug("CalibrationEngine", f"Received position data for pixel {self.current_index}: ({x}, {y})")
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