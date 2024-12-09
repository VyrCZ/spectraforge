import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_sphere(ax, center, width, height, depth):
    """
    Plot a sphere on the given 3D axes.

    Parameters:
        ax (Axes3D): The 3D axes to plot on.
        center (tuple): The (x, y, z) center of the sphere.
        width (float): The width (along x-axis) of the sphere.
        height (float): The height (along z-axis) of the sphere.
        depth (float): The depth (along y-axis) of the sphere.
    """
    # Generate sphere coordinates
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = width * np.outer(np.cos(u), np.sin(v)) / 2 + center[0]
    y = depth * np.outer(np.sin(u), np.sin(v)) / 2 + center[1]
    z = height * np.outer(np.ones(np.size(u)), np.cos(v)) / 2 + center[2]

    # Plot the surface
    ax.plot_surface(x, y, z, color='green', alpha=0.3, edgecolor='k')

# Function to calculate sphere from point boundaries
def sphere_from_points(ax, points):
    """
    Create a sphere from the boundary points of a list of coordinates.

    Parameters:
        ax (Axes3D): The 3D axes to plot on.
        points (list): List of (x, y, z) tuples.

    Returns:
        None
    """
    # Extract boundaries
    min_x, max_x = min(p[0] for p in points), max(p[0] for p in points)
    min_y, max_y = min(p[1] for p in points), max(p[1] for p in points)
    min_z, max_z = min(p[2] for p in points), max(p[2] for p in points)
    
    # Calculate center and dimensions
    center = ((max_x + min_x) / 2, (max_y + min_y) / 2, (max_z + min_z) / 2)
    width = max_x - min_x
    depth = max_y - min_y
    height = max_z - min_z

    # Plot the sphere
    plot_sphere(ax, center, width, height, depth)


# List of 3D coordinates
coordinates = [(3296, 1996, 966), (930, 1996, 964), (2116, 2986, 432), (2112, 790, 1264), (2602, 1472, 1376), (2296, 2402, 1848), (1810, 1658, 1392), (2768, 2038, 1738), (1868, 2372, 1700)]
labels = ["left", "right", "bottom", "top", 'Koule', 'Knot', 'Bila vec', "svicen vpravo", "svicen vlevo"]  # Define labels for the points

# Extract x, y, and z coordinates from the list
x = [coord[0] for coord in coordinates]
y = [coord[1] for coord in coordinates]
z = [coord[2] for coord in coordinates]

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the coordinates
ax.scatter(x, y, z)

# Add labels to each point
for i in range(len(coordinates)):
    ax.text(x[i], y[i], z[i], labels[i], fontsize=10, color='red')

# Set labels for the axes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

sphere_from_points(ax, coordinates[:4])

# Show the plot
plt.show()
