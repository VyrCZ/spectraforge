from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import json
import sys, os, importlib.util, inspect
from pathlib import Path
from modules.lightshow_effects import LightshowEffects
from modules.config_manager import Config

class LightshowEngine(AudioEngine):
    """
    A test engine implementation for testing purposes.
    """

    def __init__(self, renderer, active_setup, ready_callback):
        super().__init__(renderer, ready_callback)
        self.lightshow_data = None
        self.active_setup = active_setup
        self.coords = active_setup.coords

    def load_lightshow(self, lightshow_file):
        """Load the lightshow JSON file and extract the audio file path."""
        # get the performance mode
        performance_mode = Config.get("performance_mode", "normal")
        if performance_mode == "low":
            self.FPS = 20
        elif performance_mode == "high":
            self.FPS = 60
        else:
            self.FPS = 30
        try:
            with open(lightshow_file, "r") as f:
                data = json.load(f)
                self.lightshow_data = data
                audio_file = data.get("audio_file")
                if not audio_file:
                    raise ValueError("No audio file specified in the lightshow JSON.")
                Log.info("LightshowEngine", f"Loaded lightshow: {lightshow_file}")
                return audio_file
        except Exception as e:
            Log.error("LightshowEngine", f"Failed to load lightshow file: {e}")
            return None

    def on_audio_load(self, audio_file: str):
        """Load the lightshow data and prepare for playback."""
        lightshow_file = os.path.join("lightshows", f"{os.path.splitext(audio_file)[0]}.json")
        audio_file_path = self.load_lightshow(lightshow_file, )
        if audio_file_path:
            super().on_audio_load(audio_file_path)
            Log.info("LightshowEngine", f"Audio file loaded: {audio_file_path}")
        else:
            Log.error("LightshowEngine", "Failed to load lightshow or audio file.")

    def on_enable(self):
        Log.info("LightshowEngine", "LightshowEngine enabled.")

    def on_disable(self):
        Log.info("LightshowEngine", "LightshowEngine disabled.")

    def _load_effects(self):
        EFFECT_DIR = "lightshow_effects"
        self.effects_dir = Path(EFFECT_DIR)
        self.registry = {}
        self._load_all()
 
    def _load_all(self):
        for py in self.effects_dir.glob("*.py"):
            self._import_file(py)
    
    def _import_file(self, path: Path):
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, LightshowEffects) and cls is not LightshowEffects:
                self._register_class(cls)

    def process_lightshow(self):
        """
        Steps:
        (have effects loaded)
        1. ignore incompatible effects (3D on 2D setup and vice versa)
        2. separate timeline into layer lists
        3. for each layer:
        - apply all filters to the layers beneath
        - process all effects in the layer
        4. fill None (transparent) with black at the end
        """
        # sort the timeline by layers
        layer_count = self.lightshow_data.get("editorData", {}).get("layerCount", 1)
        layers = [[] for _ in range(layer_count)]
        # put all timeline items into their respective layers
        for item in self.lightshow_data.get("timeline", []):
            layer_index = item.get("layer", 0)
            if layer_index < layer_count:
                layers[layer_index].append(item)
        # sort layers by their start time (should be already sorted, but just in case)
        for layer in layers:
            layer.sort(key=lambda x: x.get("start", 0))
        # apply effects for now (TODO: add filters, not implemented yet)
        frames = [[[None] * len(self.coords) for _ in range(self.FPS * self.audio_length)]] # frames filled with None (transparent)
        for layer in layers:
            for item in layer:
                effect_name = item.get("effect")
                if effect_name:
                    if effect_name in self.registry:
                        effect_func = self.registry[effect_name]
                        params = item.get("parameters", {})
                        # calculate the number of steps
                        start_time = item.get("start", 0)
                        end_time = item.get("end", 0)
                        if end_time <= start_time:
                            Log.warning("LightshowEngine", f"Effect {effect_name} [{start_time}-{end_time}] has invalid end time, skipping.")
                            continue
                        duration = end_time - start_time
                        steps = int(duration * self.FPS)
                        # call the effect function
                        Log.info("LightshowEngine", f"Processing effect {effect_name} with params {params}")
                        effect_output = effect_func(steps, **params)
                        # slice the frames to give the effect function the correct time range
                        start_frame = int(start_time * self.FPS)
                        # insert output directly into frames (no need for having lists for each layer in this case)
                        for i, frame in enumerate(effect_output):
                            if start_frame + i < len(frames):
                                frames[start_frame + i] = frame
                    else:
                        Log.warning("LightshowEngine", f"Effect {effect_name} not found or not registered.")
                else:
                    Log.warning("LightshowEngine", "No effect key found in item, probably a filter, skipping for now.")
        # fill None (transparent) with black at the end
        for i in range(len(frames)):
            frames[i] = [color if color is not None else (0, 0, 0) for color in frames[i]]
        # return the processed frames
        return frames


    def _register_class(self, cls):
        ns = getattr(cls, "__namespace__", "") or ""
        inst = cls(self.coords)
        for name, fn in inspect.getmembers(inst, inspect.ismethod):
            if hasattr(fn, "__is_effect__"):
                key = f"{ns + ':' if ns else ''}{name}"
                self.registry[key] = fn


