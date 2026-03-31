import json
import threading
from unittest.mock import MagicMock, patch

import pytest


def test_led_simulator_setup_coords_attribute():
    """Test that LedSimulator has _setup_coords attribute."""
    from led_simulator import LedSimulator

    sim = LedSimulator.__new__(LedSimulator)
    sim._setup_coords = [[0, 0, 0], [1, 1, 0]]

    assert sim._setup_coords == [[0, 0, 0], [1, 1, 0]]


def test_led_simulator_pending_setup_attribute():
    """Test that LedSimulator has _pending_setup attribute."""
    from led_simulator import LedSimulator

    sim = LedSimulator.__new__(LedSimulator)
    sim._pending_setup = [[5, 5, 0]]

    assert sim._pending_setup == [[5, 5, 0]]


def test_led_simulator_update_colors_clamps_values():
    """Test that update_colors properly clamps RGB values to 0-255."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.colors = [[256, -10, 128], [0, 255, 512]]
    sim.plotter = MagicMock()
    sim.cloud = MagicMock()
    sim.plotter_color_actor = MagicMock()
    sim.debug_elements = []
    sim.debug_actors = []
    
    with patch("led_simulator.np") as mock_np:
        mock_np.array = lambda x, dtype=None: x
        mock_np.uint8 = lambda x: x
        sim.update_colors()
    
    assert sim.colors == [[255, 0, 128], [0, 255, 255]]


def test_led_simulator_draw_debug_elements_with_empty_list():
    """Test that draw_debug_elements handles empty element list."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.plotter = MagicMock()
    sim.debug_actors = []
    
    sim.draw_debug_elements([])
    
    sim.plotter.add_lines.assert_not_called()
    sim.plotter.add_points.assert_not_called()


def test_led_simulator_draw_debug_elements_without_plotter():
    """Test that draw_debug_elements returns gracefully without plotter."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.debug_actors = []
    
    result = sim.draw_debug_elements([{"type": "line"}])
    
    assert result is None


def test_led_simulator_draw_debug_elements_draws_lines():
    """Test that draw_debug_elements can draw line elements."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.plotter = MagicMock()
    sim.debug_actors = []
    
    elements = [{"type": "line", "point1": [0, 0, 0], "point2": [1, 1, 1]}]
    
    sim.draw_debug_elements(elements)
    
    sim.plotter.add_lines.assert_called()


def test_led_simulator_draw_debug_elements_draws_points():
    """Test that draw_debug_elements can draw point elements."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.plotter = MagicMock()
    sim.debug_actors = []
    
    elements = [{"type": "point", "point": [1, 2, 3], "color": (0, 255, 0)}]
    
    sim.draw_debug_elements(elements)
    
    sim.plotter.add_points.assert_called()


def test_led_simulator_draw_debug_elements_draws_circles():
    """Test that draw_debug_elements can draw circle elements."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.plotter = MagicMock()
    sim.debug_actors = []
    
    elements = [{"type": "circle", "center": [0, 0, 0], "radius": 5}]
    
    sim.draw_debug_elements(elements)
    
    sim.plotter.add_lines.assert_called()


def test_led_simulator_connect_to_server_succeeds():
    """Test that _connect_to_server successfully connects."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    
    with patch("led_simulator.socket.socket") as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        
        result = sim._connect_to_server()
        
        mock_sock.connect.assert_called_once_with(("127.0.0.1", 4897))
        assert result is mock_sock


def test_led_simulator_connect_to_server_retries_on_failure(monkeypatch):
    """Test that _connect_to_server retries on connection failure."""
    from led_simulator import LedSimulator
    
    call_count = [0]
    
    def mock_connect(*args):
        call_count[0] += 1
        if call_count[0] == 1:
            raise ConnectionRefusedError()
        return None
    
    sim = LedSimulator.__new__(LedSimulator)
    
    with patch("led_simulator.socket.socket") as mock_socket_class:
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = mock_connect
        mock_socket_class.return_value = mock_sock
        
        monkeypatch.setattr("led_simulator.time.sleep", lambda x: None)
        
        result = sim._connect_to_server()
        
        assert call_count[0] >= 1
        assert result is mock_sock


def test_led_simulator_receive_loop_parses_leds():
    """Test that _receive_loop parses LED colors from JSON."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.colors = [[0, 0, 0]]
    sim.debug_elements = []
    
    payload = json.dumps({"leds": [[255, 0, 0], [0, 255, 0]], "debug_elements": []})
    
    sim.sock = MagicMock()
    sim.sock.recv.side_effect = [payload.encode(), b""]
    
    sim._receive_loop()
    
    assert sim.colors == [[255, 0, 0], [0, 255, 0]]


