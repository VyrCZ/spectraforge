from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import math
import random
import colorsys

class Grow(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Grow", EffectType.UNIVERSAL)
        self.active_color = None
        self.growing = False
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 10, min=1, max=100, step=1)
        self.reset()

    def reset(self):
        self.growing = not self.growing
        if self.growing:
            self.active_color = tuple([int(channel * 255) for channel in colorsys.hsv_to_rgb(random.random(), 1, 1)])
        self.random_point = random.choice(self.coords)
        self.current_size = 0 if self.growing else 800

    def update(self):
        self.current_size += self.speed.get() / 30 if self.growing else -self.speed.get() / 30
        if self.current_size >= 800 or self.current_size <= 0:
            self.reset()
        if self.current_size <= 0:
            self.current_size = 0.1
        self.current_size = round(self.current_size, 1)
        for i in range(len(self.renderer)):
            active_color = [channel * (1 - mu.normalize(mu.clamp(abs(math.dist(self.coords[i], self.random_point)), 0, self.current_size), 0, self.current_size)) for channel in self.active_color]
            #print(f"Active color: {active_color}")
            self.renderer[i] = active_color  # Update specific point's color
        self.renderer.show()