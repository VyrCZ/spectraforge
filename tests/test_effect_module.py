from modules.effect import EffectType, LightEffect, ParamType, Parameter


class DemoEffect(LightEffect):
    def __init__(self):
        super().__init__(renderer=[], coords=[[0, 0, 0], [1, 2, 0]], display_name="Demo", effect_type=EffectType.UNIVERSAL)

    def update(self):
        return None


def test_parameter_getters_and_button_callbacks():
    events = []
    color = Parameter("Color", ParamType.COLOR, "#ff0001")
    slider = Parameter("Speed", ParamType.SLIDER, 3)
    checkbox = Parameter("Enabled", ParamType.CHECKBOX, True)
    button = Parameter(
        "Run",
        ParamType.BUTTON,
        False,
        onDown=lambda: events.append("down"),
        onUp=lambda: events.append("up"),
        onClick=lambda: events.append("click"),
    )

    assert color.get() == (255, 0, 1)
    assert slider.get() == 3.0
    assert checkbox.get() is True

    button.set(True)
    button.set(False)
    assert events == ["down", "up", "click"]


def test_light_effect_add_parameter_and_serialize():
    effect = DemoEffect()
    effect.add_parameter("Speed", ParamType.SLIDER, 2, min=1, max=5)
    effect.add_parameter("Color", ParamType.COLOR, "#00ff00")
    effect.add_parameter("Enabled", ParamType.CHECKBOX, False)
    effect.add_parameter("Action", ParamType.BUTTON, None, onClick=lambda: None)

    params = effect.get_parameters()
    assert params["Speed"]["value"] == 2.0
    assert params["Color"]["value"] == "#00ff00"
    assert params["Enabled"]["value"] is False
    assert params["Action"]["value"] is False
    assert params["Action"]["options"]["onClick"] is True


def test_effect_type_display_name_unknown_and_known():
    assert EffectType.display_name(EffectType.UNIVERSAL) == "Universal"
    assert EffectType.display_name("mystery") == "Unknown"