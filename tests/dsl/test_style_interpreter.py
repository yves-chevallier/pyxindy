from tests_paths import XINDY_TESTS_DIR as TESTS_DIR
from xindy.dsl.interpreter import StyleInterpreter


def test_attr1_style_defines_location_classes_and_attributes():
    interpreter = StyleInterpreter()
    state = interpreter.load(TESTS_DIR / "attr1.xdy")

    assert "page-numbers" in state.location_classes
    assert "follows" in state.location_classes
    assert {"def", "imp", "default", "follows"}.issubset(state.attributes)
    assert any(path.name in {"modules", "_modules"} for path in state.search_paths)
    assert any(path.name == "testbed.xdy" for path in state.loaded_files)


def test_require_is_idempotent():
    interpreter = StyleInterpreter()
    state = interpreter.load(TESTS_DIR / "attr1.xdy")
    before = len(state.loaded_files)
    interpreter.load(TESTS_DIR / "attr1.xdy")
    assert len(state.loaded_files) == before
