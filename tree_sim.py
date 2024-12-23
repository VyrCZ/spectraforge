import pyvista as pv
import numpy as np
import time
import math
from scipy.spatial import distance

class Simulation:
    def get_points(self, n, height, diameter):
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
        return self.find_shortest_path(points)
    
    def path_length(path):
        return sum(distance.euclidean(path[i], path[i + 1]) for i in range(len(path) - 1))

    # Define the function to find the shortest path
    def find_shortest_path(self, points):
        # Find the point with the lowest Z coordinate
        start_index = min(range(len(points)), key=lambda i: points[i][2])
        remaining = set(range(len(points)))
        remaining.remove(start_index)
        
        # Start the path with the lowest Z point
        path_indices = [start_index]
        
        # Nearest neighbor greedy approach
        while remaining:
            last = path_indices[-1]
            next_index = min(remaining, key=lambda i: distance.euclidean(points[last], points[i]))
            path_indices.append(next_index)
            remaining.remove(next_index)
        
        # Create the ordered list of points
        ordered_points = [points[i] for i in path_indices]
        ordered_points.append(points[start_index])  # Return to start
        
        return ordered_points


    def __init__(self):
        self.height = 2.4
        self.diameter = 1.5
        self.points = self.get_points(200, self.height, self.diameter)
        self.num_points = len(self.points)

        # Initialize colors as white (RGB: [255, 255, 255])
        self.colors = [[0, 0, 0] for _ in self.points]

        # Create a PyVista point cloud
        self.cloud = pv.PolyData(self.points)
        self.cloud['colors'] = np.array(self.colors, dtype=np.uint8)

        # Plot the point cloud
        self.plotter = pv.Plotter()
        self.plotter.background_color = "black"
        self.actor = self.plotter.add_points(self.cloud, scalars='colors', rgb=True)
        self.plotter.show(interactive_update=True)  # Enable interactive updates

        # Function to update colors dynamically
    def update_colors(self):
        self.cloud['colors'] = np.array(self.colors, dtype=np.uint8)
        self.plotter.update_scalars(self.cloud['colors'])  # Efficiently update colors
        self.plotter.update()  # Redraw the scene