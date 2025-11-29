from pathlib import Path

import pytest

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import IndexBuilderError, build_index_entries
from xindy.raw.reader import load_raw_index

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "xindy-src" / "xindy-2.1" / "tests"


def _load_state_and_entries():
    interpreter = StyleInterpreter()
    state = interpreter.load(TESTS_DIR / "attr1.xdy")
    raw_entries = load_raw_index(TESTS_DIR / "attr1.raw")
    numeric_entries = [entry for entry in raw_entries if entry.locref.isdigit()]
    return state, numeric_entries


def test_build_index_entries_converts_raw_data_using_style():
    state, raw_entries = _load_state_and_entries()
    index = build_index_entries(raw_entries[:3], state)
    first = index.groups[0].nodes[0]
    assert first.key == ("a",)
    assert first.attribute == "def"
    assert first.locrefs[0].layers == ("13",)
    assert index.groups[0].entry_count == 3


def test_missing_attribute_uses_default_group():
    state, raw_entries = _load_state_and_entries()
    entry_without_attr = next(entry for entry in raw_entries if entry.attr is None)
    index = build_index_entries([entry_without_attr], state)
    assert index.groups[0].nodes[0].attribute == "default"


def test_unknown_location_class_raises():
    state, raw_entries = _load_state_and_entries()
    with pytest.raises(IndexBuilderError):
        build_index_entries([raw_entries[0]], state, default_locclass="missing")


def test_entries_are_sorted_by_key():
    state, raw_entries = _load_state_and_entries()
    unsorted = list(reversed(raw_entries[:5]))
    index = build_index_entries(unsorted, state)
    keys = [node.key for node in index.groups[0].nodes]
    assert keys == sorted(keys)
