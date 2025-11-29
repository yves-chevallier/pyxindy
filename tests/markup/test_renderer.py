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
    output = render_index(
        index,
        MarkupConfig(
            range_separator="--",
            default_locref_format=MarkupConfig().default_locref_format.__class__(
                open="[",
                close="]",
            ),
            letter_group_separator="",
            index_open="<<INDEX>>",
            index_close="<<END>>",
            letter_group_open="<<GROUP {label}>>",
            letter_group_close="<<ENDGROUP {label}>>",
            entry_template="{indent}- {term}{locrefs}",
        ),
    )
    assert "A" in output
    assert "<<INDEX>>" in output
    assert "<<END>>" in output
    assert "<<GROUP A>>" in output
    assert "<<ENDGROUP A>>" in output
    assert "- apple [1, 5]" in output
    assert "10--11" in output


def test_renderer_shows_crossrefs():
    state = StyleInterpreter().load(DATA_DIR / "crossref.xdy")
    raw_entries = load_raw_index(DATA_DIR / "crossref.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(
        index,
        MarkupConfig(
            crossref_prefix="see ",
            default_locref_format=MarkupConfig().default_locref_format.__class__(
                prefix="[",
                separator="; ",
            ),
            crossref_label_template="see ",
            letter_header_prefix="(",
            letter_header_suffix=")",
            entry_open_templates={0: "<{content}>"},
            entry_close_templates={0: " END"},
            crossref_unverified_suffix=" (?)",
        ),
        style_state=state,
    )
    assert "(A)" in output
    assert "<see-target" in output
    assert "END" in output
    assert "see target" in output
    assert "see missing (?)" in output


def test_renderer_respects_max_depth():
    state = StyleInterpreter().load(DATA_DIR / "simple.xdy")
    raw_entries = load_raw_index(DATA_DIR / "simple.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index, MarkupConfig(max_depth=0))
    assert "topic" in output
    assert "subtopic" not in output


def test_renderer_verbose_mode():
    state = StyleInterpreter().load(DATA_DIR / "simple.xdy")
    raw_entries = load_raw_index(DATA_DIR / "simple.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index, MarkupConfig(verbose=True))
    assert "[d=0]" in output


def test_locref_formats_are_attr_specific():
    state = StyleInterpreter().load(DATA_DIR / "markup-locref.xdy")
    raw_entries = load_raw_index(DATA_DIR / "markup-locref.raw")
    index = build_index_entries(raw_entries, state)
    output = render_index(index, style_state=state)
    assert "<1|2" in output
    assert "[3;4" in output
    assert "||" in output
