import numpy as np
import time
import math
import random
import sys
import os
# add parent directory to python path so I can import my scripts from inside of a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import modules.mathutils as mu
import legacy.tree_sim as tree_sim

class Flashy(tree_sim.Simulation):
    """
    Random flashing between selected colors
    """
    def __init__(self):
        super().__init__() # don't forget to call the parent's init
        # define config variables
        self.current_point = 0
        self.trail_length = 10
        self.color = [255, 0, 0]

    def update(self):
        self.current_point += 1
        # reset colors
        self.colors = [[0, 0, 0] for _ in range(self.num_points)]
        for i in range(self.trail_length):
            self.colors[(self.current_point - i) % self.num_points] = [int(channel * (1 - i / self.trail_length)) for channel in self.color]
        self.update_colors()

lights = Flashy()
while True:
    lights.update()
    time.sleep(0.05)  # Regulate speed of the effect