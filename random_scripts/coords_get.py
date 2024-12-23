from tkinter import Tk, Canvas
from PIL import Image, ImageTk

def on_click(event):
    # Get the coordinates of the click and scale them back up
    x, y = int(event.x / scale), int(event.y / scale)
    print(f"({x}, {y})")
    
    # Draw the cross on the scaled image
    scaled_x, scaled_y = event.x, event.y
    canvas.create_line(0, scaled_y, scaled_width, scaled_y, fill="red", width=2)  # Horizontal line
    canvas.create_line(scaled_x, 0, scaled_x, scaled_height, fill="red", width=2)  # Vertical line

# Load the image
image_path = "images/side.jpg"
image = Image.open(image_path)

# Scale factor (e.g., 0.5 to reduce to half size)
scale = 0.5
scaled_width, scaled_height = int(image.width * scale), int(image.height * scale)

# Resize the image
image = image.resize((scaled_width, scaled_height), Image.ANTIALIAS)

# Create a GUI window
root = Tk()
root.title("Image Click Coordinates")

# Convert the image for Tkinter compatibility
tk_image = ImageTk.PhotoImage(image)

# Create a canvas to display the image
canvas = Canvas(root, width=scaled_width, height=scaled_height)
canvas.pack()

# Add the image to the canvas
canvas.create_image(0, 0, anchor="nw", image=tk_image)

# Bind the mouse click event to the canvas
canvas.bind("<Button-1>", on_click)

# Run the application
root.mainloop()
