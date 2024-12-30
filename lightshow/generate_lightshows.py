import time
import colorsys
import mathutils as mu
from bisect import bisect_right
import pickle
# CONSTANTS, GLOBAL VARIABLES
color_states = {}
LED_COUNT = 200
coords = []
with open('coordinates.txt', 'r') as f:
    for coord in f.readlines():
        coords.append([int(value) for value in coord.strip().split(',')])
tree_height = max([coord[2] for coord in coords])
limits_x = (min([coord[0] for coord in coords]), max([coord[0] for coord in coords]))
limits_y = (min([coord[1] for coord in coords]), max([coord[1] for coord in coords]))
x_width = limits_x[1] - limits_x[0]
y_width = limits_y[1] - limits_y[0]


# PARSING FUNCTIONS

def parse_labels(file_path):
    def parse_arg(arg):
        """Converts a string argument into its appropriate type."""
        arg = arg.strip()
        # Check if the argument is a tuple
        if arg.startswith("(") and arg.endswith(")"):
            return tuple(parse_arg(x) for x in arg[1:-1].split(","))
        # Try to convert to float or int
        if arg in ["True", "False"]:
            return arg == "True"
        try:
            if "." in arg:
                return float(arg)
            return int(arg)
        except ValueError:
            # If conversion fails, return as a string
            return arg

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().replace(", ", ",").replace("; ", ";")
            if not line:
                continue  # Skip empty lines

            # Split the line into parts
            start_time_str, end_time_str, func_args = line.split('\t')
            start_time = float(start_time_str)
            end_time = float(end_time_str)

            # Parse the function and its arguments
            func_parts = func_args.split(';')
            func_name = func_parts[0].strip()
            args = [parse_arg(arg) for arg in func_parts[1:]]

            # Compute the duration
            duration = end_time - start_time

            # Convert func_name to actual function
            func = globals().get(func_name)
            if func is None:
                raise ValueError(f"Function '{func_name}' not found!")

            # Schedule the effect
            print(f"Scheduling {func_name} at {start_time:.2f}s with args {args}")
            func(start_time, duration, *args)

def finalize_transparent():
    """Replace all None values in the color states with the color of last frame."""
    for idx, timestamp in enumerate(sorted(color_states.keys())):
        if idx == 0:
            for i in range(LED_COUNT):
                if color_states[timestamp][i] is None:
                    color_states[timestamp][i] = (0, 0, 0)
        else:
            for i in range(LED_COUNT):
                if color_states[timestamp][i] is None:
                    color_states[timestamp][i] = color_states[idx-1][i]

# COLOR STATE FUNCTIONS

def update_color_state(timestamp, colors):
    """Update the global color state at a specific timestamp."""
    color_states[timestamp] = colors[:]

def set_color(timestamp, index, color):
    """Set the color of a specific LED at a specific timestamp."""
    if timestamp not in color_states:
        color_states[timestamp] = [(0, 0, 0)] * LED_COUNT
    color_states[timestamp][index] = color

def fill_color(timestamp, color):
    """Set all LEDs to the same color at a specific timestamp."""
    if timestamp not in color_states:
        color_states[timestamp] = [(0, 0, 0)] * LED_COUNT
    color_states[timestamp] = [color] * LED_COUNT

# EFFECTS =====================================================================
# EFFECTS =====================================================================
# EFFECTS =====================================================================
# EFFECTS =====================================================================

def solid_color(start_time, duration, color):
    for t in range(int(start_time), int(start_time + duration)):
        update_color_state(t, [color] * LED_COUNT)

def fade(start_time, duration, color1, color2, steps=0):
    if steps <= 0:
        steps = int(duration * 24)

    step_r = (color2[0] - color1[0]) / steps
    step_g = (color2[1] - color1[1]) / steps
    step_b = (color2[2] - color1[2]) / steps

    for step in range(steps):
        intermediate_color = (
            int(color1[0] + step * step_r),
            int(color1[1] + step * step_g),
            int(color1[2] + step * step_b),
        )
        timestamp = start_time + step * (duration / steps)
        if step == steps - 1:
            intermediate_color = color2
        update_color_state(timestamp, [intermediate_color] * LED_COUNT)

def flash(start_time, duration, color1, color2, frequency=20):
    steps = int(duration * frequency)
    for step in range(steps):
        timestamp = start_time + step / frequency
        colors = [color1] * LED_COUNT if step % 2 == 0 else [color2] * LED_COUNT
        update_color_state(timestamp, colors)

def flash2(start_time, duration, color1, color2, frequency=20):
    steps = int(duration * frequency)
    for step in range(steps):
        timestamp = start_time + step / frequency
        colors = [color1 if i % 2 == step % 2 else color2 for i in range(LED_COUNT)]
        update_color_state(timestamp, colors)

def flash_times(start_time, duration, color1, color2, times):
    frequency = times / duration
    flash(start_time, duration, color1, color2, frequency)

