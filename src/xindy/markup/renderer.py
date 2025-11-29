"""Simple textual renderer for the Python xindy index."""

from __future__ import annotations

from dataclasses import dataclass

from xindy.index.models import Index, IndexNode


@dataclass(slots=True)
class MarkupConfig:
    show_letter_headers: bool = True
    letter_header_template: str = "{label}"
    entry_indent: str = "  "
    locref_prefix: str = ""
    locref_separator: str = ", "
    crossref_prefix: str = "see "
    crossref_separator: str = ", "
    crossref_label_template: str | None = None


def render_index(index: Index, config: MarkupConfig | None = None) -> str:
    cfg = config or MarkupConfig()
    lines: list[str] = []
    for group in index.groups:
        if cfg.show_letter_headers:
            lines.append(cfg.letter_header_template.format(label=group.label.upper()))
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
    if node.locrefs:
        locref_body = cfg.locref_separator.join(
            ref.locref_string for ref in node.locrefs
        )
        locref_part = f" {cfg.locref_prefix}{locref_body}"
    lines.append(base + locref_part)
    for crossref in node.crossrefs:
        refs = cfg.crossref_separator.join(crossref.target)
        label = cfg.crossref_prefix
        if cfg.crossref_label_template:
            label = cfg.crossref_label_template.format(target=refs)
        lines.append(f"{indent}{label}{refs}")
    for child in node.children:
        _render_node(child, lines, cfg, depth + 1)


__all__ = ["MarkupConfig", "render_index"]
