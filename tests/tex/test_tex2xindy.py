from pathlib import Path

from xindy.raw.reader import load_raw_index
from xindy.tex.tex2xindy import convert_idx_to_raw_entries, parse_idx_line

TESTS_DIR = Path(__file__).resolve().parents[2] / "xindy-src" / "xindy-2.1" / "tests"


def test_parse_idx_line_extracts_term_attr_and_loc():
    entry = parse_idx_line(r"\indexentry{Register!Instruktions-|textbf}{7}")
    assert entry is not None
    assert entry.key == ("Register", "Instruktions-")
    assert entry.display_key is None
    assert entry.attr == "textbf"
    assert entry.loc == "7"


def test_parse_idx_line_handles_escapes_and_display():
    entry = parse_idx_line(r"\indexentry{foo\!bar@\\alpha!qux\@at|textit}{42}")
    assert entry is not None
    assert entry.key == ("foo!bar", "qux@at")
    assert entry.display_key == ("\\alpha", "qux@at")
    assert entry.attr == "textit"
    assert entry.loc == "42"


def test_parse_idx_line_crossref():
    entry = parse_idx_line(r"\indexentry{Apple|see{Orange!Tree}}{12}")
    assert entry is not None
    assert entry.key == ("Apple",)
    assert entry.attr == "see"
    assert entry.xref_target == ("Orange", "Tree")
    assert entry.loc is None


def test_convert_idx_matches_reference_raw():
    idx_path = TESTS_DIR / "infII.idx"
    raw_expected = load_raw_index(TESTS_DIR / "infII.raw")
    converted = convert_idx_to_raw_entries(idx_path)

    assert len(converted) == len(raw_expected)
    # compare tuples (key, attr, locref) ignoring extras and order differences
    expected_set = {(e.key, e.attr, e.locref) for e in raw_expected}
    converted_set = {(e.key, e.attr, e.locref) for e in converted}
    assert converted_set == expected_set
