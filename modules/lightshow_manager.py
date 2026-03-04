from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import json
import sys, os, importlib.util, inspect
from pathlib import Path
from modules.lightshow_effects import LightshowEffects
from modules.config_manager import Config
import time
import modules.caching as caching
from typing import Any

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
    Refactored Lightshow Compiler (Alpha Blending Edition)
    
    1. Initializes the canvas as solid BLACK (0,0,0).
    2. Stacks layers from bottom to top.
    3. Blends new effects onto the existing canvas using Alpha Compositing.
    4. Returns a standard list of RGB tuples (Alpha is baked in).
    """

    def _canonicalize(obj: Any) -> Any:
        """
        Recursively canonicalize the object for consistent hashing.
        Sorts dictionaries by keys
        """
        if isinstance(obj, dict):
            return {k: _canonicalize(obj[k]) for k in sorted(obj)}
        if isinstance(obj, (list, tuple)):
            return [_canonicalize(v) for v in obj]
        return obj
    
    def compute_lightshow_hash(registry: RegistryInstance, lightshow_data: dict, settings: LightshowSettings) -> str:
        # normalize the lightshow data
        canon = _canonicalize(lightshow_data)
        j = json.dumps(canon, separators=(",", ":"), ensure_ascii=False)
        return caching.hash_data(j + str(settings.FPS) + str(registry.coords))

    process_start_time = time.time()
    # --- 0. CHECK CACHE FIRST ---
    file_cache_key = compute_lightshow_hash(registry, lightshow_data, settings)
    Log.debug("LightshowEngine", f"Cache key: {file_cache_key}")
    cached_result = caching.get_cache_by_name("lightshow_engine", file_cache_key)
    if cached_result:
        j = json.loads(cached_result)
        Log.info("LightshowEngine", f"Loading lightshow from cache, took {(time.time() - process_start_time) * 1000:.2f} ms.")
        return j
    
    # --- 1. SETUP & TIMELINE PARSING ---
    
    # Sort timeline by layers to ensure correct rendering order (Background -> Foreground)
    timeline = lightshow_data.get("timeline", [])
    timeline.sort(key=lambda x: x.get("layer", 0))

    # Basic Setup
    bpm = lightshow_data.get("bpm", 120) or 120
    if bpm == 0:
        Log.warn("LightshowEngine", "BPM is 0, defaulting to 120")
        bpm = 120

    # Compute total duration
    audio_length_beats = max(item.get("end", 0) for item in timeline) if timeline else 0
    audio_length = audio_length_beats * (60.0 / bpm)
    total_frames = int(settings.FPS * audio_length)
    num_leds = len(registry.coords)

    # Initialize the "Canvas" with Black (0, 0, 0)
    # This is our base layer. We will paint on top of this.
    black_pixel = (0, 0, 0)
    frames = [[black_pixel] * num_leds for _ in range(total_frames)]

    # create a cache of processed effects to avoid redundant calculations for identical effects
    # effect cache key will be a tuple of (effect_name, frozenset(params.items()), steps) to uniquely identify effect calls
    effect_cache = {}


    # --- 2. LAYER PROCESSING ---
    
    # We process items sequentially. Since we sorted by layer above, 
    # we are naturally painting from bottom to top.
    for item in timeline:
        effect_name = item.get("effect")
        if not effect_name:
            continue # Skip if no effect name (filters not implemented yet)
        

        effect_func = registry.registry.get(effect_name)
        if effect_func is None:
            Log.warn("LightshowEngine", f"Effect {effect_name} not found.")
            continue

        # Prepare Parameters
        params = item.get("parameters", {})
        
        # Convert Hex params to RGB tuples
        for key, value in params.items():
            if type(value) is str and value.startswith("#"):
                # Fast hex string extraction
                hex_str = value[1:] 
                hex_len = len(hex_str)
                
                try:
                    # bytes.fromhex is implemented in C and much faster than int(x, 16)
                    if hex_len == 6:
                        r, g, b = bytes.fromhex(hex_str)
                        params[key] = (r, g, b, 255)
                    elif hex_len == 8:
                        params[key] = tuple(bytes.fromhex(hex_str))
                except ValueError:
                    Log.warn("LightshowEngine", f"Invalid hex color: {value}")

        # Calculate Timing
        start_beats = item.get("start", 0)
        end_beats = item.get("end", 0)
        start_time = start_beats * (60.0 / bpm)
        end_time = end_beats * (60.0 / bpm)

        if end_time <= start_time:
            continue

        duration = end_time - start_time
        steps = int(duration * settings.FPS)
        start_frame_index = int(start_time * settings.FPS)

        # --- 3. GENERATE EFFECT FRAMES ---
        # The effect should now ideally return RGBA
        cache_key = (effect_name, frozenset(params.items()), steps)
        if cache_key in effect_cache:
            effect_output = effect_cache[cache_key]
        else:
            try:
                effect_output = effect_func(steps, **params)
                # don't trust the user functions
                if not effect_output or not isinstance(effect_output, list):
                    Log.warn("LightshowEngine", f"Effect {effect_name} did not return a valid frame list.")
                    continue
            except Exception as e:
                Log.error_exc(f"LightshowEngine/{effect_name}", e)
                continue
            # cache the output
            effect_cache[cache_key] = effect_output

    # --- 4. THE COMPOSITOR (BLENDING) ---
    for i, src_frame in enumerate(effect_output):
        global_frame_idx = start_frame_index + i
        
        # Boundary check
        if global_frame_idx >= len(frames):
            break

        dest_frame = frames[global_frame_idx]

        for led_idx, src_pixel in enumerate(src_frame):
            # Skip if LED index out of bounds or pixel is strictly None
            if led_idx >= len(dest_frame) or src_pixel is None:
                continue

            # --- BLENDING LOGIC ---
            
            # Check 1: Is the pixel fully transparent? (0,0,0,0) or equivalent
            # Optimization: Check length and alpha value to avoid math on empty pixels
            if len(src_pixel) == 4 and src_pixel[3] == 0:
                continue

            # Get Background Color (Current state of the canvas)
            bg_r, bg_g, bg_b = dest_frame[led_idx]

            # Get Foreground Color & Alpha
            if len(src_pixel) == 4:
                # RGBA Mode
                fg_r, fg_g, fg_b, alpha = src_pixel
                
                # Normalize Alpha: If user sends 0-255, convert to 0.0-1.0
                if alpha > 1.0:
                    alpha = alpha / 255.0
            else:
                # RGB Mode (Legacy/Fallback) - Assume 100% Opacity
                fg_r, fg_g, fg_b = src_pixel
                alpha = 1.0

            # Optimization: If fully opaque, just overwrite (saves math)
            if alpha >= 1.0:
                dest_frame[led_idx] = (int(fg_r), int(fg_g), int(fg_b))
                continue

            # Standard Alpha Blending Formula:
            # Out = (Foreground * Alpha) + (Background * (1 - Alpha))
            inv_alpha = 1.0 - alpha
            
            out_r = (fg_r * alpha) + (bg_r * inv_alpha)
            out_g = (fg_g * alpha) + (bg_g * inv_alpha)
            out_b = (fg_b * alpha) + (bg_b * inv_alpha)

            # Clamp to 255 (just in case of float weirdness) and Cast to Int
            dest_frame[led_idx] = (
                min(255, int(out_r)),
                min(255, int(out_g)),
                min(255, int(out_b))
            )

    ms_taken = (time.time() - process_start_time) * 1000
    Log.info("LightshowEngine", f"Processed lightshow in {ms_taken:.2f} ms.")
    # --- 5. FINALIZE, CACHE FOR LATER ---
    # Cache the final frames for this lightshow configuration
    caching.set_cache_by_name("lightshow_engine", file_cache_key, json.dumps(frames))

    return frames