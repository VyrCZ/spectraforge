from enum import Enum

class SetupType(Enum):
    TWO_DIMENSIONAL = "2D"
    THREE_DIMENSIONAL = "3D"
    
class Setup:
    """
    A class holding calibration data for the current setup of the LED strip.
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
        return cls(
            name=name, # name is not stored in the JSON, it's the file name
            type=data["type"],
            coords=data["coordinates"],
        )
    
    def get_formatted_name(self):
        """
        Get the name of the setup in a file-safe format.
        """
        return self.name.replace(" ", "_").replace("/", "_").replace("\\", "_").lower()