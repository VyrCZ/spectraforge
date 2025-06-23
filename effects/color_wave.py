from effects.base_effect import LightEffect, ParamType
import modules.mathutils as mu

class ColorSweep(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 20, min=5, max=100, step=1)
        self.active_color = self.add_parameter("Active Color", ParamType.COLOR, "#FF0000")
        self.background_color = self.add_parameter("Background Color", ParamType.COLOR, "#000000")
        self.blend_factor = self.add_parameter("Blend Factor", ParamType.SLIDER, 0.5, min=0, max=1, step=0.01)
        self.current_z = 0
        self.current_dir = 1
        self.blend_range = self.height / 2

    def update(self):
        #print(f"Speed: {self.speed.get()}")
        self.current_z += 0.1 * self.current_dir * self.speed.get()

        # Reverse direction if reaching bounds
        if self.current_z > self.height:
            self.current_dir = -1
        if self.current_z < 0:
            self.current_dir = 1

        for i in range(len(self.pixels)):
            z_distance = abs(self.coords[i][2] - self.current_z)  # Distance from the current Z
            z_clamped = mu.clamp(z_distance, 0, self.height)  # Clamp to range
            blend_factor = mu.normalize(z_clamped, 0, self.height) / 4  # Normalize to [0, 1]
            
            if z_distance > self.blend_range:
                blend_factor = 1
            # Linear interpolation between active_color and background_color
            new_color = mu.color_lerp(self.active_color.get(), self.background_color.get(), blend_factor)
            self.pixels[i] = new_color  # Update specific point's color

        self.pixels.show()