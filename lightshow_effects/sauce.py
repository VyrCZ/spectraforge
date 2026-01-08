from modules.lightshow_effects import LightshowEffects, l_effect, namespace, CustomParamType
import modules.mathutils as mu
import colorsys
import math
import random
from modules.effect import EffectType

# Alias for brevity
Color = CustomParamType.Color

@namespace("sauce")
class SauceEffects(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)

    @l_effect(EffectType.UNIVERSAL)
    def sparkle(self, steps: int, color1: Color = Color.white, color2: Color = Color.white, bg_color: Color = Color.transparent, percentage: int = 50, seed: int = 12345):
        """
        Randomly selects a % of LEDs based on a seed and fades them from color1 to color2.
        """
        frames = []
        n_leds = len(self.coords)
        
        # 1. Setup deterministic random selection
        # We use a local Random instance to ensure the seed doesn't affect global state
        rng = random.Random(seed)
        
        num_active = int(n_leds * (max(0, min(100, percentage)) / 100))
        
        # Select random indices
        active_indices = set(rng.sample(range(n_leds), num_active))
        
        for step in range(steps):
            frame = [bg_color] * n_leds
            
            # Calculate fade progress (0.0 to 1.0)
            progress = step / (steps - 1) if steps > 1 else 1
            
            # Calculate the current color for the active LEDs
            # Unpacking tuples for mu.color_lerp compatibility as seen in your example
            lerp_color = mu.color_lerp(
                (color1[0], color1[1], color1[2], color1[3]), 
                (color2[0], color2[1], color2[2], color2[3]), 
                progress
            )
            
            for i in range(n_leds):
                if i in active_indices:
                    frame[i] = lerp_color
                else:
                    frame[i] = bg_color
            
            frames.append(frame)
            
        return frames