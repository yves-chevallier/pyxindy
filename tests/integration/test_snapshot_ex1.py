from tests_paths import XINDY_TESTS_DIR as TESTS_DIR

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import build_index_entries
from xindy.markup import render_index
from xindy.raw.reader import load_raw_index


def test_ex1_snapshot():
    state = StyleInterpreter().load(TESTS_DIR / "ex1.xdy")
    raw_entries = load_raw_index(TESTS_DIR / "ex1.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index, style_state=state)
    expected = (TESTS_DIR / "ex1.cmp").read_text(encoding="latin-1")
    assert output.strip() == expected.strip()
