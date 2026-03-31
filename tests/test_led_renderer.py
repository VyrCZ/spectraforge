from modules.config_manager import Config
from modules.led_renderer import DummyRenderer, LEDRenderer
from modules.setup import Setup, SetupType


def build_setup():
    return Setup("demo", SetupType.TWO_DIMENSIONAL, [[0, 0, 0], [1, 1, 0]])


def test_dummy_renderer_set_and_fill():
    renderer = DummyRenderer(build_setup())
    renderer[0] = [1, 2, 3]
    renderer[1] = (4, 5, 6)
    assert renderer[0] == (1, 2, 3)
    assert renderer[1] == (4, 5, 6)
    renderer.fill((9, 9, 9))
    assert renderer.leds == [(9, 9, 9), (9, 9, 9)]


def test_dummy_renderer_rejects_invalid_values():
    renderer = DummyRenderer(build_setup())
    try:
        renderer[0] = (1, 2)
    except ValueError as exc:
        assert "tuple of (R, G, B)" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_led_renderer_apply_filters_and_debug_draw(monkeypatch):
    monkeypatch.setitem(Config().config, "enhance_colors", False)
    renderer = LEDRenderer.__new__(LEDRenderer)
    renderer.led_count = 2
    renderer.leds = [(100, 50, 0), (20, 40, 60)]
    renderer.brightness = 0.5
    renderer._gamma_table = list(range(256))
    renderer.debug_draw = LEDRenderer.DebugDraw()

    assert renderer._apply_filters(renderer.leds) == [(50, 25, 0), (10, 20, 30)]

    renderer.debug_draw.line([0, 0], [1, 1], persistent=False)
    renderer.debug_draw.point([1, 2, 3], persistent=True)
    renderer.debug_draw.circle([0, 0, 0], 5, persistent=False)
    elements = renderer.debug_draw._get_elements()
    assert len(elements) == 3
    assert all("persistent" not in element for element in elements)
    assert len(renderer.debug_draw.debug_elements) == 1


def test_led_renderer_set_colors_and_brightness(monkeypatch):
    Config().config = {}
    monkeypatch.setattr(Config, "save", lambda self: None)
    renderer = LEDRenderer.__new__(LEDRenderer)
    renderer.led_count = 2
    renderer.leds = [(0, 0, 0), (0, 0, 0)]
    renderer.brightness = 1.0
    renderer.set_colors([(1, 2, 3), (4, 5, 6)])
    assert renderer.leds == [(1, 2, 3), (4, 5, 6)]
    renderer.set_brightness(2)
    assert renderer.brightness == 1

    try:
        renderer.set_colors([(1, 2, 3)])
    except ValueError as exc:
        assert "Expected 2 colors" in str(exc)
    else:
        raise AssertionError("Expected ValueError")