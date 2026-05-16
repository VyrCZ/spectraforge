import os
import json
import importlib
from threading import Thread

from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.setup import Setup, SetupType
from modules.config_manager import Config
from modules.effect import EffectType
from modules.log_manager import Log
from modules.led_renderer import DummyRenderer
import modules.caching as cache
import traceback
import ast

class EffectsEngine(Engine):
    """
    The star of the show, the EffectsEngine is responsible for managing effect scripts and their execution.
    """

    SETUP_FOLDER = "config/setups"

    def __init__(self, renderer, init_setup):
        self.renderer = renderer
        self.current_effect = None
        self.effects = {}
        self.running = False
        self.runner_thread = None

        # file storing current effect, parameters and current setup
        # load current setup
        #self.setup = init_setup
        #self.coords = self.setup.coords

    def on_enable(self):
        Log.info("EffectsEngine", "EffectsEngine enabled.")
        self.load_effects()
        effect_name = Config().config.get("current_effect")
        if effect_name in self.effects:
            self.current_effect = self.effects[effect_name](self.renderer, self.coords)
            # load parameters
            for param in self.current_effect.parameters.values():
                last_value = Config().config.get("parameters", {}).get(effect_name, {}).get(param.name)
                if last_value is not None:
                    param.set(last_value)
        else:
            # set to first effect
            if self.effects:
                effect_name = list(self.effects.keys())[0]
                self.current_effect = list(self.effects.values())[0](self.renderer, self.coords)
                Config().config["current_effect"] = effect_name
                Config().save()

        self.running = True
        self.runner_thread = Thread(target=self.effect_runner, daemon=True)
        self.runner_thread.start()

    def on_disable(self):
        Log.info("EffectsEngine", "EffectsEngine disabled.")
        self.running = False
        if self.runner_thread:
            self.runner_thread.join()
        self.renderer.fill((0, 0, 0))
        self.renderer.show()

    def on_setup_changed(self, setup):
        Log.debug("EffectsEngine", f"Setup changed to {setup.name}")
        self.setup = setup
        self.coords = setup.coords
        # reload the runner
        if(self.running):
            self.set_effect(Config().config["current_effect"])

    def get_effect_name(self, effect):
        for name, eff_class in self.effects.items():
            if isinstance(effect, eff_class):
                return name
        return None
    
    class StaticAnalysis(ast.NodeVisitor):
        """Performs static analysis on effect scripts before importing them."""

        def __init__(self):
            self.allowed_modules = ["math", "numpy", "random", "time", "colorsys", "modules.mathutils", "modules.effect", "modules.led_renderer", "modules.log_manager"]

        class DisallowedExecution(Exception):
            """
            Exception raised when an effect tries to execute disallowed 
            """
            def __init__(self, disallowed_call):
                super().__init__(f"Using '{disallowed_call}' is not allowed in effect scripts for security reasons, sorry!")

        def perform_analysis(self, code, filename="<effect>"):
            tree = ast.parse(code, filename=filename)
            self.visit(tree)

        def is_effect_class(self, node):
            if not isinstance(node, ast.ClassDef):
                return False

            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "LightEffect":
                    return True
                if isinstance(base, ast.Attribute) and base.attr == "LightEffect":
                    return True
            return False

        def visit_Import(self, node):
            # Check every module they are trying to import (e.g., import math, os)
            for alias in node.names:
                if alias.name not in self.allowed_modules:
                    raise self.DisallowedExecution(alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            # Check 'from X import Y' style imports
            if node.module not in self.allowed_modules:
                raise self.DisallowedExecution(node.module)
            self.generic_visit(node)

        def visit_Call(self, node):
            # Still block the really dangerous built-in functions
            if isinstance(node.func, ast.Name) and node.func.id in ["exec", "eval", "open", "__import__"]:
                raise self.DisallowedExecution(node.func.id)
            self.generic_visit(node)

        def visit_Attribute(self, node):
            # Block access to any "dunder" (double underscore) attributes.
            # This prevents attackers from crawling the inheritance tree 
            # (e.g., ().__class__.__bases__[0].__subclasses__())
            if node.attr.startswith('__') and node.attr != "__init__":
                raise self.DisallowedExecution(f"hidden attribute '{node.attr}'")
            self.generic_visit(node)

        def visit_Name(self, node):
            # Block direct access to the built-ins dictionary.
            # e.g. __builtins__['eval']('print("This is malicious code execution!")')
            if node.id == "__builtins__":
                raise self.DisallowedExecution("__builtins__")
            self.generic_visit(node)

    def validate_effect_source(self, code, filename="<effect>") -> None:
        """Validate source code before it is imported."""
        analyzer = self.StaticAnalysis()
        analyzer.perform_analysis(code, filename)

    def get_effect_class_names(self, code):
        """Return the names of classes that appear to inherit from `LightEffect`."""
        analyzer = self.StaticAnalysis()
        tree = ast.parse(code)
        return [node.name for node in tree.body if analyzer.is_effect_class(node)]
    
    def validate_effect(self, cls) -> Exception | None:
        """Validate if the class doesn't throw any immediate exceptions.
        Returns None if valid, otherwise returns the exception."""
        # check for mandatory attributes
        if not hasattr(cls, "update") or not callable(cls.update):
            return TypeError(f"Effect class {cls.__name__} must implement an 'update' method.")
        if not hasattr(cls, "__init__") or not callable(cls.__init__):
            return TypeError(f"Effect class {cls.__name__} must have an '__init__' method.")
        dummy_renderer = DummyRenderer(self.setup)
        try:
            effect_instance = cls(dummy_renderer, self.coords)
            effect_instance.update()  # Call update to check for runtime errors
        except Exception as e:
            Log.error_exc("EffectsEngine", e)
            return e
        return None

            
    def load_effects(self, folder="effects"):
        """Dynamically load all effect scripts."""
        Log.info("EffectsEngine", "Loading and validating effects...")
        self.effects = {}
        cached_hashes = []
        cached_hashes_set = set()
        # get hashed of previously cached validated effects
        cache_data = cache.get_cache_by_name("effects_engine", "valid_effects")
        if cache_data:
            cached_hashes = list(json.loads(cache_data))
            cached_hashes_set = set(cached_hashes)
        for filename in os.listdir(folder):
            if filename.endswith(".py") and not filename.startswith("__"):
                file_path = os.path.join(folder, filename)
                module_name = filename[:-3]
                try:
                    with open(file_path, "r", encoding="utf-8") as file_handle:
                        source = file_handle.read()

                    self.validate_effect_source(source, file_path)
                    effect_class_names = self.get_effect_class_names(source)
                    if not effect_class_names:
                        continue

                    module = importlib.import_module(f"{folder}.{module_name}")
                    for class_name in effect_class_names:
                        cls = getattr(module, class_name, None)
                        if not isinstance(cls, type):
                            continue
                        if not hasattr(module, "LightEffect") or not issubclass(cls, module.LightEffect) or cls is module.LightEffect:
                            continue

                        module_hash = cache.hash_module(cls)
                        if module_hash in cached_hashes_set:
                            self.effects[module_name] = cls
                        else:
                            Log.debug("EffectsEngine", f"Effect {module_name} isn't cached, validating...")
                            thrown_exception = self.validate_effect(cls)
                            if thrown_exception is None:
                                self.effects[module_name] = cls
                                cached_hashes.append(module_hash)
                                cached_hashes_set.add(module_hash)
                            else:
                                Log.warn("EffectsEngine", f"Effect {module_name} is invalid. (Traceback above ^)")
                except Exception as e:
                    Log.warn("EffectsEngine", f"Skipping effect {module_name}: {e}")
        # save the cache
        cache.set_cache_by_name("effects_engine", "valid_effects", json.dumps(cached_hashes))
            
        Log.info("EffectsEngine", f"Loaded {len(self.effects)} effects.")
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
                "parameters": None,
                "effect_type": None
            }
        
        if self.current_effect:
            return {
                "current_effect": self.get_effect_name(self.current_effect),
                "parameters": {name: param.get() for name, param in self.current_effect.parameters.items()},
                "effect_type": EffectType.display_name(self.current_effect.effect_type)
            }
        
        return {
            "current_effect": None,
            "parameters": None,
            "effect_type": None
        }

    @EngineManager.requires_active
    def set_effect(self, effect_name):
        """Set the current LED effect."""
        Log.info("EffectsEngine", f"Setting effect to {effect_name}")
        if effect_name in self.effects:
            self.current_effect = self.effects[effect_name](self.renderer, self.coords)
            Config().config["current_effect"] = effect_name
            Config().save()
            for param in self.current_effect.parameters.values():
                last_value = Config().config.get("parameters", {}).get(effect_name, {}).get(param.name, None)
                if last_value is not None:
                    param.set(last_value)
            Log.info("EffectsEngine", f"Effect set to {effect_name}")
            return {"status": "success", "current_effect": effect_name}
        return {"status": "error", "message": "Effect not found"}

    @EngineManager.requires_active
    def get_parameters(self, effect_name):
        """Get parameters for a specific effect."""
        if effect_name in self.effects:
            effect_class = self.effects[effect_name]
            parameters = effect_class(self.renderer, self.coords).get_parameters()
            return parameters
        return {"error": "Effect not found"}

    @EngineManager.requires_active
    def set_parameter(self, param_name, value):
        """Set a specific parameter for the current effect."""
        Log.info("EffectsEngine", f"Setting parameter {param_name} to {value}")
        if self.current_effect and param_name in self.current_effect.parameters:
            if "parameters" not in Config().config:
                Config().config["parameters"] = {}
                Config().save()

            effect_name = self.get_effect_name(self.current_effect)
            if effect_name not in Config().config["parameters"]:
                Config().config["parameters"][effect_name] = {}
                Config().save()

            self.current_effect.parameters[param_name].set(value)
            Config().config["parameters"][effect_name][param_name] = value
            Config().save()
            return {"status": "success"}
        return {"status": "error", "message": "Invalid parameter"}

    #@EngineManager.requires_active
    def get_effect_data(self):
        """Get data for loaded effects for the frontend.
        Returns a zip of effect names and their types."""
        effect_names = []
        types = []
        display_names = []
        for name, effect_class in self.effects.items():
            effect_instance = effect_class(self.renderer, self.coords)
            # Check if the effect is compatible with the current setup
            if (effect_instance.effect_type == EffectType.ONLY_2D and self.setup.type == SetupType.THREE_DIMENSIONAL) or \
                (effect_instance.effect_type == EffectType.ONLY_3D and self.setup.type == SetupType.TWO_DIMENSIONAL):
                continue
            types.append(EffectType.display_name(effect_instance.effect_type))
            effect_names.append(name)
            display_names.append(effect_instance.display_name)
        effect_data = list(zip(effect_names, types, display_names))
        sorting_key_2d = {
            EffectType.display_name(EffectType.ONLY_2D): 0,
            EffectType.display_name(EffectType.PRIMARILY_2D): 1,
            EffectType.display_name(EffectType.UNIVERSAL): 2,
            EffectType.display_name(EffectType.PRIMARILY_3D): 3,
            EffectType.display_name(EffectType.ONLY_3D): 4
        }
        sorted_data = sorted(effect_data, key=lambda x: sorting_key_2d.get(x[1], 5), reverse=self.setup.type == SetupType.THREE_DIMENSIONAL)
        return sorted_data