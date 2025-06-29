import json

class Config:
    _instance = None
    CONFIG_PATH = "config/server_config.json"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init_once(*args, **kwargs)
        return cls._instance

    def _init_once(self, *args, **kwargs):
        self.config = {}
        self.load_config()

    def load_config(self):
        with open(self.CONFIG_PATH, 'r') as file:
            self.config = json.load(file)
            print(f"Config: {self.config}")

    def save_config(self):
        with open(self.CONFIG_PATH, 'w') as file:
            json.dump(self.config, file, indent=4)

    def get(self, key, default=None):
        """
        Get a configuration value by key.
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value by key.
        """
        self.config[key] = value
        self.save_config()

    def __getitem__(self, key):
        """
        Get a configuration value by key using dictionary-like access.
        """
        return self.get(key)
    
    def __setitem__(self, key, value):
        """
        Set a configuration value by key using dictionary-like access.
        """
        self.set(key, value)