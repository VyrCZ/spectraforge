from tkinter import Tk, Canvas
from PIL import Image, ImageTk
import numpy as np

# Load the image
image_path = "images/side.jpg"
image_path = "images\wall\IMG_20241205_154517.jpg"
image = Image.open(image_path)

# Scale factor (e.g., 0.5 to reduce to half size)
scale = 0.5
scaled_width, scaled_height = int(image.width * scale), int(image.height * scale)

# Resize the image
image = image.resize((scaled_width, scaled_height), Image.LANCZOS)

# Find the brightest pixel
image_array = np.array(image.convert("L"))  # Convert to grayscale for brightness calculation
brightest_y, brightest_x = np.unravel_index(np.argmax(image_array), image_array.shape)

# Output the coordinates of the brightest pixel
print(f"Brightest pixel at: ({brightest_x}, {brightest_y})")

# Create a GUI window
root = Tk()
root.title("Image Brightest Pixel")

# Convert the image for Tkinter compatibility
tk_image = ImageTk.PhotoImage(image)

# Create a canvas to display the image
canvas = Canvas(root, width=scaled_width, height=scaled_height)
canvas.pack()

# Add the image to the canvas
canvas.create_image(0, 0, anchor="nw", image=tk_image)

# Draw crosshairs at the brightest pixel
canvas.create_line(0, brightest_y, scaled_width, brightest_y, fill="red", width=2)  # Horizontal line
canvas.create_line(brightest_x, 0, brightest_x, scaled_height, fill="red", width=2)  # Vertical line

# Run the application
root.mainloop()
