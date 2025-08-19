from modules.mathutils import Bounds

class Parameter:
    """Class to store parameter metadata and value."""
    def __init__(self, name, param_type, value, **kwargs):
        self.name = name
        self.param_type = param_type
        self.value = value
        self.options = kwargs  # Additional metadata like range, colors, etc.

    def set(self, value):
        self.value = value

    def get(self):
        if self.param_type == ParamType.COLOR:
            return tuple(int(self.value[i : i + 2], 16) for i in (1, 3, 5))
        elif self.param_type == ParamType.SLIDER:
            return float(self.value)
        elif self.param_type == ParamType.CHECKBOX:
            return self.value == True
        return self.value
    
class ParamType:
    """Define parameter types
    COLOR: Color picker, returns RGB tuple.
    SLIDER: Slider - returns float. Additional values: min, max, step
    BOOL: Checkbox - returns a boolean.
    """
    COLOR = "color"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    INPUT = "input"

class EffectType:
    ONLY_2D = "only_2d"
    ONLY_3D = "only_3d"
    PRIMARILY_2D = "primarily_2d"
    PRIMARILY_3D = "primarily_3d"
    UNIVERSAL = "universal"

    def display_name(cls):
        """Return a human-readable name for the effect type."""
        return {
            EffectType.ONLY_2D: "2D Only",
            EffectType.ONLY_3D: "3D Only",
            EffectType.PRIMARILY_2D: "Primarily 2D",
            EffectType.PRIMARILY_3D: "Primarily 3D",
            EffectType.UNIVERSAL: "Universal"
        }.get(cls, "Unknown")



class LightEffect:
    def __init__(self, renderer, coords, display_name, effect_type: EffectType):
        self.renderer = renderer
        self.coords = coords
        self.display_name = display_name
        self.effect_type = effect_type
        self.parameters = {}
        self.height = max([coord[1] for coord in coords]) - min([coord[1] for coord in coords])
        self.bounds = Bounds(
            min_x=min(coord[0] for coord in coords),
            max_x=max(coord[0] for coord in coords),
            min_y=min(coord[1] for coord in coords),
            max_y=max(coord[1] for coord in coords),
            min_z=min(coord[2] for coord in coords),
            max_z=max(coord[2] for coord in coords)
        )
        #print(f"Height: {self.height}")

    def add_parameter(self, name, param_type, default_value, **kwargs):
        """Add a configurable parameter."""
        self.parameters[name] = Parameter(name, param_type, default_value, **kwargs)
        return self.parameters[name]

    def get_parameters(self):
        """Return all parameters."""
        return {name: param.__dict__ for name, param in self.parameters.items()}

    def update(self):
        """Update the LED effect (override in subclasses)."""
        raise NotImplementedError("Update method must be implemented by subclasses.")
