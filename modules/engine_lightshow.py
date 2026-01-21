from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import json
import sys, os, importlib.util, inspect
from pathlib import Path
from modules.lightshow_effects import LightshowEffects
from modules.config_manager import Config
from modules.lightshow_manager import RegistryInstance, LightshowSettings, process_lightshow

class LightshowEngine(AudioEngine):
    """
    A test engine implementation for testing purposes.
    """

    def __init__(self, renderer, active_setup, ready_callback):
        super().__init__(renderer, ready_callback)
        self.lightshow_data = None
        self.active_setup = active_setup
        self.coords = active_setup.coords
        self.ready_callback = ready_callback
        self.registry = None

    def compile_lightshow(self, lightshow_file):
        """Load the lightshow JSON file and extract the audio file path."""
        # get the performance mode
        # init the registry/manager for effects for this setup
        self.registry = RegistryInstance(self.coords)
        performance_mode = Config().config.get("performance_mode", "normal")
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
                # use the new free function API: process_lightshow(registry, data, settings)
                self.frames = process_lightshow(self.registry, data, LightshowSettings(self.FPS))
                # TODO: Calculate audio length properly
                self.audio_length = len(self.frames) / self.FPS if self.frames else 0
                Log.info("LightshowEngine", f"Loaded lightshow: {lightshow_file}")
                return audio_file
        except Exception as e:
            Log.error_exc("LightshowEngine", e)
            return None

    @EngineManager.requires_active
    def on_audio_load(self, audio_file: str):
        """Load the lightshow data and prepare for playback."""
        lightshow_file = os.path.join("lightshows", f"{os.path.splitext(audio_file)[0]}.json")
        audio_file_path = self.compile_lightshow(lightshow_file)
        if audio_file_path:
            Log.debug("LightshowEngine", self.frames)
            Log.debug("LightshowEngine", f"Audio length: {self.audio_length}s; Calculated frames: {len(self.frames)}; FPS: {self.FPS}")
            Log.info("LightshowEngine", f"Audio file loaded: {audio_file_path}")
            self.ready_callback(audio_file_path)
        else:
            Log.error("LightshowEngine", "Failed to load lightshow or audio file.")

    def on_enable(self):
        Log.info("LightshowEngine", "LightshowEngine enabled.")

    def on_disable(self):
        Log.info("LightshowEngine", "LightshowEngine disabled.")

    def on_frame(self, current_time):
        # display the correct frame
        frame_index = int(current_time * self.FPS)
        if frame_index < len(self.frames):
            frame = self.frames[frame_index]
            # update the colors in the renderer
            self.renderer.set_colors(frame)
        self.renderer.show()
