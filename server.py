import os
import traceback
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from modules.engine_manager import EngineManager
from modules.engine_effects import EffectsEngine
from modules.engine_calibration import CalibrationEngine
from modules.engine_canvas import CanvasEngine
from modules.setup import SetupType
from flask_socketio import SocketIO, emit
from modules.config_manager import Config
from modules.log_manager import Log

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

LED_COUNT = 200
# determine if running on windows to run debug instead
if os.name == 'nt':
    #import sys
    pixels = DummyNeoPixel(18, LED_COUNT, auto_write=False, print_pixels=False)
else:
    from neopixel import NeoPixel
    import board
    # LED Configuration
    PIN = board.D18
    pixels = NeoPixel(PIN, LED_COUNT, auto_write=False)
app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
socketio = SocketIO(app)
# Globals for effect management

@app.route("/")
def page_index():
    return render_template("index.html", effects=list(effects_engine.effects.keys()))

@app.route("/effects")
def page_effects():
    return render_template("effects.html", effect_data=list(effects_engine.get_effect_data()))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/api/get_state", methods=["GET"])
def get_state():
    """Return the current state of the LED strip."""
    return jsonify(effects_engine.get_state())

@app.route("/api/set_effect", methods=["POST"])
def set_effect():
    """Set the current LED effect."""
    effect_name = request.json.get("effect")
    result = effects_engine.set_effect(effect_name)
    if result["status"] == "success":
        return jsonify(result)
    return jsonify(result), 404


@app.route("/api/get_parameters/<effect_name>", methods=["GET"])
def get_parameters(effect_name):
    """Get parameters for a specific effect."""
    result = effects_engine.get_parameters(effect_name)
    if "error" not in result:
        return jsonify(result)
    return jsonify(result), 404


@app.route("/api/set_parameter", methods=["POST"])
def set_parameter():
    """Set a specific parameter for the current effect."""
    request_data = request.json
    param_name = request_data.get("name")
    value = request_data.get("value")
    print(f"Setting parameter {param_name} to {value}")
    result = effects_engine.set_parameter(param_name, value)
    if result["status"] == "success":
        return jsonify(result)
    return jsonify(result), 400

# Setup API endpoints

# setup and calibration pages
@app.route("/setup")
def page_setup():
    setups = []
    tags = []
    if os.path.exists(effects_engine.SETUP_FOLDER):
        for file in os.listdir(effects_engine.SETUP_FOLDER):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(effects_engine.SETUP_FOLDER, file), "r") as f:
                        setup_data = json.load(f)
                        setup_type = setup_data.get("type", None)
                        if setup_type:
                            tags.append(setup_type)
                            setups.append(file[:-5])  # remove .json extension
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {file}: {traceback.format_exc()}")
                except Exception as e:
                    print(f"Error reading setup file {file}: {traceback.format_exc()}")

    # TODO: Handle case where no setups are available
    return render_template("setup.html", current_setup=Config().config.get("current_setup"), setup_data=zip(setups, tags))

@app.route("/setup/new")
def page_setup_new():
    return render_template("setup_new.html")

