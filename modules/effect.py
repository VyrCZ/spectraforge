from modules.mathutils import Bounds
from modules.log_manager import Log

class Parameter:
    """Class to store parameter metadata and value."""
    def __init__(self, name, param_type, value, **kwargs):
        self.name = name
        self.param_type = param_type
        self.value = value
        self.options = kwargs  # Additional metadata like range, colors, etc.

    def set(self, value):
        self.value = value
        # Special handling for BUTTON type
        if self.param_type == ParamType.BUTTON:
            # 1. Handle "Down" (Press)
            if value is True:
                on_down = self.options.get("onDown")
                if on_down:
                    on_down()
            
            # 2. Handle "Up" (Release) AND "Click"
            elif value is False:
                # Trigger Up event
                on_up = self.options.get("onUp")
                if on_up:
                    on_up()
                
                # Trigger Click event (Standard behavior: fire on release)
                on_click = self.options.get("onClick")
                if on_click:
                    on_click()

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
    CHECKBOX: Checkbox - returns a boolean.
    BUTTON: Button - triggers passed onClick function.
    """
    COLOR = "color"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    BUTTON = "button"

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
        self.bounds = Bounds(self.coords)
        #print(f"Height: {self.height}")

    def add_parameter(self, name, param_type, default_value, **kwargs):
        """Add a configurable parameter.
        # Values for each parameter:

        **COLOR**: None

        **SLIDER**:
        - min (float)
        - max (float)
        - step (float)

        **CHECKBOX**: None,

        **BUTTON**: pass None into default value and 'onClick=function' in kwargs.
        """
        if param_type == ParamType.BUTTON:
            if 'onClick' not in kwargs:
                Log.warn("EffectEngine", f"Button parameter '{name}' created without onClick handler.")
            if 'onDown' not in kwargs:
                kwargs['onDown'] = None
            if 'onUp' not in kwargs:
                kwargs['onUp'] = None
            
            if default_value is None:
                default_value = False  # Buttons start unpressed
                
        self.parameters[name] = Parameter(name, param_type, default_value, **kwargs)
        return self.parameters[name]

    def get_parameters(self):
        """Return all parameters in a JSON-serializable form."""
        def serialize_param(param: Parameter):
            # Use the Parameter.get() for typed values where applicable
            if param.param_type == ParamType.COLOR:
                value = param.get()
                # return as hex string the frontend likely expects (e.g. "#rrggbb")
                value = "#{:02x}{:02x}{:02x}".format(*value)
            elif param.param_type == ParamType.SLIDER:
                value = param.get()
            elif param.param_type == ParamType.CHECKBOX:
                value = param.get()
            else:
                # For BUTTON and fallback types, keep the stored value (could be None)
                value = param.value

            # Serialize options but don't attempt to send callables (methods/functions)
            options_serialized = {}
            for k, v in (param.options or {}).items():
                if callable(v):
                    # indicate presence of a handler without sending the function
                    options_serialized[k] = True
                else:
                    options_serialized[k] = v

            return {
                "name": param.name,
                "param_type": param.param_type,
                "value": value,
                "options": options_serialized
            }

        return {name: serialize_param(param) for name, param in self.parameters.items()}

    def update(self):
        """Update the LED effect (override in subclasses)."""
        raise NotImplementedError("Update method must be implemented by subclasses.")
