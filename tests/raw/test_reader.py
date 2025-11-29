from pathlib import Path

import pytest

from xindy.raw.reader import RawIndexSyntaxError, load_raw_index, parse_raw_index

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "xindy-src" / "xindy-2.1" / "tests"


def test_load_raw_index_reads_fixture():
    entries = load_raw_index(FIXTURES / "attr1.raw")
    assert entries  # sanity check
    first = entries[0]
    assert first.key == ("a",)
    assert first.locref == "13"
    assert first.attr == "def"


def test_parse_raw_index_keeps_unknown_properties():
    expr = '(indexentry :key ("foo") :locref "1" :attr "bar" :extra "baz")'
    entries = parse_raw_index(expr)
    assert entries[0].extras["extra"] == "baz"


def test_missing_key_is_rejected():
    broken = '(indexentry :locref "1")'
    with pytest.raises(RawIndexSyntaxError):
        parse_raw_index(broken)
