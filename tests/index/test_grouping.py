from pathlib import Path

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index.builder import build_index_entries
from xindy.index.grouping import group_entries_by_letter
from xindy.raw.reader import load_raw_index

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "xindy-src" / "xindy-2.1" / "tests"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _load_state_and_entries(style_name: str, raw_name: str, only_numeric: bool = False):
    interpreter = StyleInterpreter()
    state = interpreter.load(TESTS_DIR / style_name)
    raw_entries = load_raw_index(TESTS_DIR / raw_name)
    if only_numeric:
        raw_entries = [entry for entry in raw_entries if entry.locref.isdigit()]
    entries = build_index_entries(raw_entries, state)
    return state, entries


def test_group_entries_respects_defined_letter_groups_and_hierarchy():
    interpreter = StyleInterpreter()
    state = interpreter.load(DATA_DIR / "simple.xdy")
    raw_entries = load_raw_index(DATA_DIR / "simple.raw")
    entries = build_index_entries(raw_entries, state)
    groups = group_entries_by_letter(entries, state)
    labels = [group.label for group in groups]
    assert labels == ["a", "b", "c", "t"]
    a_group_nodes = groups[0].nodes
    assert [node.term for node in a_group_nodes] == ["apple"]
    topic_node = groups[-1].nodes[0]
    assert topic_node.term == "topic"
    assert topic_node.children[0].term == "subtopic"


def test_group_entries_falls_back_to_alphabet():
    state, entries = _load_state_and_entries("attr1.xdy", "attr1.raw", only_numeric=True)
    groups = group_entries_by_letter(entries, state)
    assert groups[0].label.lower().startswith("a")
    assert groups[0].nodes[0].term == "a"
