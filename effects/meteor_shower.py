from modules.effect import LightEffect, ParamType, EffectType
import math
import random
import time
from modules.log_manager import Log

class MeteorShower(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Meteor Shower", EffectType.ONLY_2D)
        self.color = self.add_parameter("Meteors Color", ParamType.COLOR, "#FF7300")
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 5, min=1, max=10, step=1)  # Fall speed
        self.amount = self.add_parameter("Amount", ParamType.SLIDER, 8, min=1, max=15, step=1)  # Droplet count
        self.angle = self.add_parameter("Angle", ParamType.SLIDER, 10, min=-45, max=45, step=1) # Angle to the vertical line
        self.thickness = self.add_parameter("Thickness", ParamType.SLIDER, 1, min=1, max=100, step=1)  # Thickness of the meteor
        self.trail_length = self.add_parameter("Trail Length", ParamType.SLIDER, 30, min=1, max=100, step=1) # % of height

        # set spawn bounds
        self.max_y = max(coord[1] for coord in coords)
        self.min_y = min(coord[1] for coord in coords)
        self.min_x = min(coord[0] for coord in coords)
        self.max_x = max(coord[0] for coord in coords)
        self.height = self.max_y - self.min_y
        self.spawn_y = self.max_y + self.height * 0.1  # Spawn above
        self.meteors = []
        self.spawn_cooldown = 0
        self.frame_length = 1/60

    def update(self):
        self.renderer.clear()
        bound_y = self.min_y - self.height * self.trail_length.get() / 100  # don't need the top y bound
        bound_min_x = self.min_x - self.height * self.trail_length.get() / 100
        bound_max_x = self.max_x + self.height * self.trail_length.get() / 100
        move_distance = self.speed.get() * self.frame_length * 150
        move_vector = [
            -math.sin(math.radians(self.angle.get())) * move_distance,
            -math.cos(math.radians(self.angle.get())) * move_distance,
            0
        ]
        self.spawn_delay = (self.amount.get() / self.speed.get()) / 4
        x_offset = (math.tan(math.radians(self.angle.get())) * (self.height / 10))
        x_offset *= -1 if self.angle.get() < 0 else 1  # Adjust direction based on angle
        self.spawn_min_x = self.min_x + x_offset
        self.spawn_max_x = self.max_x + x_offset
        #self.renderer.debug_draw.line(
        #    (self.spawn_min_x, self.spawn_y, 0),
        #    (self.spawn_max_x, self.spawn_y, 0),
        #    color=(0, 255, 0))
        #Log.debug("MeteorShower", f"Cooldown: {self.spawn_cooldown} / {self.spawn_delay}")
        if len(self.meteors) < self.amount.get() and self.spawn_cooldown <= 0:
            #print("Spawning meteor")
            self.meteors.append([random.randint(int(self.spawn_min_x), int(self.spawn_max_x)), self.spawn_y, 0])
            self.spawn_cooldown = self.spawn_delay
        for meteor in self.meteors:
            # Update meteor position
            meteor[0] += move_vector[0]
            meteor[1] += move_vector[1]
            #print(f"Meteor pos: {meteor}; Move vector: {move_vector}")
            if meteor[1] < bound_y or meteor[0] < bound_min_x or meteor[0] > bound_max_x:
                print(f"Removing meteor {meteor}; Bounds: y: {bound_y}, x: [{bound_min_x}, {bound_max_x}]")
                self.meteors.remove(meteor)
                continue
            tail = [
                meteor[0] + math.sin(math.radians(self.angle.get())) * (self.height * self.trail_length.get() / 100),
                meteor[1] + math.cos(math.radians(self.angle.get())) * (self.height * self.trail_length.get() / 100),
                0
            ]
            #self.renderer.debug_draw.line(meteor, tail, (255,255,255))
            t = tail
            m = meteor
            for idx, coord in enumerate(self.coords):
                # formula I calculated, hopefully correct
                # distance from point to the line Meteor-Tail
                l = coord
                dx = t[0] - m[0]
                dy = t[1] - m[1]
                # Numerator of the distance formula
                numerator = abs(dy * (l[0] - m[0]) - dx * (l[1] - m[1]))
                # Denominator of the distance formula (length of the trail)
                denominator = math.sqrt(dx**2 + dy**2)
                if denominator == 0: continue # Avoid division by zero
                dist = numerator / denominator

                if dist < self.thickness.get():
                    # Vector from meteor head to the light
                    ml_vec = (l[0] - m[0], l[1] - m[1])
                    # Vector of the meteor trail (head to tail)
                    mt_vec = (t[0] - m[0], t[1] - m[1])

                    # Project ml_vec onto mt_vec to see if the light is behind the head
                    dot_product = ml_vec[0] * mt_vec[0] + ml_vec[1] * mt_vec[1]

                    # If the dot product is negative, the light is in front of the meteor head
                    if dot_product < 0:
                        continue

                    # calculate brightness based on ratio of distance from M to T
                    dist_ml_sq = (l[0] - m[0])**2 + (l[1] - m[1])**2

                    # Ensure the projection is on the segment using pythagoras
                    # and avoid sqrt domain error
                    if dist_ml_sq < dist**2:
                        dist_on_line = 0
                    else:
                        dist_on_line = math.sqrt(dist_ml_sq - dist**2)

                    # Total length of the meteor trail
                    trail_len = math.sqrt((t[0] - m[0])**2 + (t[1] - m[1])**2)
                    if trail_len == 0: continue

                    # Ratio along the trail
                    ratio = 1 - (dist_on_line / trail_len)
                    if ratio < 0: # No need to check for > 1 with the dot product check
                        ratio = 0
                    col = self.color.get()
                    self.renderer[idx] = [
                        int(col[0] * ratio),
                        int(col[1] * ratio),
                        int(col[2] * ratio)
                    ]
                else:
                    continue
        self.renderer.show()
        self.spawn_cooldown -= self.frame_length
        time.sleep(self.frame_length)