from modules.engine_test1 import EngineTest1
from modules.engine_test2 import EngineTest2
from modules.engine_manager import EngineManager

engine_one = EngineTest1()
engine_two = EngineTest2()
manager = EngineManager()
manager.register_engine(engine_one)
manager.register_engine(engine_two)
engine_one.test_function()
engine_two.test_function()