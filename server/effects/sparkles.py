from effects.base_effect import LightEffect
import mathutils as mu
import time
import random

class Sparkles(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.color = self.add_parameter("Color", "color", "#FF0000"),
        self.speed = self.add_parameter("Speed", "slider", 0.5, min=0.01, max=0.9, step=0.01)
        self.amount = self.add_parameter("Amount", "slider", 1, min=1, max=10, step=1)
        self.states = [0] * len(self.pixels)

    def update(self):
        off_lights = [j for j in range(len(self.pixels)) if self.states[j] == 0]
        # randomly select amount lights to turn on (state = 1)
        for led in random.sample(off_lights, self.amount.get()):
            self.states[led] = 1
        for i in range(len(self.pixels)):
            if self.states[i] > 0:
                self.states[i] -= self.speed.get()
            if self.states[i] < 0:
                self.states[i] = 0
            self.pixels[i] = [channel * self.states[i] for channel in self.color[0].get()]
        
            