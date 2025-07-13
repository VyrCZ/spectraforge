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
import modules.mathutils as mu
import legacy.tree_sim as tree_sim

class Effects(tree_sim.Simulation):
    """
    Small effects made for a lightshow to the song "Centipede" by Knife Party
    BPM: 140
    """
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
                new_color = [channel * (1 - mu.normalize(mu.clamp(abs(self.points[i][2] - self.current_z), 0, self.height/8), 0, self.height/8)) for channel in color]
                self.colors[i] = new_color  # Update specific point's color
            self.update_colors()
            await asyncio.sleep(length / steps)


    def update(self):
        for i in range(self.num_points):
            self.colors[i] = random.choice(self.color_bank)

        self.update_colors()

pygame.mixer.init()
pygame.mixer.music.load("centipede.ogg")
pygame.mixer.music.set_volume(0.1)

lights = Effects()
async def perform():
    if(pygame.mixer.music.get_pos() > 0):
        while True:
            await asyncio.sleep(0.719)
            await lights.swoop((1 / (140 / 60)), [255, 255, 255], True)

    # Add timestamps and corresponding functions with arguments
events = [
    (0.55, lights.swoop, [0.2, [255, 255, 255], True]),
    (0.9, lights.swoop, [0.2, [255, 255, 255], True]),
]

# Sort events by timestamp
events.sort(key=lambda x: x[0])

async def play_music():
    """Play music using pygame mixer."""
    pygame.mixer.music.play()

async def track_events():
    """Track and execute events at specified times based on music playback."""
    executed = set()  # Keep track of executed events

    while pygame.mixer.music.get_busy():
        current_pos = pygame.mixer.music.get_pos() / 1000  # Convert to seconds

        for timestamp, func, args in events:
            if timestamp <= current_pos and timestamp not in executed:
                print(f"Running event {timestamp:.3f} at {pygame.mixer.music.get_pos() / 1000:.3f}")
                await func(*args)
                executed.add(timestamp)

        await asyncio.sleep(0.1)  # Small delay to reduce CPU usage

async def main():
    """Main coroutine to manage music playback and event tracking."""
    await asyncio.gather(play_music(), track_events())

# Run the asyncio event loop
asyncio.run(main())

# Wait for the song to finish playing
while pygame.mixer.music.get_busy():
    pygame.time.wait(100)

pygame.mixer.quit()