from pathlib import Path

import pytest

from xindy.dsl.interpreter import StyleInterpreter

MODULES_DIR = Path(__file__).resolve().parents[2] / "xindy-src" / "xindy-2.1" / "modules"


@pytest.mark.parametrize(
    "module_path",
    sorted(MODULES_DIR.rglob("*.xdy")),
)
def test_builtin_module_can_be_loaded(module_path: Path):
    state = StyleInterpreter().load(module_path)
    assert module_path in state.loaded_files
