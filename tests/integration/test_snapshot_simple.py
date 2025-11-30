from pathlib import Path

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import build_index_entries
from xindy.markup import render_index
from xindy.raw.reader import load_raw_index


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SNAPSHOT = DATA_DIR / "simple.ind"


def test_simple_snapshot(tmp_path):
    state = StyleInterpreter().load(DATA_DIR / "simple.xdy")
    raw_entries = load_raw_index(DATA_DIR / "simple.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index, style_state=state)
    snapshot_content = SNAPSHOT.read_text()
    assert output == snapshot_content
