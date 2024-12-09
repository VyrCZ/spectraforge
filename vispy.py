import pyvista as pv
import numpy as np
import time
import math

def lerp(a, b, t):
    return (1 - t) * a + t * b

def normalize(value, old_min, old_max):
    if old_min == old_max:
        raise ValueError("old_min and old_max cannot be the same.")
    return (value - old_min) / (old_max - old_min)

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def generate_points_in_cone(n, height, diameter):
    points = []
    radius_at_base = diameter / 2

    for _ in range(n):
        # Random height between 0 and the cone height
        z = np.random.uniform(0, height)

        # The radius at the current height is scaled linearly with height
        radius_at_z = radius_at_base * (1 - z / height)

        # Randomly choose a point within the circle at this radius
        r = np.random.uniform(0, radius_at_z)
        theta = np.random.uniform(0, 2 * np.pi)

        # Convert polar coordinates to Cartesian coordinates
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Append the 3D point to the list
        points.append((float(x), float(y), float(z)))

    return points


# Generate points and initialize colors
height = 2.4
diameter = 1.5
points = generate_points_in_cone(200, height, diameter)
num_points = len(points)

# Initialize colors as white (RGB: [255, 255, 255])
colors = np.ones((num_points, 3)) * 255  # All points white initially

# Create a PyVista point cloud
cloud = pv.PolyData(points)
cloud['colors'] = colors.astype(np.uint8)  # Set initial colors to white

# Plot the point cloud
plotter = pv.Plotter()
plotter.background_color = "black"
actor = plotter.add_points(cloud, scalars='colors', rgb=True)
plotter.show(interactive_update=True)  # Enable interactive updates

# Function to update colors dynamically
def update_colors():
    for i in range(num_points):
        # Example: Assign random color to each point
        new_color = np.random.randint(0, 256, size=3)  # Random RGB
        colors[i] = new_color  # Update specific point's color

    cloud['colors'] = colors.astype(np.uint8)  # Update color data
    plotter.update_scalars(cloud['colors'])  # Efficiently update colors
    plotter.update()  # Redraw the scene

current_z = 0
current_dir = 1 # 1 for up, -1 for down
# Function to update colors dynamically
def color_line():
    global current_z, current_dir
    current_z += 0.1 * current_dir
    if current_z > height:
        current_dir = -1
    if current_z < 0:
        current_dir = 1
    for i in range(num_points):
        # Example: Assign random color to each point
        new_color = [255, 0, 0]
        # new_color[1] -> Z position same as current_z = 0; Z distance from current_z same as height = 125
        new_color[0] = lerp(0, 255, 1 - normalize(clamp(abs(points[i][2] - current_z), 0, height/2), 0, height/2))
        colors[i] = new_color  # Update specific point's color

    cloud['colors'] = colors.astype(np.uint8)  # Update color data
    plotter.update_scalars(cloud['colors'])  # Efficiently update colors
    plotter.update()  # Redraw the scene


# Simulate periodic updates
while True:
    color_line()
    time.sleep(0.1)  # Pause for a short time to visualize changes
plotter.close()

