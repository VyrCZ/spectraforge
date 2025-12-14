import json
import os
import time
from json import JSONDecodeError
from modules.log_manager import Log

class Config:
    _instance = None
    CONFIG_PATH = "config/server_config.json"
    _DEFAULT_CONFIG = {"current_setup": ""}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init_once(*args, **kwargs)
        return cls._instance

    def _init_once(self, *args, **kwargs):
        self.config = {}
        self.load()

    def load(self, retries=5, delay_s=0.05):
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)

        if not os.path.exists(self.CONFIG_PATH):
            self.config = dict(self._DEFAULT_CONFIG)
            self.save()
            return

        last_err = None
        for _ in range(retries):
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as file:
                    text = file.read()

                if not text.strip():
                    raise JSONDecodeError("Empty config file", text, 0)

                self.config = json.loads(text)
                Log.info("Config", "Configuration loaded successfully.")
                return
            except JSONDecodeError as e:
                last_err = e
                time.sleep(delay_s)

        Log.warn("Config", f"Config load failed (keeping previous): {last_err}")

    def save(self):
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
        tmp_path = self.CONFIG_PATH + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(self.config, file, indent=4)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp_path, self.CONFIG_PATH)