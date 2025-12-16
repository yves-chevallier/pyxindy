import pytest
from tests_paths import XINDY_TESTS_DIR as FIXTURES

from xindy.raw.reader import RawIndexSyntaxError, load_raw_index, parse_raw_index


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


def test_boolean_flags_are_parsed():
    expr = '(indexentry :key ("foo") :locref "1" :open-range)'
    entry = parse_raw_index(expr)[0]
    assert entry.extras["open-range"] is True


def test_concatenated_keywords_are_split():
    expr = '(indexentry :key ("foo") :locref "2" :attr "bar":close-range)'
    entry = parse_raw_index(expr)[0]
    assert entry.attr == "bar"
    assert entry.extras["close-range"] is True
