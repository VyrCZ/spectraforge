from functools import wraps
from modules.engine import Engine

class EngineManager:
    _instance = None  # ← Added for singleton**
    _initialized = False  # ← Added guard so __init__ only runs once**

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:  # ← Ensure only one instance ever created
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self.__class__._initialized:
            return  # ← Skip if already initialized
        self.engines = []
        self.active_engine = None
        self.__class__._initialized = True  # ← Mark init-done**

    def register_engine(self, engine: Engine):
        """
        Register a new engine.
        """
        if engine not in self.engines:
            self.engines.append(engine)
        else:
            print(f"Engine {engine} is already registered.")
        if self.active_engine is None:
            engine.on_enable()
            self.active_engine = engine
        engine.manager = self

    @staticmethod
    def requires_active(func):
        """
        Decorator to ensure an engine is active before executing the function.
        """
        @wraps(func)
        def wrapper(engine_instance: Engine, *args, **kwargs):
            mgr = getattr(engine_instance, 'manager', None)
            if mgr is None or engine_instance not in mgr.engines:
                raise EngineManager.EngineNotRegisteredError(engine_instance)

            if mgr.active_engine is engine_instance:
                pass  # already active
            else:
                mgr.active_engine.on_disable()
                engine_instance.on_enable()
                mgr.active_engine = engine_instance

            return func(engine_instance, *args, **kwargs)
        return wrapper

    class EngineNotRegisteredError(Exception):
        def __init__(self, engine):
            super().__init__(f"Engine {engine} is not registered.")
            self.engine = engine
