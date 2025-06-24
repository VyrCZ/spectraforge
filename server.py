import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from modules.engine_manager import EngineManager
from modules.engine_effects import EffectsEngine
from modules.engine_calibration import CalibrationEngine

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

@app.route("/")
def page_index():
    return render_template("index.html", effects=list(effects_engine.effects.keys()))

@app.route("/effects")
def page_effects():
    return render_template("effects.html", effects=list(effects_engine.effects.keys()))


# setup and calibration pages
@app.route("/setup")
def page_setup():
    setups = []
    if os.path.exists(effects_engine.SETUP_FOLDER):
        setups = [f[:-5] for f in os.listdir(effects_engine.SETUP_FOLDER) if f.endswith(".json")]
    # TODO: Handle case where no setups are available
    return render_template("setup.html", current_setup=effects_engine.config.get("current_setup"), setups=setups)

@app.route("/setup/new")
def page_setup_new():
    return render_template("setup_new.html")

@app.route("/start_calibration")
def page_start_calibration():
    """Start the calibration process."""
    calibration_engine.start_calibration()
    return jsonify({"status": "success", "message": "Calibration started."})
    

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/get_state", methods=["GET"])
def get_state():
    """Return the current state of the LED strip."""
    return jsonify(effects_engine.get_state())

@app.route("/set_effect", methods=["POST"])
def set_effect():
    """Set the current LED effect."""
    effect_name = request.json.get("effect")
    result = effects_engine.set_effect(effect_name)
    if result["status"] == "success":
        return jsonify(result)
    return jsonify(result), 404


@app.route("/get_parameters/<effect_name>", methods=["GET"])
def get_parameters(effect_name):
    """Get parameters for a specific effect."""
    result = effects_engine.get_parameters(effect_name)
    if "error" not in result:
        return jsonify(result)
    return jsonify(result), 404


@app.route("/set_parameter", methods=["POST"])
def set_parameter():
    """Set a specific parameter for the current effect."""
    request_data = request.json
    param_name = request_data.get("name")
    value = request_data.get("value")
    result = effects_engine.set_parameter(param_name, value)
    if result["status"] == "success":
        return jsonify(result)
    return jsonify(result), 400

if __name__ == "__main__":
    manager = EngineManager()
    effects_engine = EffectsEngine(pixels)
    calibration_engine = CalibrationEngine(pixels)
    # IMPORTANT! Always register the effects engine first, as it is the main engine.
    manager.register_engine(effects_engine)
    manager.register_engine(calibration_engine)
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        effects_engine.disable_engine("effects")
