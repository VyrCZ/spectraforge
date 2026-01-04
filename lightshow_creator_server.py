import os
import inspect
import importlib.util
import sys
from typing import Dict, List, Any

# Assuming these are defined elsewhere in your project, but needed for type checks
# from your_project import LightshowEffects, EffectType, CustomParamType

LIGHTSHOW_EFFECTS_DIR = r"C:\Users\vojta\Code\python\spectraforge\lightshow_effects"

def get_type_name(annotation) -> str:
    """Helper to convert type annotations to readable strings."""
    if hasattr(annotation, "__name__"):
        return annotation.__name__
    return str(annotation).replace("typing.", "")

def list_effects() -> Dict[str, List[Dict[str, Any]]]:
    """
    Scans the LIGHTSHOW_EFFECTS_DIR for classes with @namespace
    and methods with @l_effect, extracting their metadata.
    """
    
    effects_data = []
    
    # Ensure the directory exists
    if not os.path.exists(LIGHTSHOW_EFFECTS_DIR):
        print(f"Warning: Directory {LIGHTSHOW_EFFECTS_DIR} not found.")
        return {"effects": []}

    # 1. Scan for python files
    for filename in os.listdir(LIGHTSHOW_EFFECTS_DIR):
        if filename.endswith(".py") and not filename.startswith("__"):
            
            module_name = filename[:-3]
            file_path = os.path.join(LIGHTSHOW_EFFECTS_DIR, filename)
            
            # 2. Dynamically import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module # Register module
                try:
                    spec.loader.exec_module(module)
                except Exception as e:
                    print(f"Failed to load module {module_name}: {e}")
                    continue

                # 3. Inspect classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    
                    # We look for classes that have the @namespace decorator metadata
                    # We assume @namespace stores the name in `_namespace_name`
                    # If using the provided DefaultUniversal example, it likely has this attribute.
                    # If not, you can check inheritance from LightshowEffects instead.
                    
                    namespace = getattr(obj, "__namespace__", None)
                    
                    # Fallback: check if it inherits from LightshowEffects if namespace is missing
                    # but usually, we want strictly decorated classes.
                    if namespace is None:
                        continue
                        
                    # 4. Inspect methods (effects) in the class
                    for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                        
                        # Check for @l_effect metadata
                        # We assume @l_effect stores the type in `_effect_type`
                        effect_type = getattr(method, "__effect_type__", None)
                        
                        if effect_type:
                            # Construct the ID
                            # If namespace is empty string, format is just ":name" or "name"
                            # depending on your preference. Here we do "namespace:name"
                            full_id = f"{namespace}:{method_name}" if namespace else method_name
                            
                            params_dict = {}
                            
                            # 5. Extract Parameters
                            sig = inspect.signature(method)
                            
                            for param_name, param in sig.parameters.items():
                                # Ignore ignored parameters
                                if param_name in ["self", "steps"]:
                                    continue
                                
                                # Ignore unannotated parameters
                                if param.annotation == inspect.Parameter.empty:
                                    continue

                                # Extract type and default
                                p_type = get_type_name(param.annotation)
                                
                                p_data = {"type": p_type}
                                
                                if param.default != inspect.Parameter.empty:
                                    p_data["default"] = param.default
                                
                                params_dict[param_name] = p_data
                            
                            # Build the effect object
                            effect_entry = {
                                "id": full_id,
                                "effect_type": str(effect_type), # Convert Enum to string if necessary
                                "parameters": params_dict
                            }
                            
                            effects_data.append(effect_entry)

    return {"effects": effects_data}

def get_effects_json() -> str:
    """Returns the effects data as a JSON string."""
    import json
    effects = list_effects()
    return json.dumps(effects, indent=4)