from pathlib import Path

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index.builder import build_index_entries
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
    index = build_index_entries(raw_entries, state)
    groups = index.groups
    labels = [group.label for group in groups]
    assert labels == ["a", "b", "c", "r", "t"]
    assert groups[0].entry_count == 2
    a_group_nodes = groups[0].nodes
    assert [node.term for node in a_group_nodes] == ["apple"]
    range_node = groups[3].nodes[0]
    assert len(range_node.ranges) == 1
    assert [ref.locref_string for ref in range_node.ranges[0]] == ["10", "11"]
    topic_node = groups[-1].nodes[0]
    assert topic_node.term == "topic"
    assert topic_node.children[0].term == "subtopic"


def test_group_entries_falls_back_to_alphabet():
    state, index = _load_state_and_entries(
        "attr1.xdy",
        "attr1.raw",
        only_numeric=True,
    )
    groups = index.groups
    assert groups[0].label.lower().startswith("a")
    assert groups[0].nodes[0].term == "a"
