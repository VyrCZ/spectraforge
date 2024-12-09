import numpy as np
import time
import math
import random
import asyncio
import pygame
import sys
import os
# add parent directory to path so I can import my scripts from a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mathutils import *
import tree_sim

class Effects(tree_sim.Simulation):
    def __init__(self):
        super().__init__()
        self.color_bank = [
            [255, 0, 0],
            [0, 255, 0]
        ]

    async def swoop(self, length, color, is_up):
        # Swoop up or down
        steps = 20
        self.current_z = 0
        while self.current_z < self.height:
            self.current_z += self.height / steps
            for i in range(self.num_points):
                new_color = [channel * (1 - normalize(clamp(abs(self.points[i][2] - self.current_z), 0, self.height/8), 0, self.height/8)) for channel in color]
                self.colors[i] = new_color  # Update specific point's color
            self.update_colors()
            await asyncio.sleep(length / steps)


    def update(self):
        for i in range(self.num_points):
            self.colors[i] = random.choice(self.color_bank)

        self.update_colors()

async def setup():
    pygame.mixer.init()
    pygame.mixer.music.load("centipede.ogg")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play()
    await asyncio.sleep(1)

lights = Effects()
async def perform():
    if(pygame.mixer.music.get_pos() > 0):
        while True:
            await asyncio.sleep(0.719)
            await lights.swoop((1 / (140 / 60)), [255, 255, 255], True)
    
if __name__ == "__main__":
    asyncio.run(setup())
    asyncio.run(perform())