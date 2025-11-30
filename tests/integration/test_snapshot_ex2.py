from pathlib import Path

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import build_index_entries
from xindy.markup import render_index
from xindy.raw.reader import load_raw_index

TESTS_DIR = Path(__file__).resolve().parents[2] / "xindy-src" / "xindy-2.1" / "tests"


def test_ex2_snapshot():
    state = StyleInterpreter().load(TESTS_DIR / "ex2.xdy")
    raw_entries = load_raw_index(TESTS_DIR / "ex2.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index, style_state=state)
    expected = (TESTS_DIR / "ex2.cmp").read_text(encoding="latin-1")
    assert output.strip() == expected.strip()
