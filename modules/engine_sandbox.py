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

    def __init__(self, renderer, active_setup: Setup):
        self.opened_file = None
        self.renderer = renderer
        self.file_name = None
        self.thread = None
        self.effect_thread = None
        self.current_effect_instance = None
        self.running = False
        self.active_setup = active_setup
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
        file_path = os.path.join(self.SANDBOX_PATH, self.file_name + ".py")
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
            
            full_module_name = f"{self.SANDBOX_PATH}.{self.file_name}"
            
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
        files = []
        for file in os.listdir(sandbox_dir):
            if file.endswith(".py"):
                files.append(file[:-3]) # Remove .py extension
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