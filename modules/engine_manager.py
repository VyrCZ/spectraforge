from functools import wraps
from modules.engine import Engine, AudioEngine
from modules.setup import Setup, SetupType
from modules.config_manager import Config
from modules.log_manager import Log
import json

class EngineManager:
    """
    A singleton class responsible for managing multiple engines and ensuring that only one engine is active at a time.
    This class also handles the setup system, calling engines when the setup is changed.
    All engines must decorate their methods communicating with the app, especially when modifying the LED state with the `@EngineManager.requires_active` decorator to ensure that the engine is active and others are not before executing the method.
    """
    _instance = None
    _initialized = False
    SETUPS_FOLDER = "config/setups"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self.__class__._initialized:
            return
        self.engines = []
        self.active_engine = None
        active_setup_name = Config().config.get("current_setup", None)
        if active_setup_name:
            try:
                with open(f"{self.SETUPS_FOLDER}/{active_setup_name}.json", "r") as f:
                    active_setup_data = json.load(f)
            except FileNotFoundError:
                Log.warn("EngineManager", f"Setup {active_setup_name} not found, using default setup.")
        self.active_setup = Setup.from_json(active_setup_name, active_setup_data) if active_setup_name else None
        Log.info("EngineManager", "EngineManager initialized with active setup: " + str(self.active_setup))
        self.__class__._initialized = True

    def register_engine(self, engine: Engine):
        """
        Register a new engine.
        """
        if engine not in self.engines:
            self.engines.append(engine)
        else:
            Log.warn("EngineManager", f"Engine {engine} is already registered.")
        if self.active_engine is None:
            engine.on_setup_changed(self.active_setup)
            engine.on_enable()
            self.active_engine = engine
        engine.manager = self

    def register_audio_engine(self, audio_engine: AudioEngine):
        """
        Register a new audio engine.
        """
        if not isinstance(audio_engine, AudioEngine):
            raise TypeError("Audio engine must be an instance of AudioEngine.")
        self.register_engine(audio_engine)
        Log.info("EngineManager", f"Audio engine {audio_engine} registered.")

    def set_active_engine(self, engine):
        """Set the active engine."""
        if self.active_engine == engine:
            return
        if self.active_engine:
            self.active_engine.on_disable()
        self.active_engine = engine

    @staticmethod
    def requires_active(func):
        """
        Decorator to ensure an engine is active before executing the function.
        """
        @wraps(func)
        def wrapper(engine_instance: Engine, *args, **kwargs):
            mgr = getattr(engine_instance, 'manager', None)
            if mgr is None or engine_instance not in mgr.engines:
                raise EngineManager.EngineNotRegisteredError(engine_instance)
            mgr.set_active_engine(engine_instance)
            return func(engine_instance, *args, **kwargs)
        return wrapper

    class EngineNotRegisteredError(Exception):
        def __init__(self, engine):
            super().__init__(f"Engine {engine} is not registered.")

    class NonAudioEngineActiveError(Exception):
        def __init__(self, engine):
            super().__init__(f"Active engine {engine} is not an audio engine, but an audio engine is required for this operation.")

    def change_setup(self, setup: Setup):
        """
        Change the current setup and notify all of the engines.
        """
        # if the coordinates are 2D, add a z coordinate of 0 to all coordinates
        if setup.type == SetupType.TWO_DIMENSIONAL:
            for coord in setup.coords:
                if len(coord) == 2:
                    coord.append(0)
        for engine in self.engines:
            engine.on_setup_changed(setup)
        self.active_setup = setup

    def change_setup_by_name(self, setup_name: str):
        """
        Change the current setup by name.
        """
        try:
            with open(f"{self.SETUPS_FOLDER}/{setup_name}.json", "r") as f:
                setup_data = json.load(f)
            setup = Setup.from_json(setup_name, setup_data)
            self.change_setup(setup)
            Config().config["current_setup"] = setup_name
            Config().save()
        except FileNotFoundError:
            raise FileNotFoundError(f"Setup {setup_name} not found in {self.SETUPS_FOLDER}.")
        
    def audio_callbacks(self, callback_name: str, *args, **kwargs):
        """
        Call the audio callback on the active audio engine.
        """
        if not isinstance(self.active_engine, AudioEngine):
            raise self.NonAudioEngineActiveError(self.active_engine)
        callback = getattr(self.active_engine, f"on_audio_{callback_name}", None)
        if callback is None:
            raise AttributeError(f"Audio engine {self.active_engine} does not have a callback for {callback_name}.")
        return callback(*args, **kwargs)


