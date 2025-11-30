from pathlib import Path

from xindy.dsl.interpreter import StyleInterpreter


def test_require_resolves_builtin_modules(tmp_path):
    xdy = tmp_path / "use_module.xdy"
    xdy.write_text('(require "class/pagenums.xdy")', encoding="utf-8")

    state = StyleInterpreter().load(xdy)

    assert "page-numbers" in state.location_classes
