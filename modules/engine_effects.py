import os
import json
import importlib
from threading import Thread

from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.setup import Setup
from modules.config_manager import Config

class EffectsEngine(Engine):
    """
    The star of the show, the EffectsEngine is responsible for managing effect scripts and their execution.
    """

    SETUP_FOLDER = "config/setups"

    def __init__(self, pixels, init_setup):
        self.pixels = pixels
        self.current_effect = None
        self.effects = {}
        self.running = False
        self.runner_thread = None

        # file storing current effect, parameters and current setup
        # load current setup
        #self.setup = init_setup
        #self.coords = self.setup.coords

    def on_enable(self):
        print("EffectsEngine enabled.")
        self.load_effects()
        
        effect_name = Config().get("current_effect")
        if effect_name in self.effects:
            self.current_effect = self.effects[effect_name](self.pixels, self.coords)
            # load parameters
            for param in self.current_effect.parameters.values():
                last_value = Config().get("parameters", {}).get(effect_name, {}).get(param.name)
                if last_value is not None:
                    param.set(last_value)
        else:
            # set to first effect
            if self.effects:
                effect_name = list(self.effects.keys())[0]
                self.current_effect = list(self.effects.values())[0](self.pixels, self.coords)
                Config()["current_effect"] = effect_name

        self.running = True
        self.runner_thread = Thread(target=self.effect_runner, daemon=True)
        self.runner_thread.start()

    def on_disable(self):
        print("EffectsEngine disabled.")
        self.running = False
        if self.runner_thread:
            self.runner_thread.join()
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def on_setup_changed(self, setup):
        self.setup = setup
        self.coords = setup.coords

    def get_effect_name(self, effect):
        for name, eff_class in self.effects.items():
            if isinstance(effect, eff_class):
                return name
        return None
            
    def load_effects(self, folder="effects"):
        """Dynamically load all effect scripts."""
        self.effects = {}
        for filename in os.listdir(folder):
            if filename.endswith(".py") and not filename.startswith("__") and filename != "base_effect.py":
                module_name = filename[:-3]
                module = importlib.import_module(f"{folder}.{module_name}")
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if hasattr(module, "LightEffect") and isinstance(cls, type) and issubclass(cls, module.LightEffect) and cls is not module.LightEffect:
                        self.effects[module_name] = cls
        return self.effects
    
    def effect_runner(self):
        """Runs the current effect in a loop."""
        while self.running:
            if self.current_effect:
                #print(f"Running effect {self.current_effect.__class__.__name__}")
                self.current_effect.update()

    @EngineManager.requires_active
    def get_state(self):
        """Return the current state of the LED strip."""
        if not self.current_effect and self.effects:
            return {
                "current_effect": list(self.effects.keys())[0],
                "parameters": None
            }
        
        if self.current_effect:
            return {
                "current_effect": self.get_effect_name(self.current_effect),
                "parameters": {name: param.get() for name, param in self.current_effect.parameters.items()}
            }
        
        return {
            "current_effect": None,
            "parameters": None
        }

    @EngineManager.requires_active
    def set_effect(self, effect_name):
        """Set the current LED effect."""
        print("Setting effect to", effect_name)
        if effect_name in self.effects:
            self.current_effect = self.effects[effect_name](self.pixels, self.coords)
            Config()["current_effect"] = effect_name
            for param in self.current_effect.parameters.values():
                last_value = Config().get("parameters", {}).get(effect_name, {}).get(param.name, None)
                if last_value is not None:
                    param.set(last_value)    
            print(f"Set effect to {effect_name}")
            return {"status": "success", "current_effect": effect_name}
        return {"status": "error", "message": "Effect not found"}

    @EngineManager.requires_active
    def get_parameters(self, effect_name):
        """Get parameters for a specific effect."""
        if effect_name in self.effects:
            effect_class = self.effects[effect_name]
            parameters = effect_class(self.pixels, self.coords).get_parameters()
            return parameters
        return {"error": "Effect not found"}

    @EngineManager.requires_active
    def set_parameter(self, param_name, value):
        """Set a specific parameter for the current effect."""
        if self.current_effect and param_name in self.current_effect.parameters:
            if "parameters" not in Config():
                Config()["parameters"] = {}

            effect_name = self.get_effect_name(self.current_effect)
            if effect_name not in Config()["parameters"]:
                Config()["parameters"][effect_name] = {}

            self.current_effect.parameters[param_name].set(value)
            Config()["parameters"][effect_name][param_name] = value
            return {"status": "success"}
        return {"status": "error", "message": "Invalid parameter"}