def flash2_times(start_time, duration, color1, color2, times):
    frequency = times / duration
    flash2(start_time, duration, color1, color2, frequency)

def swipe_up(start_time, duration, color, width=100, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_z = 0 - width
    for step in range(steps):
        current_z += (tree_height + 2 * width) / steps
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            dist = abs(coords[i][2] - current_z)
            if dist < width / 2:
                colors[i] = mu.color_lerp((0, 0, 0), color, mu.normalize(dist, 0, width / 2))
        update_color_state(timestamp, colors)

def swipe_down(start_time, duration, color, width=100, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_z = tree_height + width
    for step in range(steps):
        current_z -= (tree_height + 2 * width) / steps
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            dist = abs(coords[i][2] - current_z)
            if dist < width / 2:
                colors[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        update_color_state(timestamp, colors)

def swipe_right(start_time, duration, color, width=50, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_x = limits_x[0] - width
    for step in range(steps):
        current_x += (x_width + 2 * width) / steps
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            dist = abs(coords[i][0] - current_x)
            if dist < width / 2:
                colors[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        update_color_state(timestamp, colors)

def swipe_left(start_time, duration, color, width=50, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_x = limits_x[1] + width
    for step in range(steps):
        current_x -= (x_width + 2 * width) / steps
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            dist = abs(coords[i][0] - current_x)
            if dist < width / 2:
                colors[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        update_color_state(timestamp, colors)

def swipe_forward(start_time, duration, color, width=50, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_y = limits_y[0] - width
    for step in range(steps):
        current_y += (y_width + 2 * width) / steps
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            dist = abs(coords[i][1] - current_y)
            if dist < width / 2:
                colors[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        update_color_state(timestamp, colors)

def swipe_backward(start_time, duration, color, width=50, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_y = limits_y[1] + width
    for step in range(steps):
        current_y -= (y_width + 2 * width) / steps
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            dist = abs(coords[i][1] - current_y)
            if dist < width / 2:
                colors[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        update_color_state(timestamp, colors)

def rainbow(start_time, duration, speed=10, steps=0):
    current_z = 0
    if steps <= 0:
        steps = int(duration * 24)

    for step in range(steps):
        current_z += speed
        if current_z > tree_height:
            current_z = 0
        timestamp = start_time + step * (duration / steps)
        colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            normalized_rgb = list(colorsys.hsv_to_rgb(mu.normalize(mu.wrap(coords[i][2] - current_z, 0, tree_height), 0, tree_height), 1, 1))
            colors[i] = tuple([int(channel * 255) for channel in normalized_rgb])
        update_color_state(timestamp, colors)

def gradient(start_time, duration, color1, color2, speed=10, steps=0):
    current_z = 0
    if steps <= 0:
        steps = int(duration * 24)

    for step in range(steps):
        current_z += speed
        if current_z > tree_height:
            current_z = 0
        timestamp = start_time + step * (duration / steps)
        colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            normalized_rgb = mu.color_lerp(color1, color2, mu.normalize(mu.wrap(coords[i][2] - current_z, 0, tree_height), 0, tree_height))
            colors[i] = normalized_rgb
        update_color_state(timestamp, colors)

def string_up(start_time, duration, color, trail_length=25, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_pixel = -trail_length
    for step in range(steps):
        current_pixel += int((LED_COUNT + 2 * trail_length) / steps)
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(trail_length):
            pos = current_pixel + i
            if pos < LED_COUNT and pos >= 0:
                colors[pos] = mu.color_lerp((0, 0, 0), color, mu.normalize(i, 0, trail_length))
        update_color_state(timestamp, colors)

def string_down(start_time, duration, color, trail_length=25, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    current_pixel = LED_COUNT + trail_length
    for step in range(steps):
        current_pixel -= int((LED_COUNT + 2 * trail_length) / steps)
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(trail_length):
            pos = current_pixel - i
            if pos < LED_COUNT and pos >= 0:
                colors[pos] = mu.color_lerp((0, 0, 0), color, mu.normalize(i, 0, trail_length))
        update_color_state(timestamp, colors)

def split_vertical(start_time, duration, color1, color2, steps=0, no_clear=False):
    if steps <= 0:
        steps = int(duration * 24)

    mid_x = (limits_x[0] + limits_x[1]) / 2
    for step in range(steps):
        timestamp = start_time + step * (duration / steps)
        if no_clear:
            colors = [None] * LED_COUNT
        else:
            colors = [(0, 0, 0)] * LED_COUNT
        for i in range(LED_COUNT):
            if coords[i][0] < mid_x:
                colors[i] = color1
            else:
                colors[i] = color2
        update_color_state(timestamp, colors)

if __name__ == "__main__":
    song_name = "overkill"
    parse_labels(f"lightshow/labels/{song_name}.txt")
    print(f"Color states: {color_states}")
    with open(f"lightshow/performances/{song_name}.pkl", "wb") as f:
        pickle.dump(color_states, f)