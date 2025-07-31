from modules.lightshow_effect import *
import modules.mathutils as mu
import colorsys
from modules.effect import EffectType

@namespace("")
class Default2D(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)