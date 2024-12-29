from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from threading import Thread, Event
import os
import time
from neopixel import NeoPixel
import board
pixels = NeoPixel(board.D18, 200, auto_write=False)
import colorsys
import random
import mathutils as mu

#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class DummyNeoPixel():
    def __init__(self, pin, num_leds, auto_write):
        self.num_leds = num_leds
        self.pixels = [(0, 0, 0)] * num_leds
        self.auto_write = auto_write

    def __setitem__(self, key, value):
        self.pixels[key] = value

    def fill(self, color):
        for i in range(self.num_leds):
            self.pixels[i] = color

    def show(self):
        print(self.pixels)


#pixels = DummyNeoPixel("yes", 200, False)
coords = []
with open('coordinates.txt', 'r') as f:
    for coord in f.readlines():
        coords.append([int(value) for value in coord.strip().split(',')])
tree_height = max([coord[2] for coord in coords])
limits_x = (min([coord[0] for coord in coords]), max([coord[0] for coord in coords]))
limits_y = (min([coord[1] for coord in coords]), max([coord[1] for coord in coords]))
x_width = limits_x[1] - limits_x[0]
y_width = limits_y[1] - limits_y[0]

# Server configuration
AUDIO_FILE_PATH = "static/audio"
AUDIO_FILE_NAME = "overkill.mp3"
BPM = 174  # Beats per minute
offset = 0.2
beat_interval = 60 / BPM  # Time between beats in seconds
start_time = None  # The server's internal start time
current_time = 0  # Server's calculated playback time
last_sync_time = 0  # Last sync timestamp received from the client
stop_event = Event()
event_thread = None
scheduled_events = []
next_beat_time = 0
click_file = os.path.abspath(os.path.join("lightshow", AUDIO_FILE_PATH, "click.wav"))
hue = 0

app = Flask(__name__)
socketio = SocketIO(app)
# Function scheduling
def schedule_effect(time_in_seconds, function, *args, **kwargs):
    """Add a function to be executed at a specific time in the song."""
    scheduled_events.append((time_in_seconds, function, args, kwargs))
    scheduled_events.sort(key=lambda x: x[0])  # Keep events sorted by time

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
            schedule_effect(start_time, func, duration, *args)


def event_runner():
    """Handles the metronome and execution of scheduled events."""
    global next_beat_time, current_time

    while not stop_event.is_set():
        # Calculate the server's current playback time
        if start_time is not None:
            current_time = time.time() - start_time + offset

        # Handle metronome
        if current_time >= next_beat_time:
            on_beat()
            next_beat_time += beat_interval

        # Handle scheduled events
        for event_time, function, args, kwargs in scheduled_events[:]:
            if current_time >= event_time + offset:
                print(f"Running scheduled function at {event_time:.2f}s")
                function(*args, **kwargs)
                scheduled_events.remove((event_time, function, args, kwargs))
                break  # Avoid iterating over modified list

        time.sleep(0.01)  # Avoid busy-waiting

def on_beat():
    """Runs on every new beat."""
    """global hue
    hue += random.uniform(0.2, 0.8)
    random_color = colorsys.hsv_to_rgb(hue, 1, 0.5)
    solid_color(tuple(int(channel * 255) for channel in random_color))"""


@socketio.on("playback_progress")
def handle_progress(data):
    """Sync the server's playback time with the client."""
    global start_time, current_time, last_sync_time
    client_time = data["seconds"]
    last_sync_time = time.time()
    current_time = client_time + offset
    start_time = time.time() - current_time  # Adjust the server's start time
    #print(f"Synced playback time: {current_time:.2f}s")

@socketio.on("start_audio")
def start_audio(data=None):
    """Start the event runner when the client starts the audio."""
    global event_thread, start_time, current_time
    if event_thread is None or not event_thread.is_alive():
        stop_event.clear()
        next_beat_time = 0  # Reset metronome timing
        current_time = 0
        start_time = time.time()  # Initialize server's timer
        event_thread = Thread(target=event_runner)
        event_thread.start()
    print("Audio started by client.")

@socketio.on("stop_audio")
def stop_audio(data=None):
    """Stop the event runner when the client stops or ends the audio."""
    global start_time
    stop_event.set()
    start_time = None
    print("Audio stopped by client.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/audio/<filename>")
def audio(filename):
    return send_from_directory(AUDIO_FILE_PATH, filename)

# EFFECTS =====================================================================
# EFFECTS =====================================================================
# EFFECTS =====================================================================
# EFFECTS =====================================================================

def solid_color(duration, color):
    pixels.fill(color)
    pixels.show()

def fade(duration, color1, color2, steps=0):
    
    if(steps <= 0):
        steps = int(duration * 20) # Default to 20 steps per second

    # Calculate the color step for each channel
    step_r = (color2[0] - color1[0]) / steps
    step_g = (color2[1] - color1[1]) / steps
    step_b = (color2[2] - color1[2]) / steps

    for step in range(steps):
        # Calculate intermediate color
        intermediate_color = (
            int(color1[0] + step * step_r),
            int(color1[1] + step * step_g),
            int(color1[2] + step * step_b)
        )

        # Set the pixels to the intermediate color
        pixels.fill(intermediate_color)
        pixels.show()

        # Sleep for the appropriate time per step
        time.sleep(duration / steps)

    # Ensure the final color is set precisely
    pixels.fill(color2)
    pixels.show()

