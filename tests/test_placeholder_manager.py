from modules import placeholder_manager
from modules.config_manager import Config


def reset_config(monkeypatch):
    Config._instance = None
    config = Config()
    config.config = {}
    monkeypatch.setattr(Config, "save", lambda self: None)
    return config


def test_pick_first_file_or_default(tmp_path):
    assert placeholder_manager._pick_first_file_or_default(str(tmp_path / "missing"), ".json", "default") == "default"
    setup_dir = tmp_path / "setups"
    setup_dir.mkdir()
    (setup_dir / "demo.json").write_text("{}", encoding="utf-8")
    assert placeholder_manager._pick_first_file_or_default(str(setup_dir), ".json", "default") == "demo"


def test_check_config_populates_defaults(tmp_path, monkeypatch):
    reset_config(monkeypatch)
    monkeypatch.setattr(placeholder_manager, "SETUP_DIR", str(tmp_path / "setups"))
    monkeypatch.setattr(placeholder_manager, "EFFECTS_DIR", str(tmp_path / "effects"))
    monkeypatch.setattr(placeholder_manager, "SANDBOX_DIR", str(tmp_path / "sandbox"))
    (tmp_path / "setups").mkdir()
    (tmp_path / "effects").mkdir()
    (tmp_path / "sandbox").mkdir()
    (tmp_path / "setups" / "tree.json").write_text("{}", encoding="utf-8")
    (tmp_path / "effects" / "rainbow.py").write_text("pass", encoding="utf-8")
    (tmp_path / "sandbox" / "main.py").write_text("pass", encoding="utf-8")

    placeholder_manager._check_config()
    config = Config().config
    assert config["current_setup"] == "tree"
    assert config["current_effect"] == "rainbow"
    assert config["sandbox_opened_file"] == "main"
    assert config["brightness"] == 1.0
    assert config["performance_mode"] == "high"
    assert config["enhance_colors"] is True


def test_check_creates_missing_defaults(tmp_path, monkeypatch):
    reset_config(monkeypatch)
    monkeypatch.setattr(placeholder_manager, "SETUP_DIR", str(tmp_path / "setups"))
    monkeypatch.setattr(placeholder_manager, "EFFECTS_DIR", str(tmp_path / "effects"))
    monkeypatch.setattr(placeholder_manager, "SANDBOX_DIR", str(tmp_path / "sandbox"))
    placeholder_manager.check()
    assert (tmp_path / "setups" / "default_setup.json").exists()
    assert (tmp_path / "effects" / "breathing.py").exists()
    assert (tmp_path / "sandbox" / "default.py").exists()