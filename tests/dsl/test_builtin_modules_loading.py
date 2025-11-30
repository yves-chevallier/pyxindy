from pathlib import Path

import pytest

from tests_paths import XINDY_MODULES_DIR as MODULES_DIR
from xindy.dsl.interpreter import StyleInterpreter


@pytest.mark.parametrize(
    "module_path",
    sorted(MODULES_DIR.rglob("*.xdy")),
)
def test_builtin_module_can_be_loaded(module_path: Path):
    state = StyleInterpreter().load(module_path)
    assert module_path in state.loaded_files
