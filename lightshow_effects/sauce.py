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
    
    @l_effect(EffectType.UNIVERSAL)
    def ground_mist(self, steps: int, 
                       mist_color: Color = (0, 255, 100, 255), 
                       bg_color: Color = Color.transparent, 
                       density: int = 20, 
                       rise_speed: float = 0.05, 
                       particle_radius: float = 0.5, 
                       seed: int = 42):
        """
        High-fidelity ground mist with Gaussian anti-aliasing and additive RGBA blending.
        Y is the vertical axis: particles spawn near the lowest Y and rise along Y.
        """
        frames = []
        n_leds = len(self.coords)
        rng = random.Random(seed)

        # 1. Geometry Setup (Find the floor using Y as up)
        y_coords = [c[1] for c in self.coords]
        min_y = min(y_coords)
        ground_threshold = min_y + ((max(y_coords) - min_y) * 0.15)  # Bottom 15%
        
        # Pre-calculate emitter indices for speed (spawn near floor in Y)
        emitter_indices = [i for i, y in enumerate(y_coords) if y <= ground_threshold]

        # Particle structure: {'pos': [x,y,z], 'age', 'life', 'vel': [vx, vy, vz]}
        particles = []

        # Optimization: Pre-calculate color values as 0-1 floats for math
        mc_r, mc_g, mc_b, mc_a = [c / 255.0 for c in mist_color]
        bg_r, bg_g, bg_b, bg_a = [c / 255.0 for c in bg_color]

        # Gaussian width control (sigma). 
        sigma = particle_radius / 2.0 
        sigma_sq_inv = 1.0 / (2 * sigma * sigma)

        for _ in range(steps):
            # --- 1. Accumulation Buffers (Float precision) ---
            buff_r = [bg_r] * n_leds
            buff_g = [bg_g] * n_leds
            buff_b = [bg_b] * n_leds
            buff_a = [bg_a] * n_leds

            # --- 2. Spawn Logic ---
            if density > 0 and rng.randint(0, 100) < density and emitter_indices:
                start_idx = rng.choice(emitter_indices)
                start_pos = self.coords[start_idx]
                # vel: lateral drift on X/Z, rise on Y
                particles.append({
                    'pos': list(start_pos),
                    'age': 0,
                    'life': rng.randint(30, 60),
                    'vel': [rng.uniform(-0.02, 0.02), rise_speed, rng.uniform(-0.02, 0.02)]
                })

            # --- 3. Physics & Rendering ---
            active_particles = []
            for p in particles:
                # Update Motion
                p['pos'][0] += p['vel'][0]
                p['pos'][1] += p['vel'][1]
                p['pos'][2] += p['vel'][2]
                p['age'] += 1

                # Calculate Age Opacity (Fade in fast, fade out slow)
                age_pct = p['age'] / p['life']
                if age_pct >= 1.0:
                    continue  # Kill particle
                
                particle_opacity = math.sin(age_pct * math.pi) 

                active_particles.append(p)
                
                px, py, pz = p['pos']

                # --- 4. Volumetric Anti-Aliasing (Gaussian Splatting) ---
                for i, (lx, ly, lz) in enumerate(self.coords):
                    dx = lx - px
                    dy = ly - py
                    dz = lz - pz
                    
                    if abs(dx) > particle_radius or abs(dy) > particle_radius or abs(dz) > particle_radius:
                        continue

                    dist_sq = dx*dx + dy*dy + dz*dz
                    intensity = math.exp(-dist_sq * sigma_sq_inv) * particle_opacity

                    if intensity > 0.01:
                        buff_r[i] += mc_r * intensity
                        buff_g[i] += mc_g * intensity
                        buff_b[i] += mc_b * intensity
                        buff_a[i] += mc_a * intensity

            particles = active_particles

            # --- 5. Composite Frame ---
            final_frame = []
            for i in range(n_leds):
                r = int(min(1.0, buff_r[i]) * 255)
                g = int(min(1.0, buff_g[i]) * 255)
                b = int(min(1.0, buff_b[i]) * 255)
                a = int(min(1.0, buff_a[i]) * 255)
                final_frame.append((r, g, b, a))

            frames.append(final_frame)

        return frames