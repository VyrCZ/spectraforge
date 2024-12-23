from effects.base_effect import LightEffect
import mathutils as mu

class ColorSweep(LightEffect):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.speed = self.add_parameter("Speed", "slider", 0.2, min=0.1, max=1, step=0.1)
        self.color = self.add_parameter("Color", "color", "#FF0000")
        self.falloff = self.add_parameter("Falloff", "slider", 10, min=1, max=50, step=1)
        self.current_pixel = self.falloff

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
                mu.lerp(self.active_color[0], self.background_color[0], blend_factor),
                mu.lerp(self.active_color[1], self.background_color[1], blend_factor),
                mu.lerp(self.active_color[2], self.background_color[2], blend_factor)
            ]
            self.pixels[i] = new_color  # Update specific point's color

        self.pixels.show()