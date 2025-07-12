from modules.effect import LightEffect,ParamType, EffectType
import modules.mathutils as mu

class ColorSweep(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Color Wave", EffectType.UNIVERSAL)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 20, min=5, max=100, step=1)
        self.active_color = self.add_parameter("Active Color", ParamType.COLOR, "#FF0000")
        self.background_color = self.add_parameter("Background Color", ParamType.COLOR, "#000000")
        self.blend_factor = self.add_parameter("Blend Factor", ParamType.SLIDER, 0.5, min=0, max=1, step=0.01)
        self.current_y = 0
        self.current_dir = 1
        self.blend_range = self.height / 2

    def update(self):
        #print(f"Speed: {self.speed.get()}")
        self.current_y += 0.1 * self.current_dir * self.speed.get()

        # Reverse direction if reaching bounds
        if self.current_y > self.height:
            self.current_dir = -1
        if self.current_y < 0:
            self.current_dir = 1

        for i in range(len(self.renderer)):
            y_distance = abs(self.coords[i][1] - self.current_y)  # Distance from the current Y
            y_clamped = mu.clamp(y_distance, 0, self.height)  # Clamp to range
            blend_factor = mu.normalize(y_clamped, 0, self.height) / 4  # Normalize to [0, 1]
            
            if y_distance > self.blend_range:
                blend_factor = 1
            # Linear interpolation between active_color and background_color
            new_color = mu.color_lerp(self.active_color.get(), self.background_color.get(), blend_factor)
            self.renderer[i] = new_color  # Update specific point's color

        self.renderer.show()