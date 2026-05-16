from modules.effect import LightEffect, EffectType
#import os

class MaliciousEffect(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Malicious Effect Test", EffectType.UNIVERSAL)
    # example malicious code
        #os.system("echo 'This is a malicious effect!' > malicious_effect_test.txt")
    

    def update(self):
        pass