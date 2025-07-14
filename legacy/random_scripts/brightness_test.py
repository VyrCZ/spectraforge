from tkinter import Tk, Canvas
from PIL import Image, ImageTk
import numpy as np

# Load the image
image_path = "calibration/images/tree-2024/front/31.jpg"
image = Image.open(image_path)

# Scale factor (e.g., 0.5 to reduce to half size)
scale = 1
scaled_width, scaled_height = int(image.width * scale), int(image.height * scale)

# Resize the image
image = image.resize((scaled_width, scaled_height), Image.LANCZOS)

# Find the brightest pixel
image_array = np.array(image.convert("L"))  # Convert to grayscale for brightness calculation
brightest_value = np.max(image_array)
brightest_pixels = np.where(image_array == brightest_value)

# Change all brightest pixels to pure red
image_rgb = image.convert("RGB")
image_data = np.array(image_rgb)
image_data[brightest_pixels] = [255, 0, 0]  # Set to red
image = Image.fromarray(image_data)

# Output the coordinates of the brightest pixel
brightest_y, brightest_x = brightest_pixels[0][0], brightest_pixels[1][0]
print(f"Brightest pixel at: ({brightest_x}, {brightest_y})")

# Draw crosshairs at the brightest pixel
for x in range(scaled_width):
    image_data[brightest_y, x] = [255, 0, 0]  # Horizontal line
for y in range(scaled_height):
    image_data[y, brightest_x] = [255, 0, 0]  # Vertical line

# Save the modified image
output_path = "31_modified.jpg"
Image.fromarray(image_data).save(output_path)
print(f"Modified image saved to: {output_path}")
