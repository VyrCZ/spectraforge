from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import json
import sys, os, importlib.util, inspect
from pathlib import Path
from modules.lightshow_effects import LightshowEffects
from modules.config_manager import Config

EFFECTS_DIR = Path("lightshow_effects")

class LightshowSettings:
    def __init__(self, fps: int = 30):
        self.FPS = fps  # Default FPS setting

class RegistryInstance:
    """
    Instances of all lightshow effects, loaded for a specific coordinate setup.
    """

    def __init__(self, coords: list[tuple[int, int, int]]):
        self.coords = coords
        self.registry = {}
        self.init_registry()

    def init_registry(self):
        # just initialise; _load_all doesn't return anything
        self._load_all()

    def _load_all(self):
        for py in EFFECTS_DIR.glob("*.py"):
            self._import_file(py)

    def _import_file(self, path: Path):
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, LightshowEffects) and cls is not LightshowEffects:
                self._register_class(cls)

    def _register_class(self, cls):
        ns = getattr(cls, "__namespace__", "") or ""
        inst = cls(self.coords)
        for name, fn in inspect.getmembers(inst, inspect.ismethod):
            if hasattr(fn, "__is_effect__"):
                key = f"{ns + ':' if ns else ''}{name}"
                self.registry[key] = fn

def process_lightshow(registry: RegistryInstance, lightshow_data: dict, settings: LightshowSettings):
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
    layer_count = lightshow_data.get("editor_data", {}).get("layer_count", 1)
    layers = [[] for _ in range(layer_count)]
    timeline = lightshow_data.get("timeline", [])
    audio_length = max(item.get("end", 0) for item in timeline) if timeline else 0
    # put all timeline items into their respective layers
    for item in timeline:
        layer_index = item.get("layer", 0)
        if layer_index < layer_count:
            layers[layer_index].append(item)
    # sort layers by their start time (should be already sorted, but just in case)
    for layer in layers:
        layer.sort(key=lambda x: x.get("start", 0))
    # apply effects for now (TODO: add filters, not implemented yet)
    frames = [[None] * len(registry.coords) for _ in range(int(settings.FPS * audio_length))] # frames filled with None (transparent)
    for layer in layers:
        for item in layer:
            effect_name = item.get("effect")
            if effect_name:
                # lookup in the registry mapping stored on the RegistryInstance
                if effect_name in registry.registry:
                    effect_func = registry.registry[effect_name]
                    params = item.get("parameters", {})
                    # convert hex to RGB
                    for key, value in params.items():
                        if isinstance(value, str) and value.startswith("#"):
                            params[key] = tuple(int(value[i:i+2], 16) for i in (1, 3, 5))  # convert hex to RGB tuple
                    # calculate the number of steps
                    start_time = item.get("start", 0)
                    end_time = item.get("end", 0)
                    if end_time <= start_time:
                        Log.warn("LightshowEngine", f"Effect {effect_name} [{start_time}-{end_time}] has invalid end time, skipping.")
                        continue
                    duration = end_time - start_time
                    steps = int(duration * settings.FPS)
                    # call the effect function
                    Log.info("LightshowEngine", f"Processing effect {effect_name} with params {params}")
                    effect_output = effect_func(steps, **params)
                    # slice the frames to give the effect function the correct time range
                    start_frame = int(start_time * settings.FPS)
                    # insert output directly into frames
                    for i, frame in enumerate(effect_output):
                        frame_index = start_frame + i
                        if frame_index < len(frames):
                            for led_index, color in enumerate(frame):
                                if led_index < len(frames[frame_index]) and color is not None:
                                    frames[frame_index][led_index] = color
                else:
                    Log.warn("LightshowEngine", f"Effect {effect_name} not found or not registered.")
            else:
                Log.warn("LightshowEngine", "No effect key found in item, probably a filter, skipping for now.")
    # fill None (transparent) with black at the end
    for i in range(len(frames)):
        frames[i] = [color if color is not None else (0, 0, 0) for color in frames[i]]
    # return the processed frames
    return frames