from effects.base_effect import LightEffect
import mathutils as mu

class ColorSweep(LightEffect):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.speed = self.add_parameter("Speed", "slider", 20, min=5, max=50, step=1)
        self.active_color = self.add_parameter("Active Color", "color", "#FF0000")
        self.background_color = self.add_parameter("Background Color", "color", "#000000")
        self.current_z = 0
        self.current_dir = 1

    def update(self):
        self.current_z += 0.1 * self.current_dir

        # Reverse direction if reaching bounds
        if self.current_z > self.height:
            self.current_dir = -1
        if self.current_z < 0:
            self.current_dir = 1

        for i in range(len(self.pixels)):
            z_distance = abs(self.coords[i][2] - self.current_z)  # Distance from the current Z
            z_clamped = mu.clamp(z_distance, 0, self.height)  # Clamp to range
            blend_factor = mu.normalize(z_clamped, 0, self.height)  # Normalize to [0, 1]

            # Linear interpolation between active_color and background_color
            new_color = [
                mu.lerp(self.active_color.get()[0], self.background_color.get()[0], blend_factor),
                mu.lerp(self.active_color.get()[1], self.background_color.get()[1], blend_factor),
                mu.lerp(self.active_color.get()[2], self.background_color.get()[2], blend_factor)
            ]
            self.pixels[i] = new_color  # Update specific point's color

        self.pixels.show()