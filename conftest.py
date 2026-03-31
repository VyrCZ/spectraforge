"""
Root-level conftest: stub out hardware-only and platform-specific dependencies
before any test module is collected, so the test suite runs on any platform
(Linux CI, Windows, etc.) without physical Raspberry Pi hardware or a live
gevent server loop.
"""
import sys
import types
from unittest.mock import MagicMock


def _make_module(name, **attrs):
    mod = types.ModuleType(name)
    mod.__dict__.update(attrs)
    return mod


# --- Stub gevent.monkey so patch_all() is a no-op during tests ---
if "gevent" not in sys.modules:
    gevent_mod = _make_module("gevent")
    monkey_mod = _make_module("gevent.monkey", patch_all=lambda **kw: None)
    gevent_mod.monkey = monkey_mod
    sys.modules["gevent"] = gevent_mod
    sys.modules["gevent.monkey"] = monkey_mod
else:
    # gevent already imported — replace patch_all with a no-op
    sys.modules["gevent.monkey"].patch_all = lambda **kw: None

# --- Stub neopixel (Raspberry Pi LED library) ---
class _NeoPixel:
    def __init__(self, pin, n, auto_write=True, **kw):
        self.n = n
        self._data = [(0, 0, 0)] * n

    def __setitem__(self, idx, val):
        self._data[idx] = val

    def __getitem__(self, idx):
        return self._data[idx]

    def show(self):
        pass

    def fill(self, color):
        self._data = [color] * self.n


sys.modules.setdefault("neopixel", _make_module("neopixel", NeoPixel=_NeoPixel))

# --- Stub board (Raspberry Pi GPIO pin definitions) ---
sys.modules.setdefault("board", _make_module("board", D18=18))

# --- Stub pyvista (3D visualisation, not available in headless CI) ---
if "pyvista" not in sys.modules:
    pv_mod = _make_module("pyvista")
    pv_mod.PolyData = MagicMock
    pv_mod.Plotter = MagicMock
    sys.modules["pyvista"] = pv_mod
