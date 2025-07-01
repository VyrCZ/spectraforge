from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time
import random
import colorsys

class IndependantRainbow(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords, "Chaos Rainbow", EffectType.UNIVERSAL)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 0.5, min=0.01, max=0.99, step=0.01)
        self.hue = [random.random() for _ in range(len(self.pixels))]

    def update(self):
        for i in range(len(self.pixels)):
            self.hue[i] += self.speed.get() / 100
            if self.hue[i] > 1:
                self.hue[i] -= 1
            normalized_rgb = list(colorsys.hsv_to_rgb(self.hue[i], 1, 1))
            self.pixels[i] = tuple([int(channel * 255) for channel in normalized_rgb])
        self.pixels.show()