def flash(duration, color1, color2, frequency=20):
    # flashes between two colors at the given frequency for the given duration
    steps = int(duration * frequency)
    for i in range(steps):
        if i % 2 == 0:
            pixels.fill(color1)
        else:
            pixels.fill(color2)
        pixels.show()
        time.sleep(1 / frequency)

def flash2(duration, color1, color2, frequency=20):
    """Flash between two colors."""
    # switches between two states: even leds are color1, odd leds are color2 and vice versa at the given frequency for the given duration
    steps = int(duration * frequency)
    for i in range(steps):
        if i % 2 == 0:
            pixels[::2] = [color1] * len(pixels[::2])
            pixels[1::2] = [color2] * len(pixels[1::2])
        else:
            pixels[::2] = [color2] * len(pixels[::2])
            pixels[1::2] = [color1] * len(pixels[1::2])
        pixels.show()
        time.sleep(1 / frequency)

def flash_times(duration, color1, color2, times):
    """Same as flash but instead of frequency, you enter exact number of flashes."""
    frequency = duration / times
    flash(duration, color1, color2, frequency)

def flash2_times(duration, color1, color2, times):
    """Same as flash2 but instead of frequency, you enter exact number of flashes."""
    frequency = duration / times
    flash2(duration, color1, color2, frequency)

def swipe_up(duration, color, width=50, steps=0, no_clear = False):
    """[SPACIAL] Passes a wave of color up the tree."""
    if steps <= 0:
        steps = int(duration * 20)
    print(f"Steps: {steps}, Duration: {duration}")
    current_z = 0 - width
    for step in range(steps):
        current_z += (tree_height + 2 * width) / steps
        print("Current Z:", current_z)
        for i in range(len(pixels)):
            dist = abs(coords[i][2] - current_z)
            # width is the width of the whole thing, (2 gradients from top and bottom)
            if dist < width / 2:
                pixels[i] = mu.color_lerp((0, 0, 0), color, mu.normalize(dist, 0, width / 2))
            else:
                if not no_clear:
                    pixels[i] = (0, 0, 0)
        pixels.show()
        time.sleep(duration / steps)

