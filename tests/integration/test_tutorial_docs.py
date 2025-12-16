from pathlib import Path

from tests_paths import XINDY_TESTS_DIR as REFERENCE_DIR

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import build_index_entries
from xindy.markup import render_index
from xindy.raw.reader import load_raw_index


DOCS_DIR = Path(__file__).resolve().parents[2] / "docs" / "tutorial"


def _render(style_name: str, raw_name: str) -> str:
    state = StyleInterpreter().load(DOCS_DIR / style_name)
    raw_entries = load_raw_index(DOCS_DIR / raw_name)
    index = build_index_entries(raw_entries, state)
    return render_index(index, style_state=state).strip()


def test_docs_style1_matches_reference_snapshot():
    assert (
        _render("style1.xdy", "ex1.raw")
        == (REFERENCE_DIR / "ex1.cmp").read_text(encoding="latin-1").strip()
    )


def test_docs_style2_matches_reference_snapshot():
    assert (
        _render("style2.xdy", "ex2.raw")
        == (REFERENCE_DIR / "ex2.cmp").read_text(encoding="latin-1").strip()
    )
