from pathlib import Path

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import build_index_entries
from xindy.markup import render_index
from xindy.raw.reader import load_raw_index
from xindy.tex.tex2xindy import convert_idx_to_raw_entries


TESTS_DIR = Path(__file__).resolve().parents[2] / "xindy-src" / "xindy-2.1" / "tests"


def test_infII_snapshot():
    state = StyleInterpreter().load(TESTS_DIR / "infII.xdy")
    # validate both idx conversion and raw path
    from_idx = convert_idx_to_raw_entries(TESTS_DIR / "infII.idx")
    raw_entries = load_raw_index(TESTS_DIR / "infII.raw")
    assert {(e.key, e.attr, e.locref) for e in from_idx} == {
        (e.key, e.attr, e.locref) for e in raw_entries
    }
    index = build_index_entries(raw_entries, state)
    output = render_index(index, style_state=state)
    expected = (TESTS_DIR / "infII.cmp").read_text(encoding="latin-1")
    assert output.strip() == expected.strip()

    # End-to-end from .idx without touching the bundled .raw
    index_from_idx = build_index_entries(from_idx, state)
    output_from_idx = render_index(index_from_idx, style_state=state)
    assert output_from_idx.strip() == expected.strip()