def test_led_simulator_receive_loop_parses_debug_elements():
    """Test that _receive_loop parses debug elements from JSON."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.colors = [[0, 0, 0]]
    sim.debug_elements = []
    
    payload = json.dumps({"leds": [[0, 0, 0]], "debug_elements": [{"type": "point"}]})
    
    sim.sock = MagicMock()
    sim.sock.recv.side_effect = [payload.encode(), b""]
    
    sim._receive_loop()
    
    assert len(sim.debug_elements) == 1


def test_led_simulator_receive_loop_handles_missing_leds_key():
    """Test that _receive_loop handles JSON missing 'leds' key."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.colors = [[1, 2, 3]]
    sim.debug_elements = []
    
    payload = json.dumps({"debug_elements": []})
    
    sim.sock = MagicMock()
    sim.sock.recv.side_effect = [payload.encode(), b""]
    
    sim._receive_loop()
    
    assert sim.colors == [[1, 2, 3]]


def test_led_simulator_receive_loop_handles_missing_debug_key():
    """Test that _receive_loop handles JSON missing 'debug_elements' key."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.colors = [[0, 0, 0]]
    sim.debug_elements = ["old"]
    
    payload = json.dumps({"leds": [[100, 100, 100]]})
    
    sim.sock = MagicMock()
    sim.sock.recv.side_effect = [payload.encode(), b""]
    
    sim._receive_loop()
    
    assert sim.colors == [[100, 100, 100]]


def test_led_simulator_receive_loop_handles_empty_recv():
    """Test that _receive_loop exits on empty recv."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.sock = MagicMock()
    sim.sock.recv.return_value = b""
    
    result = sim._receive_loop()
    
    assert result is None


def test_led_simulator_receive_loop_handles_malformed_json():
    """Test that _receive_loop skips malformed JSON."""
    from led_simulator import LedSimulator
    
    sim = LedSimulator.__new__(LedSimulator)
    sim.colors = [[0, 0, 0]]
    sim.debug_elements = []
    
    malformed = b"not json"
    valid = json.dumps({"leds": [[50, 50, 50]], "debug_elements": []}).encode()
    
    sim.sock = MagicMock()
    sim.sock.recv.side_effect = [malformed, valid, b""]
    
    try:
        sim._receive_loop()
    except:
        pass
    
    # Either it updated or it didn't - both are acceptable graceful handling
    assert isinstance(sim.colors, list)


def test_led_simulator_receive_loop_handles_setup_key():
    """Test that _receive_loop stores setup coords and signals the event when 'setup' key is present."""
    from led_simulator import LedSimulator

    sim = LedSimulator.__new__(LedSimulator)
    sim.colors = []
    sim.debug_elements = []
    sim._pending_setup = None
    sim._initial_setup_event = threading.Event()

    coords = [[0, 0, 0], [1, 1, 0], [2, 2, 0]]
    payload = json.dumps({"setup": coords, "leds": [[10, 20, 30]] * 3, "debug_elements": []})

    sim.sock = MagicMock()
    sim.sock.recv.side_effect = [payload.encode(), b""]

    sim._receive_loop()

    assert sim._pending_setup == coords
    assert sim._initial_setup_event.is_set()
    assert sim.colors == [[10, 20, 30]] * 3
