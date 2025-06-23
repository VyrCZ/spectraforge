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
            return self.value == "true"
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


class LightEffect:
    def __init__(self, pixels, coords):
        self.pixels = pixels
        self.coords = coords
        self.parameters = {}
        self.height = max([coord[2] for coord in coords])

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
