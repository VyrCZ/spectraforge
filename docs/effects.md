# Effects
All effect must be in the effects folder. Restart the server to load new effects or use the sandbox mode for hot reloading.

## Example (effects/breathing.py)
```python
from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time

class Breathing(LightEffect):
    def __init__(self, renderer, coords):
        # Init the effect
        super().__init__(renderer, coords, "Breathing", EffectType.UNIVERSAL)
        # Parameters will work in sandbox, however only the default values will be used and can't be changed at the moment
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 50, min=1, max=500, step=1)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.off_time = 0.5 # Time to wait when the effect is fully faded out
        self.t = 0 # The timer variable
        self.dir = 1 # Direction of the breathing effect (1 for fading in, -1 for fading out)

    def update(self):
        # Update the time variable
        self.t += self.dir * self.fade_speed.get() / 10000
        # Change direction if the breathing effect is fully faded in or out
        if self.t >= 1:
            self.dir = -1
        elif self.t <= 0:
            self.dir = 1
            time.sleep(self.off_time)
        # Update the leds and the renderer
        for i in range(len(self.renderer)):
            self.renderer[i] = [mu.clamp(int(channel * self.t), 0, 255) for channel in self.color.get()]
        self.renderer.show()
```

## Required structure
An effect class that is inheriting `LightEffect` imported from modules.effect with a unique name.
The class must require two parameters - pixels, coords and must call the super's init
The class must contain an update() function, which is called every frame. You should make the effect behaviour here.

## Considerations
*Don't forget about the following:*
- You need to manually call `self.renderer.show()` to update the lights.
- The `coords` list can be made of any values, so don't assume that they are only positive. You should also use ratios for things like speed and distance, as the coordinates can be in any range. (I usually divide by the height)

## Available values
- `self.renderer[LEDRenderer]` - list of connected LEDs (wrapper of NeoPixel's pixels) - set colors for individual pixels here (format (R, G, B) tuple)
- `self.coords[list]` - list of pixel coordinates in the 3D space
- `self.bounds[mathutils.Bounds]` - min and max XYZ coordinates of the light coordinates
- *(legacy, use `self.bounds` instead) `self.height[float]` - height of the lights in the Y axis (max Y - min Y)*

## Parameters
Each effect can easily set its own parameters, which are shown in the app. Parameter values are persistent. Look at the example above for more info.

### functions:
`base_effect.LightEffect.add_parameter(name: str, ParamType, default_value, **cwargs) => base_effect.Parameter`
Creates a parameter, which is shown in the app.

`base_effect.Parameter.get() => (ParamType specific)`
Returns the value of parameter set from the app.

### ParamTypes:
`ParamType.SLIDER(min, max, step) => float` - shows a slider, allowing to set a numeric value. Use `step=1; int(parameter.get())` for int values.

`ParamType.COLOR() => tuple[r,g,b]` - Shows a color picker made using iro.js. **DEFAULT VALUE IS SET IN HEX, but returns 8-bit RGB tuple.**

`ParamType.CHECKBOX() => bool` Shows a simple checkbox.

`ParamType.VALUE() => str` Shows an input field.