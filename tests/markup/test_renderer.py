from pathlib import Path

from xindy.dsl.interpreter import StyleInterpreter
from xindy.index import build_index_entries
from xindy.markup import MarkupConfig, render_index
from xindy.raw.reader import load_raw_index

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_renderer_outputs_letter_groups_and_entries():
    state = StyleInterpreter().load(DATA_DIR / "simple.xdy")
    raw_entries = load_raw_index(DATA_DIR / "simple.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index)
    assert "A" in output
    assert "apple 1, 5" in output
    assert "topic" in output


def test_renderer_shows_crossrefs():
    state = StyleInterpreter().load(DATA_DIR / "crossref.xdy")
    raw_entries = load_raw_index(DATA_DIR / "crossref.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(
        index,
        MarkupConfig(
            crossref_prefix="see ",
            locref_prefix="[",
            locref_separator="; ",
            crossref_label_template="see ",
        ),
    )
    assert "see target" in output
