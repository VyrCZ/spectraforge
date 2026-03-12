import inspect
import os
import sys
from pathlib import Path
import importlib.util
from typing import List, Dict

# add the project root (one level up) to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.effect import EffectType

EFFECTS_DIR = Path(__file__).resolve().parent.parent / "lightshow_effects"
print(f"Effects directory: {EFFECTS_DIR}")

class LEffect:
    def __init__(self, namespace: str, effect_name: str, effect_type: EffectType, params: dict[str, type]):
        self.namespace = namespace
        self.effect_name = effect_name
        self.effect_type = effect_type
        self.params = params

def load_effects() -> List[LEffect]:
    """Load all effect scripts and extract metadata about each effect."""
    effects = []
    
    # Check if the directory exists
    if not EFFECTS_DIR.exists():
        print(f"Effects directory not found: {EFFECTS_DIR}")
        return effects
    
    # Load all Python files in the effects directory
    for py_file in EFFECTS_DIR.glob("*.py"):
        effects.extend(load_effects_from_file(py_file))
    
    return effects

def load_effects_from_file(file_path: Path) -> List[LEffect]:
    """Load effects from a single Python file."""
    effects = []
    
    try:
        # Import the module
        spec = importlib.util.spec_from_file_location(file_path.stem, str(file_path))
        if spec is None or spec.loader is None:
            print(f"Failed to load spec for {file_path}")
            return effects
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find all classes that inherit from LightshowEffects
        for _, cls in inspect.getmembers(module, inspect.isclass):
            from modules.lightshow_effects import LightshowEffects
            
            if issubclass(cls, LightshowEffects) and cls is not LightshowEffects:
                effects.extend(extract_effects_from_class(cls))
    
    except Exception as e:
        print(f"Error loading effects from {file_path}: {e}")
    
    return effects

def extract_effects_from_class(cls) -> List[LEffect]:
    """Extract effects from a class that inherits from LightshowEffects."""
    effects = []
    namespace = getattr(cls, "__namespace__", "")
    
    # Create a temporary instance with dummy coordinates to inspect methods
    try:
        # Pass empty coordinates list for inspection purposes
        instance = cls([])
        
        for name, method in inspect.getmembers(instance, inspect.ismethod):
            if hasattr(method, "__is_effect__"):
                effect_type = getattr(method, "__effect_type__", None)
                
                # Get parameter types, excluding 'steps'
                signature = inspect.signature(method)
                params = {}
                for param_name, param in signature.parameters.items():
                    # Skip 'self' and 'steps'
                    if param_name not in ["self", "steps"]:
                        # Get the parameter type annotation if available
                        param_type = param.annotation if param.annotation != inspect.Parameter.empty else type(None)
                        params[param_name] = param_type
                
                # Create LEffect object
                effect = LEffect(namespace, name, effect_type, params)
                effects.append(effect)
    
    except Exception as e:
        print(f"Error extracting effects from class {cls.__name__}: {e}")
    
    return effects

def main():
    effects = load_effects()
    print(f"Loaded {len(effects)} effects:")
    
    for effect in effects:
        full_name = f"{effect.namespace + ':' if effect.namespace else ''}{effect.effect_name}"
        print(f"  - {full_name} ({effect.effect_type})")
        print(f"    Parameters: {', '.join([f'{name}: {param_type.__name__}' for name, param_type in effect.params.items()])}")

if __name__ == "__main__":
    main()