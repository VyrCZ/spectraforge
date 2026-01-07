from modules.lightshow_effects import LightshowEffects, l_effect, namespace, CustomParamType
import modules.mathutils as mu
import colorsys
import math
import random
from modules.effect import EffectType

# not typing CustomParamType.Color 100 times
Color = CustomParamType.Color

@namespace("lsd")
class LSDEffects(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)
        # Pre-calculate bounds to normalize coordinates (0.0 to 1.0)
        # This ensures the effects look good on a rig of ANY size/shape.
        if not coords:
            return
            
        xs, ys, zs = zip(*coords)
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
        self.min_z, self.max_z = min(zs), max(zs)
        
        self.width = (self.max_x - self.min_x) or 1
        self.height = (self.max_y - self.min_y) or 1
        self.depth = (self.max_z - self.min_z) or 1

        # Cache normalized coords for performance
        self.norm_coords = []
        for x, y, z in coords:
            nx = (x - self.min_x) / self.width
            ny = (y - self.min_y) / self.height
            nz = (z - self.min_z) / self.depth
            self.norm_coords.append((nx, ny, nz))

    def _hsv_to_rgba(self, h, s, v, a=255):
        """Helper to convert 0.0-1.0 HSV to 0-255 RGBA tuple"""
        r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
        return (int(r * 255), int(g * 255), int(b * 255), int(a))

    @l_effect(EffectType.UNIVERSAL)
    def lava_lamp(self, steps: int, core_color: Color = (255, 50, 0, 255), bg_color: Color = (10, 0, 20, 255), blob_speed: float = 0.05):
        """
        Simulates 3D metaballs merging and separating.
        """
        frames = []
        
        # Define 3 blob trajectories
        # Using different sine phases so they move chaotically
        for step in range(steps):
            t = step * blob_speed
            
            # Blob centers moving in 0.0-1.0 space
            b1 = (0.5 + 0.4 * math.sin(t), 0.5 + 0.3 * math.cos(t * 1.3), 0.5 + 0.4 * math.sin(t * 0.7))
            b2 = (0.5 + 0.3 * math.sin(t * 1.2 + 2), 0.5 + 0.4 * math.cos(t * 0.9), 0.5 + 0.3 * math.cos(t * 1.5))
            b3 = (0.5 + 0.4 * math.cos(t * 0.8), 0.5 + 0.2 * math.sin(t * 1.1), 0.5 + 0.4 * math.sin(t + 4))
            
            frame = []
            
            for nx, ny, nz in self.norm_coords:
                # Calculate inverse square distance to each blob (Metaball function)
                # Adding a small epsilon (0.01) to prevent division by zero
                d1 = 1.0 / (((nx - b1[0])**2 + (ny - b1[1])**2 + (nz - b1[2])**2) + 0.05)
                d2 = 1.0 / (((nx - b2[0])**2 + (ny - b2[1])**2 + (nz - b2[2])**2) + 0.05)
                d3 = 1.0 / (((nx - b3[0])**2 + (ny - b3[1])**2 + (nz - b3[2])**2) + 0.05)
                
                intensity = (d1 + d2 + d3) / 40.0 # Normalize intensity roughly
                
                # Clamp and interpolate
                t_val = max(0.0, min(1.0, intensity))
                
                # Lerp between background and core color based on proximity to blob
                # Assuming mu.color_lerp returns a tuple (r,g,b,a)
                pixel_color = mu.color_lerp(bg_color, core_color, t_val)
                frame.append(pixel_color)
                
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def psychedelic_plasma(self, steps: int, speed: float = 0.1, scale: float = 3.0, brightness: float = 1.0):
        """
        Interfering sine waves creating a liquid color shifting effect.
        """
        frames = []
        for step in range(steps):
            t = step * speed
            frame = []
            for nx, ny, nz in self.norm_coords:
                # 3D Noise formula using sine wave interference
                # The combination of x, y, z, and t creates the "liquid" motion
                v = math.sin(scale * nx + t)
                v += math.sin(scale * ny + t)
                v += math.sin(scale * nz + t)
                v += math.sin(scale * (nx + ny + nz) + t)
                
                # Map the value (-4 to 4) to 0.0-1.0 hue range
                # We add t * 0.1 to slowly cycle the entire palette over time
                hue = ((v / 4.0) + 0.5 + (t * 0.05)) % 1.0
                
                rgba = self._hsv_to_rgba(hue, 1.0, brightness)
                frame.append(rgba)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def hyperspace_tunnel(self, steps: int, twist_amount: float = 5.0, zoom_speed: float = 0.1):
        """
        Creates a radial rainbow vortex emanating from the center of the rig.
        """
        frames = []
        
        # Pre-calculate polar coordinates relative to center (0.5, 0.5, 0.5)
        # This saves processing time inside the loop
        polar_data = []
        for nx, ny, nz in self.norm_coords:
            dx, dy, dz = nx - 0.5, ny - 0.5, nz - 0.5
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            # Angle in the XY plane
            angle = math.atan2(dy, dx) 
            polar_data.append((dist, angle))

        for step in range(steps):
            offset = step * zoom_speed
            frame = []
            for dist, angle in polar_data:
                # Hue depends on distance (rings) and angle (spiral)
                # The offset makes the rings move outwards/inwards
                hue = (dist * 2.0 + angle / math.pi + offset) % 1.0
                
                # Create a "fade out" at the edges or center if desired, 
                # but for LSD trip, full saturation is better.
                # We can twist the hue based on Z-height for 3D effect
                rgba = self._hsv_to_rgba(hue, 1.0, 1.0)
                frame.append(rgba)
            frames.append(frame)
        return frames

