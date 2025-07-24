from modules.engine import Engine
from modules.engine_manager import EngineManager
import os
from modules.log_manager import Log
import importlib
import threading
import time
from modules.config_manager import Config
from modules.setup import Setup

class SandboxEngine(Engine):
    """
    Engine that allows to open and edit effects in a way, where they will be automatically reloaded and applied on each save.
    This is useful for testing and development of effects without needing to restart the entire application.
    """
    SANDBOX_PATH = "sandbox"
    # default script to create if no scripts are present
    DEFAULT_SCRIPT =\
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

    def __init__(self, renderer, active_setup: Setup):
        self.opened_file = None
        self.renderer = renderer
        self.file_name = None
        self.thread = None
        self.effect_thread = None
        self.current_effect_instance = None
        self.running = False
        self.active_setup = active_setup
        if not os.path.exists(self.SANDBOX_PATH):
            os.makedirs(self.SANDBOX_PATH)
            # Create a default script if no scripts are present
            with open(os.path.join(self.SANDBOX_PATH, "breathing.py"), "w") as f:
                f.write(self.DEFAULT_SCRIPT)
            Log.info("SandboxEngine", "No scripts are present. Created a default script (breathing.py).")
        Log.info("SandboxEngine", "Sandbox Engine initialized.")

    def on_enable(self):
        self.running = True
        if self.opened_file is None:
            last_file = Config().config.get("sandbox_opened_file", None)
            if last_file and os.path.exists(os.path.join(self.SANDBOX_PATH, last_file)):
                self.set_file(last_file)
        Log.info("SandboxEngine", "Sandbox Engine enabled.")

    def on_disable(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.effect_thread and self.effect_thread.is_alive():
            self.effect_thread.join()
        self.opened_file = None
        self.file_name = None
        self.current_effect_instance = None
        Log.info("SandboxEngine", "Sandbox Engine disabled.")

    def watch_file(self):
        """
        Watches the opened file for changes and reloads it if modified.
        """
        if not self.file_name:
            return
        file_path = os.path.join(self.SANDBOX_PATH, self.file_name)
        Log.debug("SandboxEngine", f"Watching file for changes: {file_path}")
        last_modified = os.path.getmtime(file_path)
        while self.running:
            time.sleep(0.5)
            try:
                current_modified = os.path.getmtime(file_path)
                if current_modified > last_modified:
                    Log.debug("SandboxEngine", f"File '{self.file_name}' has been modified. Reloading.")
                    last_modified = current_modified
                    self._reload_file()
            except FileNotFoundError:
                Log.error("SandboxEngine", f"File not found: {self.file_name}")
                break
            except Exception as e:
                Log.error_exc("SandboxEngine", e)
                break

    def _reload_file(self):
        """
        Reloads the currently opened file if it exists.
        """
        if not self.file_name:
            return
        Log.debug("SandboxEngine", f"Attempting to reload file: {self.file_name}")
        try:
            # Stop the effect runner while we reload
            if self.current_effect_instance:
                Log.debug("SandboxEngine", "Stopping current effect instance.")
                self.current_effect_instance = None
            
            module_name = self.file_name.replace(".py", "")
            full_module_name = f"{self.SANDBOX_PATH}.{module_name}"
            
            # Invalidate caches to ensure the module is re-read from disk
            Log.debug("SandboxEngine", "Invalidating import caches.")
            importlib.invalidate_caches()

            # Unload the module if it was already imported
            if full_module_name in importlib.sys.modules:
                Log.debug("SandboxEngine", f"Reloading module: {full_module_name}")
                importlib.reload(importlib.sys.modules[full_module_name])
            else:
                # Import the module for the first time
                Log.debug("SandboxEngine", f"Importing module for the first time: {full_module_name}")
                importlib.import_module(full_module_name)

            module = importlib.sys.modules[full_module_name]
            Log.debug("SandboxEngine", f"Searching for LightEffect class in {self.file_name}")

            effect_class_found = None
            for attr in dir(module):
                cls = getattr(module, attr)
                # The check needs to look for LightEffect from the base effect module, not the reloaded one.
                if isinstance(cls, type) and hasattr(cls, "__bases__") and any(b.__name__ == "LightEffect" for b in cls.__bases__) and cls.__name__ != "LightEffect":
                    Log.debug("SandboxEngine", f"Found LightEffect class: {cls.__name__}")
                    effect_class_found = cls
                    break # Found the class, no need to look further
            
            if effect_class_found:
                self.current_effect_instance = effect_class_found(self.renderer, self.active_setup.coords)
                Log.info("SandboxEngine", f"Effect '{effect_class_found.__name__}' reloaded and instance created from {self.file_name}")
            else:
                Log.warn("SandboxEngine", f"No valid LightEffect class found in {self.file_name}")
                self.current_effect_instance = None
            
        except Exception as e:
            Log.error_exc("SandboxEngine", e)
            self.current_effect_instance = None
    
    def _file_runner(self):
        """
        Thread running the script
        """
        while self.running:
            if self.current_effect_instance:
                #Log.debug("SandboxEngine", "About to call update() on effect instance.")
                try:
                    self.current_effect_instance.update()
                except Exception as e:
                    Log.error_exc("SandboxEngine", e)
                    self.current_effect_instance = None
            else:
                Log.debug("SandboxEngine", "No effect instance to run.")
                time.sleep(0.1)

    @EngineManager.requires_active
    def list_files(self):
        """
        Lists all files in the sandbox directory.
        """
        Log.debug("SandboxEngine", "Listing files in sandbox directory.")
        sandbox_dir = os.path.join(os.getcwd(), self.SANDBOX_PATH)
        if not os.path.exists(sandbox_dir):
            Log.error("SandboxEngine", "Sandbox directory does not exist.")
            return []

        Log.debug("SandboxEngine", f"Listing files in sandbox directory: {sandbox_dir}")
        Log.debug("SandboxEngine", f"Files found: {os.listdir(sandbox_dir)}")
        files = [f for f in os.listdir(sandbox_dir) if f.endswith('.py')]
        return files

    @EngineManager.requires_active
    def set_file(self, file_name):
        self.file_name = file_name
        self.opened_file = file_name
        Config().config["sandbox_opened_file"] = file_name
        Config().save()
        Log.info("SandboxEngine", f"Opened file: {file_name}")

        self._reload_file() # Initial load

        # Stop previous file watcher thread
        if self.thread and self.thread.is_alive():
            self.running = False
            self.thread.join()
            Log.debug("SandboxEngine", "Previous file watcher thread stopped.")

        # Stop previous effect thread
        if self.effect_thread and self.effect_thread.is_alive():
            self.running = False
            self.effect_thread.join()
            Log.debug("SandboxEngine", "Previous effect thread stopped.")

        # Start threads again
        self.running = True
        self.thread = threading.Thread(target=self.watch_file)
        self.thread.daemon = True
        self.thread.start()

        self.effect_thread = threading.Thread(target=self._file_runner)
        self.effect_thread.daemon = True
        self.effect_thread.start()
        Log.debug("SandboxEngine", "Effect thread started.")