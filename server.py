import os
import traceback
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from modules.engine_manager import EngineManager
from modules.engine_effects import EffectsEngine
from modules.engine_calibration import CalibrationEngine
from modules.engine_canvas import CanvasEngine
from modules.engine_sandbox import SandboxEngine
from modules.engine_visualiser import VisualiserEngine
from modules.engine_lightshow import LightshowEngine
from modules.setup import SetupType
from flask_socketio import SocketIO, emit
from modules.config_manager import Config
from modules.log_manager import Log
from modules.led_renderer import LEDRenderer
import modules.upload_files as upload
from modules.placeholder_manager import check as placeholder_check

# set working directory to the directory of this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))


app = Flask(__name__)
app.jinja_env.globals.update(zip=zip) # allows using zip in Jinja templates
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
    return send_from_directory(os.path.join(app.root_path, 'static', "icons"), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    
@app.route("/sandbox")
def page_sandbox():
    """Render the sandbox page."""
    return render_template("sandbox.html", files=sandbox_engine.list_files())

@app.route("/api/sandbox/set_file", methods=["POST"])
def set_sandbox_file():
    """Set the current file in the sandbox."""
    request_data = request.json
    file_name = request_data.get("file_name")
    if not file_name:
        return jsonify({"status": "error", "message": "File name is required."}), 400
    try:
        sandbox_engine.set_file(file_name)
        return jsonify({"status": "success", "message": f"Sandbox file set to '{file_name}'."})
    except Exception as e:
        Log.error_exc("SandboxEngine", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/settings")
def page_settings():
    """Render the settings page."""
    return render_template("settings.html", brightness=Config().config.get("brightness", 1)*100, performance_mode=Config().config.get("performance_mode", "normal"))

@app.route("/api/settings/set_setting", methods=["POST"])
def set_setting():
    """Set a specific setting in the server."""
    request_data = request.json
    valid_settings = ["brightness", "performance_mode"]
    for setting_name, setting_value in request_data.items():
        Log.debug("Server", f"Setting {setting_name} to {setting_value}")
        if setting_name not in valid_settings:
            Log.warn("Server", f"Invalid setting '{setting_name}' with value '{setting_value}'. Valid settings are: {valid_settings}")
            return jsonify({"status": "error", "message": f"Invalid settings. List: {valid_settings}"}), 400
        
        if setting_name == "brightness":
            try:
                renderer.set_brightness(int(setting_value)/100)  # Convert percentage to float
                return jsonify({"status": "success", "message": f"Brightness set to {setting_value}."})
            except Exception as e:
                Log.error_exc("CalibrationEngine", e)
                return jsonify({"status": "error", "message": str(e)}), 500
        elif setting_name == "performance_mode":
            try:
                Config().config["performance_mode"] = setting_value
                Config().save()
                return jsonify({"status": "success", "message": f"Performance mode set to {setting_value}."})
            except Exception as e:
                Log.error_exc("CalibrationEngine", e)
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

@app.route("/audio")
def page_audio():
    """Render the audio page."""
    return render_template("audio.html", audio_list=os.listdir(os.path.join(app.root_path, 'audio')))

# Audio API
@app.route("/api/audio/get_audio_files", methods=["GET"])
def get_audio_files():
    """Get a list of available audio files."""
    audio_folder = os.path.join(app.root_path, 'audio')
    try:
        audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3') or f.endswith('.wav') or f.endswith('.ogg')]
        return jsonify({"status": "success", "files": audio_files})
    except Exception as e:
        Log.error_exc("Server", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/audio/<path:filename>")
def send_audio(filename):
    """Send an audio file from the audio directory."""
    audio_folder = os.path.join(app.root_path, 'audio')
    return send_from_directory(audio_folder, filename)

# only the loading functions are different, the playback functions are the same
@socketio.on("audio_client_connected")
def audio_client_connected(data):
    # get file name from data
    """Handle client connection for audio playback."""
    audio_file = data.get("audio_file")
    if not audio_file:
        Log.warn("AudioEngine", "No audio file provided by client.")
        emit("audio_error", {"status": "error", "message": "Audio file is required."})
        return
    visualiser_engine.on_audio_load(audio_file)

@app.route("/lightshows")
def page_lightshows():
    """Render the lightshows page."""
    # list all lightshow files which have their audio file in the audio folder
    lightshow_folder = os.path.join(app.root_path, 'lightshows')
    if not os.path.exists(lightshow_folder):
        os.makedirs(lightshow_folder)
    audio_folder = os.path.join(app.root_path, 'audio')
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
    audio_files = []
    lightshow_files = []
    for f in os.listdir(lightshow_folder):
        # load the json and get audio_file
        if f.endswith('.json'):
            Log.debug("Server", f"Checking lightshow file: {f}")
            with open(os.path.join(lightshow_folder, f), 'r') as json_file:
                data = json.load(json_file)
                audio_file = data.get("audio_file")
                if audio_file:
                    lightshow_files.append(f[:-5])  # remove file extension
    return render_template("lightshows.html", lightshow_files=lightshow_files)

@socketio.on("lightshow_client_connected")
def lightshow_client_connected(data):
    """Handle client connection for lightshow playback."""
    lightshow_file = data.get("lightshow_file")
    if not lightshow_file:
        Log.warn("LightshowEngine", "No lightshow file provided by client.")
        emit("lightshow_error", {"status": "error", "message": "Lightshow file is required."})
        return
    lightshow_engine.on_audio_load(lightshow_file)

def audio_engine_ready(audio_file = None):
    """Callback for when the audio engine is ready for playback."""
    socketio.emit("audio_ready", {"audio_file": audio_file})

@socketio.on("audio_play")
def on_audio_play():
    Log.info("Server", "Audio play played by user.")
    manager.active_engine.on_audio_play()

@socketio.on("audio_pause")
def on_audio_pause():
    Log.info("Server", "Audio paused by user.")
    manager.active_engine.on_audio_pause()

@socketio.on("audio_stop")
def on_audio_stop():
    Log.info("Server", "Audio stopped by user.")
    manager.active_engine.on_audio_stop()

@socketio.on("audio_seek")
def on_audio_seek(data):
    Log.info("Server", "Audio seek requested by user.")
    time_pos = data.get("time")
    manager.active_engine.on_audio_seek(time_pos)

@app.route("/upload")
def page_upload():
    """Render the upload page."""
    return render_template("upload.html")

@app.route("/api/upload", methods=["POST"])
def upload_file():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"success": False, "error": "No files provided."}), 400

    result = upload.handle_file_upload(files)
    return jsonify({"success": result})

if __name__ == "__main__":
    placeholder_check()
    manager = EngineManager()
    renderer = LEDRenderer(manager.active_setup)
    effects_engine = EffectsEngine(renderer, manager.active_setup)
    calibration_engine = CalibrationEngine(renderer, take_photo_callback, send_image_callback, setup_done_callback)
    canvas_engine = CanvasEngine(renderer)
    sandbox_engine = SandboxEngine(renderer, manager.active_setup)
    visualiser_engine = VisualiserEngine(renderer, manager.active_setup, audio_engine_ready)
    lightshow_engine = LightshowEngine(renderer, manager.active_setup, audio_engine_ready)


    # IMPORTANT! Always register the effects engine first, as it is the main engine.
    manager.register_engine(effects_engine)
    manager.register_engine(calibration_engine)
    manager.register_engine(canvas_engine)
    manager.register_engine(sandbox_engine)
    manager.register_audio_engine(visualiser_engine)
    manager.register_audio_engine(lightshow_engine)
    Log.info("Server", "Starting Spectraforge server...")
    try:
        if os.name == "nt":
            app.run(host="0.0.0.0", port=5000)
        else:            
            app.run(host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'))
    finally:
        manager.active_engine.on_disable()
