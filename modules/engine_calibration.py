from modules.engine import Engine
from modules.engine_manager import EngineManager
import os
import time
import base64
from modules.setup import SetupType, Setup
from datetime import datetime
from PIL import Image
import numpy as np

class CalibrationEngine(Engine):
    """
    A test engine implementation for testing purposes.
    """

    IMAGE_DIR_ROOT = "calibration/images/"

    def __init__(self, pixels, take_photo_callback, send_image_callback):
        self.pixels = pixels
        self.pixel_count = 3 # TODO: replace with the actual pixel count
        self.take_photo_callback = take_photo_callback
        self.send_image_callback = send_image_callback
        self.calibration_color = (255, 0, 0)  # Red color for calibration
        self.current_setup = None
        self.image_dir = os.path.join(self.IMAGE_DIR_ROOT, datetime.now().strftime("%Y-%m-%d")) # fallback, just in case

    def on_enable(self):
        print("Calibration enabled.")

    def on_disable(self):
        print("Calibration disabled.")

    @EngineManager.requires_active
    def new_setup(self, setup_name, setup_type: SetupType):
        """
        Initialize the calibration engine with a new setup.
        """
        self.positions = []
        self.current_setup = Setup(setup_name, setup_type, [], datetime.now().strftime("%Y-%m-%d"))
        self.image_dir = os.path.join(self.IMAGE_DIR_ROOT, self.current_setup.get_formatted_name())

    @EngineManager.requires_active
    def start_shooting(self):
        """
        Start the photo shooting process.
        Returns True when ready to start.
        """
        self.current_index = -1
        print("Starting shooting process.")
        self.next_pixel()
    
    @EngineManager.requires_active
    def next_pixel(self):
        """
        Show the next pixel in the calibration process.
        """
        if self.current_index >= len(self.pixels):
            print("All pixels have been shown.")
            return
        self.current_index += 1
        self.pixels.fill((0, 0, 0))
        self.pixels[self.current_index] = self.calibration_color
        self.pixels.show()
        # give time to the camera to focus
        #time.sleep(2) TODO: remove this after testing
        print(f"Showing pixel {self.current_index}.")
        self.take_photo_callback()

    @EngineManager.requires_active
    def receive_photo_data(self, data):
        """
        Save an image of the pixel shown at the given index.
        """

        print("Received photo data for pixel index:", self.current_index)
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
        if self.current_index <= self.pixel_count: # testing
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
        image = Image.open(image_path)

        # get the brightest pixels
        image_array = np.array(image.convert("L"))  # Convert to grayscale for brightness calculation
        brightest_value = np.max(image_array)
        brightest_pixels = np.where(image_array == brightest_value)

        # Average out coordinates of brightest pixels
        brightest_y = int(np.mean(brightest_pixels[0]))
        brightest_x = int(np.mean(brightest_pixels[1]))
        return brightest_x, brightest_y

    def send_next_image(self):
        # get the led position from the image, then convert the image to base64
        self.current_index += 1
        x, y = self.get_image_led_position(f"{self.current_index}.png")
        base64_image = base64.b64encode(open(os.path.join(self.image_dir, f"{self.current_index}.png"), "rb").read()).decode('utf-8')
        image_data = f"data:image/png;base64,{base64_image}"
        self.send_image_callback(image_data, x, y)

    @EngineManager.requires_active
    def receive_image_position(self, x, y):
        print(f"Received image position: ({x}, {y}) for pixel {self.current_index}.")
        self.positions.append((self.current_index, x, y))
        if self.current_index < self.pixel_count:
            self.send_next_image()
        else:
            print("All images processed. Finalizing setup.")