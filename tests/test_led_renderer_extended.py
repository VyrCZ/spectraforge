import pytest
from unittest.mock import MagicMock, Mock, patch

pytest.importorskip("sys")


def create_mock_setup(led_count=60):
    """Helper to create a mock Setup object."""
    setup = MagicMock()
    setup.coords = [[i, 0, 0] for i in range(led_count)]
    return setup


def test_led_renderer_constructor_accepts_setup_object(monkeypatch):
    """Test that LEDRenderer constructor accepts Setup object."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(60)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    assert renderer.led_count == 60


def test_led_renderer_setitem_assigns_color(monkeypatch):
    """Test __setitem__ correctly assigns pixel colors."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(60)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    renderer[10] = [255, 128, 64]
    assert renderer.leds[10] == (255, 128, 64)


def test_led_renderer_getitem_retrieves_color(monkeypatch):
    """Test __getitem__ retrieves pixel colors."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(60)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    renderer[5] = [100, 50, 200]
    color = renderer[5]
    assert color == (100, 50, 200)


def test_led_renderer_set_brightness_updates_attribute(monkeypatch):
    """Test that set_brightness updates the brightness attribute."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(60)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    renderer.set_brightness(0.7)
    assert renderer.brightness == 0.7


def test_led_renderer_set_brightness_clamps_range(monkeypatch):
    """Test that set_brightness clamps values to 0.0-1.0."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(60)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    renderer.set_brightness(1.5)
    assert 0.0 <= renderer.brightness <= 1.0
    
    renderer.set_brightness(-0.5)
    assert 0.0 <= renderer.brightness <= 1.0


def test_led_renderer_fill_all_pixels(monkeypatch):
    """Test fill method sets all pixels to same color."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(10)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    renderer.fill((255, 0, 0))
    for i in range(10):
        assert renderer.leds[i] == (255, 0, 0)


def test_led_renderer_clear_all_pixels(monkeypatch):
    """Test clear method sets all pixels to black."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(10)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    renderer.fill((255, 255, 255))
    renderer.clear()
    
    for i in range(10):
        assert renderer.leds[i] == (0, 0, 0)


def test_led_renderer_len_returns_led_count(monkeypatch):
    """Test __len__ returns correct LED count."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(42)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    assert len(renderer) == 42


def test_led_renderer_set_colors_all_at_once(monkeypatch):
    """Test set_colors method sets all colors at once."""
    from modules.led_renderer import LEDRenderer
    setup = create_mock_setup(3)
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    renderer.set_colors(colors)
    
    for i, color in enumerate(colors):
        assert renderer.leds[i] == color


def test_dummy_renderer_setitem_pixel(monkeypatch):
    """Test DummyRenderer __setitem__ for pixel assignment."""
    from modules.led_renderer import DummyRenderer
    
    setup = create_mock_setup(20)
    
    dummy = DummyRenderer(setup)
    dummy[5] = [100, 50, 25]
    
    assert dummy.leds[5] == (100, 50, 25)


def test_dummy_renderer_fill_all(monkeypatch):
    """Test DummyRenderer fill method."""
    from modules.led_renderer import DummyRenderer
    
    setup = create_mock_setup(5)
    
    dummy = DummyRenderer(setup)
    dummy.fill((200, 100, 50))
    
    for i in range(5):
        assert dummy.leds[i] == (200, 100, 50)


def test_dummy_renderer_clear_all(monkeypatch):
    """Test DummyRenderer clear method."""
    from modules.led_renderer import DummyRenderer
    
    setup = create_mock_setup(5)
    
    dummy = DummyRenderer(setup)
    dummy.fill((255, 255, 255))
    dummy.clear()
    
    for i in range(5):
        assert dummy.leds[i] == (0, 0, 0)


def test_dummy_renderer_show_returns_none(monkeypatch):
    """Test that DummyRenderer.show() returns None."""
    from modules.led_renderer import DummyRenderer
    
    setup = create_mock_setup(10)
    
    dummy = DummyRenderer(setup)
    result = dummy.show()
    
    assert result is None


def test_led_renderer_show_method_exists(monkeypatch):
    """Test that LEDRenderer has show method."""
    from modules.led_renderer import LEDRenderer
    
    setup = create_mock_setup(10)
    
    with patch("modules.led_renderer.socket.socket"):
        renderer = LEDRenderer(setup)
    
    assert hasattr(renderer, "show")
    assert callable(renderer.show)
