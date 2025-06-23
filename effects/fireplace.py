from effects.base_effect import LightEffect, ParamType
import modules.mathutils as mu
import colorsys
import random

class Fireplace(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.color = self.add_parameter("Base Color", ParamType.COLOR, "#ffaa00")
        self.level = self.add_parameter("Level", ParamType.SLIDER, self.height / 2, min=0, max=self.height)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 0.2, min=0.1, max=0.5, step=0.05)
        self.amount = self.add_parameter("Particle Amount", ParamType.SLIDER, 10, min=1, max=10, step=1)
        self.hue = [0 for i in range(len(self.pixels))] # float showing the hue
        self.lights = [0 for i in range(len(self.pixels))] # float showing the brightness

    def update(self):
        top_distance = self.height - self.level.get()
        normalized_rgb = [channel / 255 for channel in self.color.get()]
        base_hue = colorsys.rgb_to_hsv(normalized_rgb[0], normalized_rgb[1], normalized_rgb[2])[0]
        max_particles = int(self.amount.get())  # Maximum allowed lit pixels
        active_particles = 0  # Counter for actively lit pixels

        turned_off_pixels = []
        weights = []
        for i in range(len(self.pixels)):
            if self.coords[i][2] > self.level.get() and self.lights[i] <= 0:
                turned_off_pixels.append(i)
                weights.append(1 / ((self.coords[i][2] - self.level.get()) ** 4))
        if len(turned_off_pixels) > 20:
            for i in random.choices(population=turned_off_pixels, weights=weights, k=int(self.amount.get())):
                self.hue[i] = base_hue - mu.lerp(0, 0.2, mu.clamp(mu.normalize(self.coords[i][2], self.level.get(), self.height) + random.uniform(-0.1, 0.1), 0, 1))
                self.lights[i] = random.uniform(0.7, 1)


        # Handle pixels
        for i in range(len(self.pixels)):
            if self.coords[i][2] > self.level.get():
                # Count actively lit pixels
                if self.lights[i] > 0:
                    active_particles += 1
                    self.lights[i] -= self.speed.get() / 20
                    if self.lights[i] < 0:
                        self.lights[i] = 0

                # Set pixel color
                new_color = tuple(mu.clamp(int(channel * 255), 0, 255) for channel in colorsys.hsv_to_rgb(self.hue[i], 1, self.lights[i]))
                self.pixels[i] = new_color
            else:
                # Set pixels below self.level to base color
                self.hue[i] = base_hue
                self.lights[i] = 1  # Full brightness
                new_color = tuple(int(channel * 255) for channel in colorsys.hsv_to_rgb(base_hue, 1, 1))
                self.pixels[i] = new_color

        # Update the LED strip
        self.pixels.show()


