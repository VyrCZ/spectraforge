from enum import Enum

class SetupType(Enum):
    TWO_DIMENSIONAL = "2D"
    THREE_DIMENSIONAL = "3D"
    
class Setup:
    """
    A class holding data about the current physical setup of the lights.
    This includes the name, type (2D or 3D), and coordinates of the lights.
    The coordinates are a list of lists. From the perspective of the camera (front), the X axis is horizontal, the Y axis is vertical, and the Z axis is depth. The vertical axis was initially Z, but it was changed to match 2D.
    Creation of setups should be handled through the CalibrationEngine.
    """
    def __init__(self, name: str, type: SetupType, coords: list[list[int]]):
        self.name = name
        self.type = type
        self.coords = coords

    @classmethod
    def from_json(cls, name, data: dict):
        """
        Create a Setup instance from a JSON dictionary.
        """
        setup = cls(
            name=name, # name is not stored in the JSON, it's the file name
            type=data["type"],
            coords=data["coordinates"],
        )
        # Give all coordinates a z-coordinate of 0 if the setup is 2D, for easier compatibility with 3D effects
        if setup.type == SetupType.TWO_DIMENSIONAL:
            for coord in setup.coords:
                coord[2] = 0
        return setup
    
    def get_formatted_name(self):
        """
        Get the name of the setup in a file-safe format.
        """
        return self.name.replace(" ", "_").replace("/", "_").replace("\\", "_").lower()