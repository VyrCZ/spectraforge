from effects.base_effect import LightEffect
import mathutils as mu
import time
import random

class IndependantRainbow(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.speed = self.add_parameter("Speed", "slider", 0.5, min=0.01, max=0.99, step=0.01)
        self.hue = [random.random() for _ in range(len(self.pixels))]

    def update(self):
        for i in range(len(self.pixels)):
            self.hue[i] += self.speed.get()
            if self.hue[i] > 1:
                self.hue[i] -= 1
            self.pixels[i] = mu.hsv_to_rgb(self.hue[i], 1, 1)
        self.pixels.show()