import os
from flask import current_app, g
from app.json_store import JsonStore


def get_store(filename):
    try:
        if not hasattr(g, '_store_cache'):
            g._store_cache = {}
        cache = g._store_cache
    except (AttributeError, RuntimeError):
        return _create_store(filename)
    if filename not in cache:
        cache[filename] = _create_store(filename)
    return cache[filename]


def _create_store(filename):
    data_dir = current_app.config.get(
        "DATA_DIR",
        os.path.join(os.path.dirname(__file__), "..", "data"),
    )
    return JsonStore(os.path.join(data_dir, filename))