@namespace("lsd")
class ChillEffects(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)
        if not coords:
            return
            
        xs, ys, zs = zip(*coords)
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
        self.min_z, self.max_z = min(zs), max(zs)
        
        self.width = (self.max_x - self.min_x) or 1
        self.height = (self.max_y - self.min_y) or 1
        self.depth = (self.max_z - self.min_z) or 1

        self.norm_coords = []
        for x, y, z in coords:
            nx = (x - self.min_x) / self.width
            ny = (y - self.min_y) / self.height
            nz = (z - self.min_z) / self.depth
            self.norm_coords.append((nx, ny, nz))

    def _hsv_to_rgba(self, h, s, v, a=255):
        r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
        return (int(r * 255), int(g * 255), int(b * 255), int(a))

    @l_effect(EffectType.UNIVERSAL)
    def aurora_borealis(self, steps: int, speed: float = 0.05, wave_density: float = 2.0):
        """
        Smooth, waving curtains of light (Teal/Green/Purple)
        """
        frames = []
        for step in range(steps):
            t = step * speed
            frame = []
            for nx, ny, nz in self.norm_coords:
                # Create the "curtain" shape using sine waves on X and Z
                # We calculate a 'center' line that moves over time
                curve_x = math.sin(nz * wave_density + t) * 0.3 + 0.5
                
                # Distance from the curtain center (horizontal distance)
                dist = abs(nx - curve_x)
                
                # Thickness of the curtain (tapering off at edges)
                intensity = max(0, 1.0 - (dist * 4.0)) 
                
                # Aurora usually fades out at the very top and bottom slightly
                vertical_fade = math.sin(ny * math.pi)
                final_brightness = intensity * vertical_fade
                
                if final_brightness <= 0.05:
                    frame.append((0, 0, 0, 0))
                    continue

                # Color logic: Map Y height to hue (Green at bottom, Purple at top)
                hue = 0.45 + (ny * 0.3)
                
                # Add a little shimmer based on time
                val = final_brightness * (0.8 + 0.2 * math.sin(t * 3 + nx * 5))
                
                frame.append(self._hsv_to_rgba(hue, 0.9, val))
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def breathing_nebula(self, steps: int, speed: float = 0.03, cloud_scale: float = 2.5):
        """
        Volumetric clouds that drift and pulse.
        Very "tame" palette: Blues, Pinks, Violets.
        """
        frames = []
        for step in range(steps):
            t = step * speed
            frame = []
            for nx, ny, nz in self.norm_coords:
                # Sum of Sines to create a cloud-like noise pattern
                n1 = math.sin(nx * cloud_scale + t)
                n2 = math.sin(ny * cloud_scale - t * 0.5)
                n3 = math.sin(nz * cloud_scale + t * 0.2)
                
                # Normalize noise -1.5 to 1.5 -> 0.0 to 1.0
                noise_val = (n1 + n2 + n3 + 3) / 6.0
                
                # Add a "breathing" global pulse
                pulse = (math.sin(t * 2) + 1) / 2.0
                brightness = noise_val * (0.5 + 0.5 * pulse)
                
                # Color Gradient: Deep Blue (0.6) to Pink/Magenta (0.9)
                hue = 0.6 + (noise_val * 0.3)
                
                sat = 0.8
                
                frame.append(self._hsv_to_rgba(hue, sat, brightness))
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def ghost_ripples(self, steps: int, speed: float = 0.1, ripples: int = 3):
        """
        Soft, horizontal rings rising slowly upward.
        """
        frames = []
        for step in range(steps):
            t = step * speed
            frame = []
            for nx, ny, nz in self.norm_coords:
                # Calculate radial distance from center (cylinder shape)
                r = math.sqrt((nx - 0.5)**2 + (nz - 0.5)**2)
                
                # The wave function: 
                wave = math.sin(10 * r - ny * 5 + t * 5)
                
                # Sharpen the wave slightly, then clamp
                intensity = (wave + 1) / 2.0
                intensity = intensity ** 4
                
                # Fade out as it gets higher (dissipating smoke)
                height_fade = 1.0 - ny
                final_val = intensity * height_fade
                
                # Color: Gold/Orange warmth
                rgba = self._hsv_to_rgba(0.08, 1.0, final_val)
                frame.append(rgba)
            frames.append(frame)
        return frames