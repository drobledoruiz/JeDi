import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def load_module():
    def _load(name: str, relative_path: str):
        base = Path(__file__).resolve().parents[1]
        module_path = base / relative_path
        spec = importlib.util.spec_from_file_location(name, module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    return _load
