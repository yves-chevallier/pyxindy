from pathlib import Path

from tests_paths import XINDY_MODULES_DIR as MODULES_DIR
from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import build_index_entries
from xindy.markup import render_index
from xindy.raw.reader import load_raw_index


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_makeidx_module_snapshot():
    style_path = MODULES_DIR / "tex" / "makeidx.xdy"
    state = StyleInterpreter().load(style_path)
    raw_entries = load_raw_index(DATA_DIR / "makeidx_module.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index, style_state=state)
    expected = (DATA_DIR / "makeidx_module.ind").read_text()
    assert output == expected
