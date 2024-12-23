from effects.base_effect import LightEffect

class EffectOne(LightEffect):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.speed = self.add_parameter("Speed", "slider", 0.5, min=0, max=1, step=0.1)
        self.color = self.add_parameter("Color", "color", "#FF0000")
        self.reverse = self.add_parameter("Reverse", "checkbox", False)

    def update(self):
        print("EffectOne update")
        color = tuple(int(self.color.get()[i : i + 2], 16) for i in (1, 3, 5))
        for i in range(len(self.pixels)):
            index = i if not self.reverse.get() else len(self.pixels) - i - 1
            self.pixels[index] = color
        self.pixels.show()