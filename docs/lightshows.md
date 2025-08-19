# Lightshows
Lightshows are a list of effects that are played at specific times, allowing you to sync them to music. You can put individual effects on a timeline, set their start & end points and set their parameters. There is support for multiple layers, so you can stack effects on top of each other and utilize transparency of parts of the effects to create more complex visuals.

## Lightshow effects
Every effect you want to use must be imported in a script to the directory `lightshow_effects/`. Each effect will be shown in the app with the namespace set in the script. When you use custom effects, you must send them with the lightshow file, so the app can load them.

## Creating a lightshow
The editor is not ready yet, but it's coming soon™! *(For now, you can create a lightshow the legacy way using audacity labels with a select few effects. You can view the lightshows created in the `legacy/lightshow/labels/` directory for reference.)*

## Creating lightshow effects
To create a lightshow effect, you must create a class that inherits from `LightshowEffects` imported from `modules.lightshow_effects`. You can use the `@l_effect` decorator with the `EffectType` parameter to register each effect, which will be shown in the app. The effect must return a list of frames, where each frame is a list of colors (RGB in range 0-255).

### Available values:
Look at [effects.md](docs/effects.md) for more information on how to create effects.
- `self.coords[list]` - list of pixel coordinates in the 3D space
- `self.bounds[mathutils.Bounds]` - min and max XYZ coordinates of the lights

Example:
```python
from modules.lightshow_effects import *
import modules.mathutils as mu
from modules.effect import EffectType

@namespace("example")
class ExampleEffects(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)

    @l_effect(EffectType.UNIVERSAL)  # works for 2D and 3D
    def color_pulse(self, steps, color, repeats=1):
        """
        Simple pulse: all LEDs fade from off to color and back.
        - steps: frames per beat (one up-and-down cycle)
        - color: target RGB tuple, e.g. (255, 0, 0)
        - repeats: how many cycles to generate
        """
        frames = []
        for _ in range(repeats):
            for step in range(steps):
                t = step / max(1, steps - 1)
                # ping-pong value from 0 -> 1 -> 0
                intensity = 1 - abs(2 * t - 1)
                frame_color = mu.color_lerp((0, 0, 0), color, intensity)
                frame = [frame_color for _ in self.coords]
                frames.append(frame)
        return frames
```