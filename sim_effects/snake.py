import numpy as np
import time
import math
import random
import sys
import os
# add parent directory to path so I can import my scripts from a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import modules.mathutils as mu
import modules.tree_sim as tree_sim

class SnakeLight(tree_sim.Simulation):
    """
    This one is ass because it was made by gpt lol
    """
    def __init__(self, snake_length):
        super().__init__()
        self.snake_length = snake_length
        self.snake = [0]  # Initialize the snake starting at the first point
        self.color_head = [255, 0, 0]  # Head of the snake (red)
        self.color_body = [0, 255, 0]  # Body of the snake (green)

    def find_nearest_point(self, current_index):
        """Find the nearest point to the current snake head that is not already in the snake."""
        current_point = self.points[current_index]
        min_distance = float('inf')
        nearest_point = None
        
        for i, point in enumerate(self.points):
            if i in self.snake:
                continue
            distance = math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(current_point, point)))
            if distance < min_distance:
                min_distance = distance
                nearest_point = i
        
        return nearest_point

    def update(self):
        # Move the snake head to a new point
        new_head = self.find_nearest_point(self.snake[-1])
        if new_head is not None:
            self.snake.append(new_head)
        
        # Trim the snake to the specified length
        if len(self.snake) > self.snake_length:
            self.snake.pop(0)
        
        # Update colors based on the snake
        self.colors = [[50, 50, 50] for _ in self.points]
        for i, index in enumerate(self.snake):
            if i == len(self.snake) - 1:  # Head of the snake
                self.colors[index] = self.color_head
            else:  # Body of the snake
                self.colors[index] = self.color_body
        
        self.update_colors()

# Example usage
snake_length = 10
lights = SnakeLight(snake_length)
while True:
    lights.update()
    time.sleep(0.1)  # Pause for a short time to visualize changes
