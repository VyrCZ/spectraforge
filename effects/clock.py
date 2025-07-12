from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time
import datetime
import requests as req
import math

class Clock(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "The Clock", EffectType.ONLY_2D)
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 50, min=1, max=500, step=1)
        self.hands_color = self.add_parameter("Hands Color", ParamType.COLOR, "#ffffff")
        self.frame_color = self.add_parameter("Frame Color", ParamType.COLOR, "#0051ff")
        self.seconds_color = self.add_parameter("Seconds Color", ParamType.COLOR, "#000000")
        try:
            response = req.get("http://worldtimeapi.org/api/timezone/Europe/Prague").json()
            accurate_time = datetime.datetime.fromisoformat(response["datetime"].replace("Z", "+00:00"))
            self.offset = accurate_time - datetime.datetime.now()
        except Exception as e:
            print(f"Error fetching time: {e}")
            self.offset = datetime.timedelta(seconds=0)
        # calculate which pixel is the most centered
        average_pos = (
            sum(coord[0] for coord in coords) / len(coords),
            sum(coord[1] for coord in coords) / len(coords)
        )
        self.center_pixel_coords = min(
            coords,
            key=lambda coord: mu.distance(coord, average_pos)
        )
        self.center_pixel_index = coords.index(self.center_pixel_coords)

        # calculate shortest distance to an edge to determine radius
        min_x = min(c[0] for c in coords)
        max_x = max(c[0] for c in coords)
        min_y = min(c[1] for c in coords)
        max_y = max(c[1] for c in coords)
        self.radius = min(
            self.center_pixel_coords[0] - min_x,
            max_x - self.center_pixel_coords[0],
            self.center_pixel_coords[1] - min_y,
            max_y - self.center_pixel_coords[1]
        )

    def update(self):
        now = datetime.datetime.now(datetime.timezone.utc) + self.offset
        
        # Calculate hand angles in radians, adjusting for 12 o'clock at top
        hour_angle = ((now.hour % 12 + now.minute / 60) / 12) * 2 * math.pi - math.pi / 2
        minute_angle = ((now.minute + now.second / 60) / 60) * 2 * math.pi - math.pi / 2
        second_angle = (now.second / 60) * 2 * math.pi - math.pi / 2

        hour_len = self.radius * 0.5
        minute_len = self.radius * 0.8
        second_len = self.radius * 0.9

        frame_c = self.frame_color.get()
        hands_c = self.hands_color.get()
        seconds_c = self.seconds_color.get()

        for i, coord in enumerate(self.coords):
            dist_from_center = mu.distance(coord, self.center_pixel_coords)
            
            # Draw frame
            if abs(dist_from_center - self.radius) < 1:
                self.renderer[i] = frame_c
                continue

            # Calculate pixel angle relative to center
            angle = math.atan2(coord[1] - self.center_pixel_coords[1], coord[0] - self.center_pixel_coords[0])
            
            # Draw hands
            on_hour = abs(angle - hour_angle) < 0.1 and dist_from_center <= hour_len
            on_minute = abs(angle - minute_angle) < 0.1 and dist_from_center <= minute_len
            on_second = abs(angle - second_angle) < 0.1 and dist_from_center <= second_len

            if on_hour or on_minute:
                self.renderer[i] = hands_c
            elif on_second:
                self.renderer[i] = seconds_c
            else:
                self.renderer[i] = (0, 0, 0)

        self.renderer.show()