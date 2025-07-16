import os
import zlib
import inspect

CACHE_DIR = ".cache"

def hash_data(data: any) -> str:
    """
    Generate a hash for the given data.
    """
    h = 0xcbf29ce484222325
    for c in str(data.encode('utf-8')):
        h ^= ord(c)
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h

def hash_module(module) -> str:
    """
    Generate a hash for the given module.
    """
    try:
        src = inspect.getsource(module)
    except (OSError, IOError):
        with open(module.__file__, 'r', encoding='utf-8') as f:
            src = f.read()
    return hash_data(src)

def set_cache_by_name(path: str, name: str, cache_data: str):
    """
    Set a cache value by name in the specified path.
    """
    dir_path = os.path.join(CACHE_DIR, path)
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(CACHE_DIR, path, f"{name}.cache"), "w") as f:
        f.write(cache_data)

def get_cache_by_name(path: str, name: str) -> str:
    """
    Get a cache value by name from the specified path.
    """
    dir_path = os.path.join(CACHE_DIR, path)
    os.makedirs(dir_path, exist_ok=True)
    cache_file = os.path.join(dir_path, f"{name}.cache")
    os.makedirs(os.path.join(CACHE_DIR, path), exist_ok=True)
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return f.read()
    return None

def set_cache_by_data(path: str, key_data: any, cache_data: str):
    """
    Set a cache value linked to specific data in the specified path.
    """
    dir_path = os.path.join(CACHE_DIR, path)
    os.makedirs(dir_path, exist_ok=True)
    data_hash = hash_data(str(key_data))
    with open(os.path.join(dir_path, f"{data_hash}.cache"), "w") as f:
        f.write(cache_data)

def get_cache_by_data(path: str, key_data: any) -> str:
    """
    Get a cache value linked to specific data from the specified path.
    """
    data_hash = hash_data(str(key_data))
    cache_file = os.path.join(CACHE_DIR, path, f"{data_hash}.cache")
    os.makedirs(os.path.join(CACHE_DIR, path), exist_ok=True)
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return f.read()
    return None