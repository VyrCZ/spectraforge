from modules.effect import LightEffect, ParamType, EffectType
import math
import colorsys

class BreathingNebula(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Breathing Nebula", EffectType.UNIVERSAL)
        
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 3, min=1, max=50, step=1)
        self.cloud_scale = self.add_parameter("Cloud Scale", ParamType.SLIDER, 2.5, min=0.5, max=10.0, step=0.5)
        
        self.t = 0
        
        # Normalize Coords
        xs, ys, zs = zip(*coords)
        min_x, width = min(xs), (max(xs) - min(xs)) or 1
        min_y, height = min(ys), (max(ys) - min(ys)) or 1
        min_z, depth = min(zs), (max(zs) - min(zs)) or 1
        
        self.norm_coords = []
        for x, y, z in coords:
            self.norm_coords.append(((x-min_x)/width, (y-min_y)/height, (z-min_z)/depth))

    def update(self):
        self.t += self.speed.get() / 8000.0
        t = self.t
        scale = self.cloud_scale.get()

        for i, (nx, ny, nz) in enumerate(self.norm_coords):
            # Sum of Sines for noise
            n1 = math.sin(nx * scale + t)
            n2 = math.sin(ny * scale - t * 0.5)
            n3 = math.sin(nz * scale + t * 0.2)
            
            noise_val = (n1 + n2 + n3 + 3) / 6.0
            
            # Breathing pulse
            pulse = (math.sin(t * 2) + 1) / 2.0
            brightness = noise_val * (0.5 + 0.5 * pulse)
            
            # Color: Deep Blue to Pink
            hue = 0.6 + (noise_val * 0.3)
            
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, brightness)
            self.renderer[i] = (int(r * 255), int(g * 255), int(b * 255))
            
        self.renderer.show()