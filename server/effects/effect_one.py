from effects.base_effect import LightEffect

class EffectOne(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.speed = self.add_parameter("Speed", "slider", 0.5, min=0, max=1, step=0.1)
        self.color = self.add_parameter("Color", "color", "#FF0000")
        self.reverse = self.add_parameter("Reverse", "checkbox", False)

    def update(self):
        print("EffectOne update")
        for i in range(len(self.pixels)):
            index = i if not self.reverse.get() else len(self.pixels) - i - 1
            self.pixels[index] = self.color.get()
        self.pixels.show()