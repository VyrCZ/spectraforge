from effects.base_effect import LightEffect

class EffectTwo(LightEffect):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.brightness = self.add_parameter("Brightness", "slider", 0.5, min=0, max=1, step=0.1)

    def update(self):
        brightness = int(self.brightness.get() * 255)
        brightness = max(0, min(brightness, 255))
        for i in range(len(self.pixels)):
            self.pixels[i] = (brightness, brightness, brightness)
        self.pixels.show()
