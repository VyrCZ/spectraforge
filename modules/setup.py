class SetupType:
    TWO_DIMENSIONAL = "2D"
    THREE_DIMENSIONAL = "3D"
    
class Setup:
    """
    A class holding calibration data for the current setup of the LED strip.
    """
    def __init__(self, name: str, type: SetupType, coords: list[list[int]], creation_date: str | None = None):
        self.name = name
        self.creation_date = creation_date
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
            creation_date=data.get("creation_date", None)
        )