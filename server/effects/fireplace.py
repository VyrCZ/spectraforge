from effects.base_effect import LightEffect, ParamType
import mathutils as mu
import colorsys
import random

class Fireplace(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.color = self.add_parameter("Base Color", ParamType.COLOR, "#ffaa00")
        self.level = self.add_parameter("Level", ParamType.SLIDER, self.height / 2, min=0, max=self.height)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 1, min=0.1, max=0.5, step=0.05)
        self.amount = self.add_parameter("Particle Amount", ParamType.SLIDER, 10, min=1, max=30, step=1)
        self.hue = [0 for i in range(len(self.pixels))] # float showing the hue
        self.lights = [0 for i in range(len(self.pixels))] # float showing the brightness
    def update(self):
        top_distance = self.height - self.level.get()
        base_hue = colorsys.rgb_to_hsv(self.color.get() / 255)[0]
        suitable_particles = []
        for i in range(len(self.pixels)):
            if self.coords[i][2] > self.level.get() and self.lights[i] <= 0:
                suitable_particles.append(i)
        for led in random.choices(suitable_particles, k=int(self.amount.get())):
            self.lights[led] = 1
            self.hue[led] = base_hue + random.uniform(-0.1, 0.1)
        for i in range(len(self.pixels)):
            if self.lights[i] > 0:
                self.lights[i] -= self.speed.get()
            if self.coords[i][2] < self.level.value:
                self.lights[i] = 1
                self.pixels[i] = self.color.get()
            self.pixels[i] = (channel * 255 for channel in colorsys.hsv_to_rgb(self.hue[i], 1, self.lights[i]))
        self.pixels.show()