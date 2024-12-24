import os
import importlib
from flask import Flask, render_template, request, jsonify, send_from_directory
from threading import Thread
from neopixel import NeoPixel
import board
import json

# set working directory to the directory of this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

# LED Configuration
LED_COUNT = 200  # Adjust to your LED strip
PIN = board.D18
pixels = NeoPixel(PIN, LED_COUNT, auto_write=False)

# Flask app
app = Flask(__name__)

# Globals for effect management
effects = {}
current_effect = None
running = True
data = {}

data = json.load(open("server_data.json"))
print(data)

def save_data():
    print(f"Saving data: {data}")
    json.dump(data, open("server_data.json", "w"))

def get_effect_name(effect):
    for name, eff in effects.items():
        if isinstance(effect, eff):
            return name

def load_effects(folder="effects"):
    """Dynamically load all effect scripts."""
    global effects
    effects = {}
    for filename in os.listdir(folder):
        if filename.endswith(".py") and filename != "base_effect.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"{folder}.{module_name}")
            for attr in dir(module):
                cls = getattr(module, attr)
                if isinstance(cls, type) and issubclass(cls, module.LightEffect) and cls is not module.LightEffect:
                    effects[module_name] = cls
    return effects


def effect_runner():
    """Runs the current effect in a loop."""
    global current_effect, running
    while running:
        if current_effect:
            #print(f"Running effect {current_effect.__class__.__name__}")
            current_effect.update()

@app.route("/")
def index():
    return render_template("index.html", effects=list(effects.keys()))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/get_state", methods=["GET"])
def get_state():
    """Return the current state of the LED strip."""
    # return current effect and current values of all parameters
    return jsonify({
        "current_effect": get_effect_name(current_effect) if current_effect else list(effects.keys())[0],
        "parameters": {name: param.get() for name, param in current_effect.parameters.items()} if current_effect else None
    })

@app.route("/set_effect", methods=["POST"])
def set_effect():
    """Set the current LED effect."""
    global current_effect
    effect_name = request.json.get("effect")
    print("Setting effect to", effect_name)
    if effect_name in effects:
        current_effect = effects[effect_name](pixels, coords)
        data["current_effect"] = effect_name
        for param in current_effect.parameters.values():
            last_value = data["parameters"].get(effect_name, {}).get(param.name, None)
            if last_value is not None:
                param.set(last_value)    
        save_data()
        print(f"Set effect to {effect_name}")
        return jsonify({"status": "success", "current_effect": effect_name})
    return jsonify({"status": "error", "message": "Effect not found"}), 404


@app.route("/get_parameters/<effect_name>", methods=["GET"])
def get_parameters(effect_name):
    """Get parameters for a specific effect."""
    if effect_name in effects:
        effect_class = effects[effect_name]
        parameters = effect_class(pixels, coords).get_parameters()
        return jsonify(parameters)
    return jsonify({"error": "Effect not found"}), 404


@app.route("/set_parameter", methods=["POST"])
def set_parameter():
    """Set a specific parameter for the current effect."""
    global current_effect, data
    request_data = request.json
    param_name = request_data.get("name")
    value = request_data.get("value")

    if current_effect and param_name in current_effect.parameters:
        # Ensure "parameters" dictionary exists
        if "parameters" not in data:
            data["parameters"] = {}

        # Ensure the current effect's parameters dictionary exists
        effect_name = get_effect_name(current_effect)
        if effect_name not in data["parameters"]:
            data["parameters"][effect_name] = {}

        # Update the parameter value
        current_effect.parameters[param_name].set(value)
        data["parameters"][effect_name][param_name] = value
        save_data()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid parameter"}), 400

coords = []
if __name__ == "__main__":
    # load coordinates.txt
    with open('coordinates.txt', 'r') as f:
        for coord in f.readlines():
            coords.append([int(value) for value in coord.strip().split(',')])
    load_effects()
    # set current effect to the effect with the name stored in data
    current_effect = None
    if data.get("current_effect") in effects:
        current_effect = effects[data.get("current_effect")](pixels, coords)
        for param in current_effect.parameters.values():
            if data["parameters"].get(data["current_effect"], {}).get(param.name, None) is not None:
                print(f"(Effect {get_effect_name(current_effect)}) Got last value for {param.name}: {data['parameters'][data['current_effect']][param.name]}")
                param.set(data["parameters"][data["current_effect"]][param.name])
    if not current_effect:
        current_effect = list(effects.values())[0](pixels, coords)
        data["current_effect"] = list(effects.keys())[0]
        save_data()
    runner_thread = Thread(target=effect_runner, daemon=True)
    runner_thread.start()

    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        running = False
        save_data()
        pixels.fill((0, 0, 0))
        pixels.show()
