"""Simple textual renderer for the Python xindy index."""

from __future__ import annotations

from dataclasses import dataclass, field

from xindy.index.models import Index, IndexNode


@dataclass(slots=True)
class MarkupConfig:
    show_letter_headers: bool = True
    letter_header_template: str = "{label}"
    letter_header_prefix: str = ""
    letter_header_suffix: str = ""
    entry_indent: str = "  "
    entry_open_templates: dict[int, str] = field(default_factory=dict)
    entry_close_templates: dict[int, str] = field(default_factory=dict)
    locref_prefix: str = ""
    locref_open: str = ""
    locref_close: str = ""
    locref_separator: str = ", "
    range_separator: str = "-"
    crossref_prefix: str = "see "
    crossref_separator: str = ", "
    crossref_label_template: str | None = None
    enable_crossrefs: bool = True


def render_index(index: Index, config: MarkupConfig | None = None) -> str:
    cfg = config or MarkupConfig()
    lines: list[str] = []
    for group in index.groups:
        if cfg.show_letter_headers:
            header = cfg.letter_header_template.format(label=group.label.upper())
            lines.append(f"{cfg.letter_header_prefix}{header}{cfg.letter_header_suffix}")
        for node in group.nodes:
            _render_node(node, lines, cfg, depth=0)
    return "\n".join(lines).rstrip() + ("\n" if lines else "")


def _render_node(
    node: IndexNode,
    lines: list[str],
    cfg: MarkupConfig,
    depth: int,
) -> None:
    indent = cfg.entry_indent * depth
    base = f"{indent}{node.term}"
    locref_part = ""
    locref_chunks = []
    if node.locrefs:
        locref_chunks.extend(ref.locref_string for ref in node.locrefs)
    if node.ranges:
        locref_chunks.extend(
            f"{start.locref_string}{cfg.range_separator}{end.locref_string}"
            for start, end in node.ranges
        )
    if locref_chunks:
        locref_body = cfg.locref_separator.join(locref_chunks)
        locref_part = (
            f" {cfg.locref_prefix}{cfg.locref_open}"
            f"{locref_body}{cfg.locref_close}"
        )
    line = base + locref_part
    open_template = cfg.entry_open_templates.get(depth)
    close_template = cfg.entry_close_templates.get(depth)
    if open_template:
        line = open_template.format(content=line, depth=depth)
    if close_template:
        line = line + close_template.format(depth=depth)
    lines.append(line)
    if cfg.enable_crossrefs:
        for crossref in node.crossrefs:
            refs = cfg.crossref_separator.join(crossref.target)
            label = cfg.crossref_prefix
            if cfg.crossref_label_template:
                label = cfg.crossref_label_template.format(target=refs)
            lines.append(f"{indent}{label}{refs}")
    for child in node.children:
        _render_node(child, lines, cfg, depth + 1)


__all__ = ["MarkupConfig", "render_index"]
