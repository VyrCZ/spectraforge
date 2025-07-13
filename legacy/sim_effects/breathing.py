import numpy as np
import time
import math
import random
import sys
import os
import asyncio
# add parent directory to python path so I can import my scripts from inside of a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import modules.mathutils as mu
import legacy.tree_sim as tree_sim

class Breathing(tree_sim.Simulation):
    """
    Random flashing between selected colors
    """
    def __init__(self):
        super().__init__() # don't forget to call the parent's init
        # define config variables
        self.fade_speed = 0.025
        self.t = 0
        self.dir = 1
        self.color = [255, 0, 0]
        self.off_time = 0.5

    async def update(self):
        # change the colors, update the tree
        self.t += self.dir * self.fade_speed
        if self.t >= 1:
            self.dir = -1
        elif self.t <= 0:
            self.dir = 1
            await asyncio.sleep(self.off_time)
        for i in range(self.num_points):
            self.colors[i] = [int(channel * self.t) for channel in self.color]
        self.update_colors()

lights = Breathing()
while True:
    asyncio.run(lights.update())
    time.sleep(0.1)  # Regulate speed of the effect