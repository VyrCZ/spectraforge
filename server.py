import os
import importlib
from flask import Flask, render_template, request, jsonify, send_from_directory
from threading import Thread
import json

# set working directory to the directory of this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class DummyNeoPixel():
    """
    A replacement for the NeoPixel class when running on Windows or for debugging purposes.
    This class simulates the behavior of NeoPixel without actual hardware interaction.
    """
    def __init__(self, pin, num_leds, auto_write, print_pixels=True):
        self.num_leds = num_leds
        self.pixels = [(0, 0, 0)] * num_leds
        self.auto_write = auto_write
        self.print_pixels = print_pixels

    def __setitem__(self, key, value):
        self.pixels[key] = value

    def fill(self, color):
        for i in range(self.num_leds):
            self.pixels[i] = color

    def show(self):
        if self.print_pixels:
            print(self.pixels)

    def __len__(self):
        return self.num_leds
    
class SetupType:
    TWO_DIMENSIONAL = "2D"
    THREE_DIMENSIONAL = "3D"
    
class Setup:
    """
    A class holding calibration data for the current setup of the LED strip.
    """
    def __init__(self, name: str, type: SetupType, coords: list[list[int]], creation_date: str | None = None):
        self.name = name
        self.creation_date = creation_date
        self.type = type
        self.coords = coords

    @classmethod
    def from_json(cls, name, data: dict):
        """
        Create a Setup instance from a JSON dictionary.
        """
        return cls(
            name=name, # name is not stored in the JSON, it's the file name
            type=data["type"],
            coords=data["coordinates"],
            creation_date=data.get("creation_date", None)
        )

# determine if running on windows to run debug instead
if os.name == 'nt':
    #import sys
    LED_COUNT = 200
    pixels = DummyNeoPixel(18, LED_COUNT, auto_write=False, print_pixels=False)
    app = Flask(__name__)
else:
    from neopixel import NeoPixel
    import board
    # LED Configuration
    LED_COUNT = 200
    PIN = board.D18
    pixels = NeoPixel(PIN, LED_COUNT, auto_write=False)
    app = Flask(__name__)

# Globals for effect management
effects = {}
current_effect = None
running = True
CONFIG_PATH = "config/server_config.json"
SETUP_FOLDER = "config/setups"

# file storing current effect, parameters and current setup
config = {}

config = json.load(open(CONFIG_PATH))
# load current setup
setup_dir = json.load(open(os.path.join(SETUP_FOLDER, config.get("current_setup")+".json")))
setup = Setup.from_json(config.get("current_setup"), setup_dir)

#print(data)

def save_data():
    #print(f"Saving data: {data}")
    json.dump(config, open(CONFIG_PATH, "w"))

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
def page_index():
    return render_template("index.html", effects=list(effects.keys()))

@app.route("/effects")
def page_effects():
    return render_template("effects.html", effects=list(effects.keys()))


# setup and calibration pages
@app.route("/setup")
def page_setup():
    setups = []
    if os.path.exists(SETUP_FOLDER):
        setups = [f[:-5] for f in os.listdir(SETUP_FOLDER) if f.endswith(".json")]
    # TODO: Handle case where no setups are available
    return render_template("setup.html", current_setup=config.get("current_setup"), setups=setups)

@app.route("/setup/new")
def page_setup_new():
    return render_template("setup_new.html")

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
        config["current_effect"] = effect_name
        for param in current_effect.parameters.values():
            last_value = config["parameters"].get(effect_name, {}).get(param.name, None)
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
    global current_effect, config
    request_data = request.json
    param_name = request_data.get("name")
    value = request_data.get("value")

    if current_effect and param_name in current_effect.parameters:
        # Ensure "parameters" dictionary exists
        if "parameters" not in config:
            config["parameters"] = {}

        # Ensure the current effect's parameters dictionary exists
        effect_name = get_effect_name(current_effect)
        if effect_name not in config["parameters"]:
            config["parameters"][effect_name] = {}

        # Update the parameter value
        current_effect.parameters[param_name].set(value)
        config["parameters"][effect_name][param_name] = value
        save_data()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid parameter"}), 400

coords = []
if __name__ == "__main__":
    coords = setup.coords
    load_effects()
    # set current effect to the effect with the name stored in data
    current_effect = None
    if config.get("current_effect") in effects:
        current_effect = effects[config.get("current_effect")](pixels, coords)
        for param in current_effect.parameters.values():
            if config["parameters"].get(config["current_effect"], {}).get(param.name, None) is not None:
                print(f"(Effect {get_effect_name(current_effect)}) Got last value for {param.name}: {config['parameters'][config['current_effect']][param.name]}")
                param.set(config["parameters"][config["current_effect"]][param.name])
    if not current_effect:
        current_effect = list(effects.values())[0](pixels, coords)
        config["current_effect"] = list(effects.keys())[0]
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
