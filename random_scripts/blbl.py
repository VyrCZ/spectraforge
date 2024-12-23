import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

# Specify the image path
image_path = "path_to_your_image.jpg"  # Change to your image path

def draw_circle(canvas, color, pos, radius):
    """
    Draws a circle on the canvas.

    :param canvas: The canvas where the circle is drawn.
    :param color: The color of the circle.
    :param pos: A tuple (x, y) for the circle's center position.
    :param radius: The radius of the circle.
    """
    x, y = pos
    canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius, fill=color, outline=color
    )

def main():
    # Initialize the main Tkinter window
    root = tk.Tk()
    root.title("Image and Circle Drawer")

    # Load and display the image
    image = Image.open(image_path)
    tk_image = ImageTk.PhotoImage(image)
    canvas = Canvas(root, width=image.width, height=image.height)
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=tk_image)

    # Draw a circle on the canvas
    draw_circle(canvas, color="red", pos=(100, 100), radius=50)  # Example circle

    root.mainloop()

if __name__ == "__main__":
    main()
