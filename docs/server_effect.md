# Light effect for server documentation
All effect must be in the server/effects folder (restart the server script after adding effects)

# Simple example (effects/static_color.py)
```python
from effects.base_effect import LightEffect, ParamType

class StaticColor(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")

    def update(self):
        self.pixels.fill(self.color.get())
        self.pixels.show()
```
All connected LEDs are set to a specified color

# Required structure
An effect class that is inheriting `LightEffect` from effects/base_effect.py with a unique name.
The class must require two parameters - pixels, coords and must call the base init
The class must contain an update function, which is called in a loop - you define your effects here

# Avaliable values
- pixels - list of connected LEDs (see NeoPixel documentation for more info) - set colors for individual pixels here (format (R, G, B) tuple)
- coords - list of pixel coordinates in the 3D space (allowing space-aware effects)
- height - the Z coordinate of the highest placed LED in the 3D space

# Parameters
Each effect can easily set its own parameters, which are shown in the app. Parameter values are persistent.

```python
from effects.base_effect import LightEffect, ParamType

class ParameterShowcase(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        # init parameters
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 2, min=1, max=10, step=1)
        self.reverse = self.add_parameter("Reverse", ParamType.CHECKBOX, False)
        self.text = self.add_parameter("Text", ParamType.VALUE, "")

        # get values
        print(f"The lights are shining with color {self.color.get()} and changing with speed {self.speed.get()}")
```

## functions:
`base_effect.LightEffect.add_parameter(name: str, ParamType, default_value, **cwargs) => base_effect.Parameter`
Creates a parameter, which is shown in the app.

`base_effect.Parameter.get() => (ParamType specific)`
Returns the value of parameter set from the app.

## ParamTypes:
`ParamType.SLIDER(min, max, step) => float` - shows a slider, allowing to set a numeric value. Use `step=1; int(parameter.get())` for int values.

`ParamType.COLOR() => tuple[r,g,b]` - Shows a color picker made using iro.js. **DEFAULT VALUE IS SET IN HEX, but returns 8-bit RGB tuple.**

`ParamType.CHECKBOX() => bool` Shows a simple checkbox.

`ParamType.VALUE() => str` Shows an input field.