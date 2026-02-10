"""
Utilities for creating placeholder/default files when nothing is present.
"""
import os
import json
from modules.log_manager import Log
from modules.config_manager import Config

def check():
    functions = [
        _check_setup,
        _check_effects,
        _check_sandbox,
        _check_config
    ]

    for func in functions:
        try:
            func()
        except Exception as e:
            Log.error_exc("PlaceholderManager", e)
            raise e

SETUP_DIR = "config/setups"
CONFIG_FILE = "config/server_config.json"
EFFECTS_DIR = "effects"
SANDBOX_DIR = "sandbox"
DEFAULT_EFFECT =\
"""from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time

class Breathing(LightEffect):
    def __init__(self, renderer, coords):
        # Init the effect
        super().__init__(renderer, coords, "Breathing", EffectType.UNIVERSAL)
        # Parameters will work in sandbox, however only the default values will be used and can't be changed at the moment
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 50, min=1, max=500, step=1)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.off_time = 0.5 # Time to wait when the effect is fully faded out
        self.t = 0 # The timer variable
        self.dir = 1 # Direction of the breathing effect (1 for fading in, -1 for fading out)

    def update(self):
        # Update the time variable
        self.t += self.dir * self.fade_speed.get() / 10000
        # Change direction if the breathing effect is fully faded in or out
        if self.t >= 1:
            self.dir = -1
        elif self.t <= 0:
            self.dir = 1
            time.sleep(self.off_time)
        # Update the leds and the renderer
        for i in range(len(self.renderer)):
            self.renderer[i] = [mu.clamp(int(channel * self.t), 0, 255) for channel in self.color.get()]
        self.renderer.show()"""

def _generate_default_effect():
    if not os.path.exists(EFFECTS_DIR):
        os.makedirs(EFFECTS_DIR, exist_ok=True)
    with open(os.path.join(EFFECTS_DIR, "breathing.py"), "w") as f:
        f.write(DEFAULT_EFFECT)

def _generate_default_sandbox():
    if not os.path.exists(SANDBOX_DIR):
        os.makedirs(SANDBOX_DIR, exist_ok=True)
    with open(os.path.join(SANDBOX_DIR, "default.py"), "w") as f:
        f.write(DEFAULT_EFFECT)

def _generate_default_setup():
    if not os.path.exists(SETUP_DIR):
        os.makedirs(SETUP_DIR, exist_ok=True)
    coordinates = []
    for x in range(10):
        for y in range(10):
            coordinates.append([x, y, 0])
    default_setup = {
        "type": "2d",
        "coordinates": coordinates
    }
    with open(os.path.join(SETUP_DIR, "default_setup.json"), "w") as f:
        json.dump(default_setup, f, indent=4)

def _check_setup():
    """
    Check if some setup file exists.
    """
    if not os.path.exists(SETUP_DIR):
        os.makedirs(SETUP_DIR, exist_ok=True)
    else:
        # check if there is any setup file
        for file in os.listdir(SETUP_DIR):
            if file.endswith(".json"):
                return
    # no valid setup file found, create a default one
    Log.info("PlaceholderManager", "No setup file found, creating a default one.")
    _generate_default_setup()

def _check_effects():
    if not os.path.exists(EFFECTS_DIR):
        os.makedirs(EFFECTS_DIR, exist_ok=True)
    else:
        # check if there is any effect file
        for file in os.listdir(EFFECTS_DIR):
            if file.endswith(".py"):
                return
    # no valid effect file found, create a default one
    Log.info("PlaceholderManager", "No effect file found, creating a default one.")
    _generate_default_effect()

def _check_sandbox():
    if not os.path.exists(SANDBOX_DIR):
        os.makedirs(SANDBOX_DIR, exist_ok=True)
    else:
        # check if there is any sandbox file
        for file in os.listdir(SANDBOX_DIR):
            if file.endswith(".py"):
                return
    # no valid sandbox file found, create a default one
    Log.info("PlaceholderManager", "No sandbox file found, creating a default one.")
    _generate_default_sandbox()

def _pick_first_file_or_default(directory, file_extension, default_name):
    if not os.path.exists(directory):
        return default_name
    for file in os.listdir(directory):
        if file.endswith(file_extension):
            return file[:-len(file_extension)]
    return default_name

def _check_config():
    folder_selections = {
        "current_setup": (SETUP_DIR, ".json", "default_setup"),
        "current_effect": (EFFECTS_DIR, ".py", "breathing"),
        "sandbox_opened_file": (SANDBOX_DIR, ".py", "default")
    }
    for key, (directory, extension, default_name) in folder_selections.items():
        if key not in Config().config:
            Log.info("PlaceholderManager", f"Config key '{key}' not found, setting it to a default value.")
            Config().config[key] = _pick_first_file_or_default(directory, extension, default_name)
    placeholder_values = {
        "brightness": 1.0,
        "performance_mode": "high",
        "enhance_colors": True
    }
    for key, value in placeholder_values.items():
        if key not in Config().config:
            Log.info("PlaceholderManager", f"Config key '{key}' not found, setting it to a default value.")
            Config().config[key] = value
    Config().save()