def swipe_down(duration, color, width=50, steps=0, no_clear = False):
    """[SPACIAL] Passes a wave of color down the tree."""
    if steps <= 0:
        steps = int(duration * 20)
    current_z = tree_height + width
    for step in range(steps):
        if not no_clear:
            pixels.fill((0, 0, 0))
        current_z -= (tree_height + 2 * width) / steps
        for i in range(len(pixels)):
            dist = abs(coords[i][2] - current_z)
            # width is the width of the whole thing, (2 gradients from top and bottom)
            if dist < width / 2:
                pixels[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        pixels.show()
        time.sleep(duration / steps)

def swipe_right(duration, color, width=25, steps=0):
    """[SPACIAL] Passes a wave of color on the X axis from left to right."""
    if steps <= 0:
        steps = int(duration * 20)
    current_x = limits_x[0] - width
    for step in range(steps):
        pixels.fill((0, 0, 0))
        current_x += (x_width + 2 * width) / steps
        for i in range(len(pixels)):
            dist = abs(coords[i][0] - current_x)
            if dist < width / 2:
                pixels[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        pixels.show()
        time.sleep(duration / steps)

def swipe_left(duration, color, width=25, steps=0):
    """[SPACIAL] Passes a wave of color on the X axis from right to left."""
    if steps <= 0:
        steps = int(duration * 20)
    current_x = limits_x[1] + width
    for step in range(steps):
        pixels.fill((0, 0, 0))
        current_x -= (x_width + 2 * width) / steps
        for i in range(len(pixels)):
            dist = abs(coords[i][0] - current_x)
            if dist < width / 2:
                pixels[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        pixels.show()
        time.sleep(duration / steps)

def swipe_forward(duration, color, width=25, steps=0):
    """[SPACIAL] Passes a wave of color on the Y axis from back to front."""
    if steps <= 0:
        steps = int(duration * 20)
    current_y = limits_y[0] - width
    for step in range(steps):
        pixels.fill((0, 0, 0))
        current_y += (y_width + 2 * width) / steps
        for i in range(len(pixels)):
            dist = abs(coords[i][1] - current_y)
            if dist < width / 2:
                pixels[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        pixels.show()
        time.sleep(duration / steps)

def swipe_backward(duration, color, width=25, steps=0):
    """[SPACIAL] Passes a wave of color on the Y axis from front to back."""
    if steps <= 0:
        steps = int(duration * 20)
    current_y = limits_y[1] + width
    for step in range(steps):
        pixels.fill((0, 0, 0))
        current_y -= (y_width + 2 * width) / steps
        for i in range(len(pixels)):
            dist = abs(coords[i][1] - current_y)
            if dist < width / 2:
                pixels[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
        pixels.show()
        time.sleep(duration / steps)
    
def rainbow(duration, speed=10, steps=0):
    """[SPACIAL] Cycles through the rainbow. From bottom to top"""  
    current_z = 0
    if(steps <= 0):
        steps = int(duration * 20)
    for step in range(steps):
        current_z += speed
        if current_z > tree_height:
            current_z = 0
        for i in range(len(pixels)):
            normalized_rgb = list(colorsys.hsv_to_rgb(mu.normalize(mu.wrap(coords[i][2] - current_z, 0, tree_height), 0, tree_height), 1, 1))
            pixels[i] = tuple([int(channel * 255) for channel in normalized_rgb])
        pixels.show()

def gradient(duration, color1, color2, steps=0):
    """[SPACIAL] Creates a vertical gradient, which is travelling up the tree, much like rainbow."""
    # fill this space with rainbow for now
    rainbow(duration, 10, steps)

def string_up(duration, color, trail_length=25, steps=0, no_clear = False):
    """Travels up the string of lights."""
    if steps <= 0:
        steps = int(duration * 5)
    current_pixel = -trail_length
    for step in range(steps):
        current_pixel += int((len(pixels) + 2 * trail_length) / steps)
        if not no_clear:
            pixels.fill((0, 0, 0))
        for i in range(trail_length):
            pos = current_pixel + i
            if pos < len(pixels) and pos >= 0:
                pixels[pos] = mu.color_lerp((0, 0, 0), color, mu.normalize(i, 0, trail_length))
        pixels.show()
        time.sleep(duration / steps)

def string_down(duration, color, trail_length=25, steps=0, no_clear = False):
    """Travels down the string of lights."""
    if steps <= 0:
        steps = int(duration * 5)
    current_pixel = len(pixels) + trail_length
    for step in range(steps):
        current_pixel -= int((len(pixels) + 2 * trail_length) / steps)
        if not no_clear:
            pixels.fill((0, 0, 0))
        for i in range(trail_length):
            pos = current_pixel - i
            if pos < len(pixels) and pos >= 0:
                pixels[pos] = mu.color_lerp((0, 0, 0), color, mu.normalize(i, 0, trail_length))
        pixels.show()
        time.sleep(duration / steps)

def split_vertical(duration, color1, color2, steps=0):
    """[SPACIAL] Makes two swipes from the middle to the top and bottom. Color1 is the top color, color2 is the bottom color."""
    # fill this place with swipe_up for now
    swipe_up(duration, color1, 50, steps)


if __name__ == "__main__":
    # Schedule some example events
    """schedule_effect(0.5, solid_color, 0, (127, 127, 127))
    schedule_effect(0.6, solid_color, 0, (0, 0, 0))
    schedule_effect(0.7, solid_color, 0, (127, 127, 127))
    schedule_effect(0.8, solid_color, 0, (0, 0, 0))
    schedule_effect(0.866, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(1.259, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(1.704, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(2.150, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(2.557, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(2.987, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(3.406, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(3.850, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(4.270, fade, 0.3, (180, 255, 0), (0, 0, 0))
    schedule_effect(4.705, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(5.137, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(5.555, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(6.000, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(6.421, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(6.852, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(7.258, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(7.677, fade, 0.3, (180, 255, 0), (0, 0, 0))
    schedule_effect(8.110, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(8.541, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(8.989, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(9.407, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(9.838, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(10.255, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(10.705, fade, 0.3, (255, 0, 0), (0, 0, 0))
    schedule_effect(11.135, fade, 1.5, (180, 0, 255), (0, 0, 0), 20)
    schedule_effect(12.844, solid_color, 0, (0, 255, 0))
    schedule_effect(13.722, solid_color, 0, (0, 0, 255))"""
    # test every effect, for duration 3 seconds, with different colors each"""
    """schedule_effect(0, solid_color, (255, 0, 0))
    schedule_effect(3, fade, (0, 255, 0), (0, 0, 0), 2.5)
    schedule_effect(6, flash, (0, 0, 255), (255, 255, 255), 2.5, 2)
    schedule_effect(9, flash2, (255, 0, 255), (0, 255, 255), 2.5, 4)
    schedule_effect(12, swipe_up, (127, 127, 127), 2.5, 100)
    schedule_effect(15, swipe_down, (127, 127, 127), 2.5, 100)
    schedule_effect(18, swipe_right, (127, 127, 127), 2.5, 50)
    schedule_effect(21, swipe_left, (127, 127, 127), 2.5, 50)
    schedule_effect(24, swipe_forward, (127, 127, 127), 2.5, 50)
    schedule_effect(27, swipe_backward, (127, 127, 127), 2.5, 50)
    schedule_effect(30, rainbow, 3, 10)"""
    parse_labels("labels/overkill.txt")
    app.run(host="0.0.0.0", port=5000, debug=True)