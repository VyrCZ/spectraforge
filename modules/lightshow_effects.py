from modules.effect import EffectType
import modules.mathutils as mu

# namespace id decorator
def namespace(namespace_id: str):
    def decorator(cls):
        cls.__namespace__ = namespace_id
        return cls
    return decorator

# lightshow decorator
def l_effect(effect_type: EffectType):
    """
    This decorator is used to mark a function as a lightshow effect. It assigns an `EffectType` to the function, which can be used to categorize or identify the effect.
    Each lightshow effect must start its params with `steps`, followed by your required params and return a list of frames, where each frame is a list of colors in RGB format.

    **Do not set unused pixels to black, but to None instead, representing transparency!**
    """
    def decorator(func):
        func.__effect_type__ = effect_type
        func.__is_effect__ = True
        return func
    return decorator

def l_filter(effect_type: EffectType):
    """
    This decorator is used to mark a function as a lightshow filter. It assigns an `EffectType` to the function, which can be used to categorize or identify the filter.
    Each lightshow filter must start its params with `frames`, followed by your required params and return a list of frames, where each frame is a list of colors in RGB format.
    """
    def decorator(func):
        func.__effect_type__ = effect_type
        func.__is_filter__ = True
        return func
    return decorator

#@namespace("")
class LightshowEffects:
    """
    This is a 'Namespace' class for individual lightshow effects. Each one will be defined as a function located in this class.

    This class has to be decorated with the `@namespace` decorator with a desired id as a parameter to be recognized as a namespace.
    This ID should be unique and will cause issues if there are multiple effects with the same name and namespace.

    Default effects are defined with no namespace for convenience, but if you create additional ones, you should include one.
    """

    def __init__(self, coords):
        self.bounds = mu.Bounds(coords)
        self.coords = coords