@app.route("/api/change_setup", methods=["POST"])
def change_setup():
    """Change the current setup."""
    request_data = request.json
    setup_name = request_data.get("name")
    if not setup_name:
        return jsonify({"status": "error", "message": "Setup name is required."}), 400
    try:
        manager.change_setup_by_name(setup_name)
        return jsonify({"status": "success", "message": f"Changed to setup '{setup_name}'."})
    except Exception as e:
        Log.error_exc("EngineManager", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# Calibration API endpoints

@app.route("/api/calibration/new_setup", methods=["POST"])
def new_setup():
    """Create a new calibration setup."""
    request_data = request.json
    setup_name = request_data.get("name")
    setup_type = request_data.get("type")
    led_count = request_data.get("led_count")
    # cast setup_type to SetupType enum if necessary
    print(f"Creating new setup: {setup_name}, type: {setup_type}, led_count: {led_count}")
    if not setup_name or not setup_type or not led_count:
        return jsonify({"status": "error", "message": "Setup name, type (str: 2D|3D) and led count are required."}), 400
    try:
        setup_type = SetupType(setup_type)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    try:
        calibration_engine.new_setup(setup_name, setup_type, led_count)
        return jsonify({"status": "success", "message": f"New setup '{setup_name}' created."})
    except Exception as e:
        Log.error_exc("CalibrationEngine", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/calibration/show_pixel", methods=["POST"])
def show_pixel():
    """Show a specific pixel in the calibration engine."""
    request_data = request.json
    index = request_data.get("index")
    color = request_data.get("color")
    if index is None or color is None:
        return jsonify({"status": "error", "message": "Index and color are required."}), 400
    try:
        calibration_engine.show_pixel(index, color)
        return jsonify({"status": "success", "message": f"Pixel {index} set to {color}."})
    except Exception as e:
        Log.error_exc("CalibrationEngine", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@socketio.on("photo_start")
def connect_calibration():
    """Connect to the calibration engine."""
    print("Client connected to calibration engine.")
    calibration_engine.start_shooting()

def take_photo_callback():
    """Call the photo event from the engine to the frontend."""
    socketio.emit("take_photo")

def send_image_callback(image_data, x, y):
    """Send the image data to the frontend."""
    socketio.emit("edit_photo_data", {"image": image_data, "x": x, "y": y})

@socketio.on("photo_data")
def receive_photo_data(data):
    calibration_engine.receive_photo_data(data)
    
@app.route("/api/calibration/upload_pixel_image", methods=["POST"])
def upload_pixel_image():
    """Save the current pixel image in the calibration engine."""
    image = request.files.get('image')
    index = request.form.get('index', type=int)
    if index is None or image is None:
        return jsonify({"status": "error", "message": "Pixel index and image are required."}), 400
    try:
        calibration_engine.upload_pixel_image(index, image)
        return jsonify({"status": "success", "message": f"Pixel {index} image saved."})
    except Exception as e:
        Log.error_exc("CalibrationEngine", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    
@socketio.on("led_position")
def receive_led_position(data):
    """Receive LED position data from the frontend."""
    x = data.get("x")
    y = data.get("y")
    if x is None or y is None:
        emit("led_position_error", {"status": "error", "message": "X and Y coordinates are required."})
        return
    try:
        calibration_engine.receive_image_position(x, y)
    except Exception as e:
        Log.error_exc("CalibrationEngine", e)
        emit("led_position_error", {"status": "error", "message": str(e)})

def setup_done_callback():
    """Callback for when the setup is done."""
    socketio.emit("setup_done")

# Canvas

@app.route("/api/get_coords", methods=["GET"])
def get_coords():
    """Get the coordinates of the LEDs in the canvas."""
    coords = manager.active_setup.coords if manager.active_setup else []
    return jsonify({"coords": coords})

@app.route("/canvas")
def page_canvas():
    """Render the canvas page."""
    return render_template("canvas.html")

@app.route("/api/canvas/get_pixels", methods=["GET"])
def get_pixels():
    pixel_list = canvas_engine.get_pixels()
    return jsonify({"pixels": pixel_list})

@app.route("/api/canvas/set_pixels", methods=["POST"])
def set_pixels():
    """Set the pixel colors in the canvas."""
    request_data = request.json
    pixel_list = request_data.get("pixels", [])
    if not pixel_list:
        Log.warn("CanvasEngine", "Client sent empty pixel list, ignoring.")
        return jsonify({"status": "error", "message": "Pixel data is required."}), 400
    try:
        canvas_engine.set_pixels(pixel_list)
        return jsonify({"status": "success", "message": "Pixels updated."})
    except Exception as e:
        Log.error_exc("CanvasEngine", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# Log API endpoints
@app.route("/logs")
def page_logs():
    """Render the logs page."""
    return render_template("logs.html")

@app.route("/api/get_log", methods=["GET"])
def get_logs():
    logs = Log.get_log_messages()
    return jsonify({"logs": logs})

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions globally and log them."""
    Log.error_exc("Server", e)
    return jsonify({"status": "error", "message": f"Error: {traceback.format_exc()}"}), 500
    

if __name__ == "__main__":
    manager = EngineManager()
    effects_engine = EffectsEngine(pixels, manager.active_setup)
    calibration_engine = CalibrationEngine(pixels, take_photo_callback, send_image_callback, setup_done_callback)
    canvas_engine = CanvasEngine(pixels)

    # IMPORTANT! Always register the effects engine first, as it is the main engine.
    manager.register_engine(effects_engine)
    manager.register_engine(calibration_engine)
    manager.register_engine(canvas_engine)
    Log.info("Server", "Starting Spectraforge server...")
    try:
        if os.name == "nt":
            app.run(host="0.0.0.0", port=5000)
        else:            
            app.run(host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'))
    finally:
        manager.active_engine.on_disable()
