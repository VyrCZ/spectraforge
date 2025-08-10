from modules.effect import LightEffect,ParamType, EffectType
import modules.mathutils as mu

class ColorSweep(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Color Wave", EffectType.UNIVERSAL)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 100, min=30, max=200, step=1)
        self.active_color = self.add_parameter("Active Color", ParamType.COLOR, "#FF0000")
        self.background_color = self.add_parameter("Background Color", ParamType.COLOR, "#000000")
        self.bounce = self.add_parameter("Bounce", ParamType.CHECKBOX, True)
        self.width = self.add_parameter("Width", ParamType.SLIDER, 50, min=5, max=50, step=1) # Width of the wave, % of the height
        self.current_y = 0
        self.current_dir = 1
        self.max_y = max(coord[1] for coord in coords)
        self.min_y = min(coord[1] for coord in coords)

    def update(self):
        #print(f"Speed: {self.speed.get()}")
        self.current_y += 10 * self.current_dir * self.speed.get() / self.height
        total_height = self.max_y - self.min_y
        wave_width = self.width.get() / 100 * total_height

        if self.bounce.get():
            # Bounce: Reverse direction if reaching bounds
            if self.current_y > self.max_y + wave_width * 0.2:
                self.current_dir = -1
            if self.current_y < self.min_y - wave_width * 0.2:
                self.current_dir = 1
        else:
            # Not bounce: wrap around instead
            if self.current_y > self.max_y + wave_width:
                self.current_y -= total_height
            elif self.current_y < self.min_y - wave_width:
                self.current_y += total_height

        for i in range(len(self.renderer)):
            y = self.coords[i][1]
            
            # Calculate direct distance
            y_distance = abs(y - self.current_y)

            if not self.bounce.get():
                # Calculate wrapped distance and take the minimum
                wrapped_dist = min(abs(y - (self.current_y - total_height)), abs(y - (self.current_y + total_height)))
                y_distance = min(y_distance, wrapped_dist)

            if y_distance > wave_width:
                ratio = 1
            else:
                # calculate % of distance from the current Y to the height
                ratio = y_distance / wave_width

            # Linear interpolation between active_color and background_color
            new_color = mu.color_lerp(self.active_color.get(), self.background_color.get(), ratio)
            self.renderer[i] = new_color  # Update specific point's color

        self.renderer.show()