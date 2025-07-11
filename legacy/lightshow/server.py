from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from threading import Thread, Event
import os
import time
from neopixel import NeoPixel
import board
pixels = NeoPixel(board.D18, 200, auto_write=False)
from bisect import bisect_right
import pickle

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

# Server configuration
AUDIO_FILE_PATH = "static/audio"
song_name = "cascade"
BPM = 174  # Beats per minute
offset = 0.2
beat_interval = 60 / BPM  # Time between beats in seconds
start_time = None  # The server's internal start time
current_time = 0  # Server's calculated playback time
last_sync_time = 0  # Last sync timestamp received from the client
stop_event = Event()
event_thread = None
hue = 0
color_states = {}

app = Flask(__name__)
socketio = SocketIO(app)


def play_effects():
    """Shows the precached LED states at the correct times, avoiding redundant updates."""
    global next_beat_time, current_time, start_time

    timestamps = sorted(color_states.keys())
    last_shown_state = None  # Keep track of the last displayed state
    last_shown_time = None   # Track the timestamp of the last displayed state

    if start_time is None:
        start_time = time.time()
    print("Starting event runner.")
    while not stop_event.is_set():
        now = time.time() - start_time + offset
        idx = bisect_right(timestamps, now) - 1
        print(f"I should be at {now} and I am showing {timestamps[idx]}")
        if idx >= 0:
            closest_time = timestamps[idx]

            # Check if the state at `closest_time` is different from the last shown state
            if closest_time != last_shown_time:
                colors = color_states[closest_time]

                # Set LED colors only if the state is different
                if colors != last_shown_state:
                    for i, color in enumerate(colors):
                        pixels[i] = color
                    pixels.show()

                    # Update the last shown state and timestamp
                    last_shown_state = colors
                    last_shown_time = closest_time

        time.sleep(0.01)  # Minimal delay to prevent high CPU usage

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
        event_thread = Thread(target=play_effects)
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

if __name__ == "__main__":
    color_states = pickle.load(open(f"performances/{song_name}.pkl", "rb"))
    print(f"Loaded {len(color_states)} states for {song_name}.")
    app.run(host="0.0.0.0", port=5000, debug=True)