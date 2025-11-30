"""Simple textual renderer for the Python xindy index."""

from __future__ import annotations

from dataclasses import dataclass, field

from xindy.dsl.interpreter import StyleState
from xindy.index.models import Index, IndexNode


@dataclass(slots=True)
class LocrefFormat:
    prefix: str = ""
    open: str = ""
    close: str = ""
    separator: str = ", "


@dataclass(slots=True)
class MarkupConfig:
    show_letter_headers: bool = True
    letter_header_template: str = "{label}"
    letter_header_prefix: str = ""
    letter_header_suffix: str = ""
    index_open: str = ""
    index_close: str = ""
    letter_group_open: str = ""
    letter_group_close: str = ""
    letter_group_separator: str = ""
    entry_indent: str = "  "
    entry_template: str = "{indent}{term}{locrefs}"
    entry_templates_by_depth: dict[int, str] = field(default_factory=dict)
    entry_list_open_templates: dict[int, str] = field(default_factory=dict)
    entry_list_close_templates: dict[int, str] = field(default_factory=dict)
    entry_open_templates: dict[int, str] = field(default_factory=dict)
    entry_close_templates: dict[int, str] = field(default_factory=dict)
    entry_separator: str = ""
    verbose: bool = False
    locref_formats: dict[str, LocrefFormat] = field(default_factory=dict)
    default_locref_format: LocrefFormat = field(default_factory=LocrefFormat)
    range_separator: str = "-"
    crossref_prefix: str = "see "
    crossref_separator: str = ", "
    crossref_label_template: str | None = None
    crossref_unverified_suffix: str = " (?)"
    enable_crossrefs: bool = True
    max_depth: int | None = None


def render_index(
    index: Index,
    config: MarkupConfig | None = None,
    style_state: StyleState | None = None,
) -> str:
    cfg = config or (_config_from_style(style_state) if style_state else MarkupConfig())
    lines: list[str] = []
    if cfg.index_open:
        lines.append(cfg.index_open)
    for idx, group in enumerate(index.groups):
        if cfg.letter_group_open:
            lines.append(cfg.letter_group_open.format(label=group.label.upper()))
        if cfg.show_letter_headers:
            header = cfg.letter_header_template.format(label=group.label.upper())
            lines.append(f"{cfg.letter_header_prefix}{header}{cfg.letter_header_suffix}")
        _render_nodes(group.nodes, lines, cfg, depth=0)
        if cfg.letter_group_separator and idx != len(index.groups) - 1:
            lines.append(cfg.letter_group_separator)
        if cfg.letter_group_close:
            lines.append(cfg.letter_group_close.format(label=group.label.upper()))
    if cfg.index_close:
        lines.append(cfg.index_close)
    return "\n".join(lines).rstrip() + ("\n" if lines else "")


def _render_node(
    node: IndexNode,
    lines: list[str],
    cfg: MarkupConfig,
    depth: int,
) -> None:
    indent = cfg.entry_indent * depth
    # choose locref format based on attribute (fallback to default)
    locfmt = cfg.default_locref_format
    if node.attribute and node.attribute in cfg.locref_formats:
        locfmt = cfg.locref_formats[node.attribute]

    locref_chunks = []
    if node.locrefs:
        locref_chunks.extend(ref.locref_string for ref in node.locrefs)
    if node.ranges:
        locref_chunks.extend(
            f"{start.locref_string}{cfg.range_separator}{end.locref_string}"
            for start, end in node.ranges
        )
    locref_part = ""
    if locref_chunks:
        locref_body = locfmt.separator.join(locref_chunks)
        locref_part = (
            f" {locfmt.prefix}{locfmt.open}"
            f"{locref_body}{locfmt.close}"
        )

    template = cfg.entry_templates_by_depth.get(depth, cfg.entry_template)
    line = template.format(
        indent=indent,
        term=node.term,
        locrefs=locref_part,
        depth=depth,
    )
    open_template = cfg.entry_open_templates.get(depth)
    close_template = cfg.entry_close_templates.get(depth)
    if open_template:
        line = open_template.format(content=line, depth=depth)
    if close_template:
        line = line + close_template.format(depth=depth)
    if cfg.verbose:
        line = f"[d={depth}] {line}"
    lines.append(line)
    if cfg.enable_crossrefs:
        for crossref in node.crossrefs:
            refs = cfg.crossref_separator.join(crossref.target)
            label = cfg.crossref_prefix
            if cfg.crossref_label_template:
                label = cfg.crossref_label_template.format(target=refs)
            suffix = ""
            if crossref.attribute and crossref.attribute.lower() == "unverified":
                suffix = cfg.crossref_unverified_suffix
            lines.append(f"{indent}{label}{refs}{suffix}")
    next_depth = depth + 1
    if cfg.max_depth is not None and next_depth > cfg.max_depth:
        return
    _render_nodes(node.children, lines, cfg, depth=next_depth)


def _render_nodes(
    nodes: list[IndexNode],
    lines: list[str],
    cfg: MarkupConfig,
    depth: int,
) -> None:
    if not nodes:
        return
    open_template = cfg.entry_list_open_templates.get(depth)
    if open_template:
        lines.append(open_template.format(depth=depth))
    for n_idx, node in enumerate(nodes):
        _render_node(node, lines, cfg, depth=depth)
        if cfg.entry_separator and n_idx != len(nodes) - 1:
            lines.append(cfg.entry_separator)
    close_template = cfg.entry_list_close_templates.get(depth)
    if close_template:
        lines.append(close_template.format(depth=depth))


def _config_from_style(style_state: StyleState) -> MarkupConfig:
    cfg = MarkupConfig()
    opts = style_state.markup_options

    index_opts = opts.get("index", {})
    cfg.index_open = _normalize_markup_string(index_opts.get("open", cfg.index_open))
    cfg.index_close = _normalize_markup_string(index_opts.get("close", cfg.index_close))

    lg_opts = opts.get("letter_group_list", {})
    cfg.letter_group_separator = lg_opts.get("sep", cfg.letter_group_separator)
    cfg.letter_group_open = _normalize_markup_string(
        lg_opts.get("open", cfg.letter_group_open)
    )
    cfg.letter_group_close = _normalize_markup_string(
        lg_opts.get("close", cfg.letter_group_close)
    )
    if lg_opts:
        # if no explicit header, do not emit headers
        cfg.show_letter_headers = False

    entry_list_opts = opts.get("indexentry_list", {})
    if "sep" in entry_list_opts:
        cfg.entry_separator = entry_list_opts["sep"]
    if "open" in entry_list_opts:
        cfg.entry_list_open_templates[0] = entry_list_opts["open"]
    if "close" in entry_list_opts:
        cfg.entry_list_close_templates[0] = entry_list_opts["close"]

    entries = opts.get("indexentries", {})
    for depth, entry_cfg in entries.items():
        if "open" in entry_cfg:
            cfg.entry_open_templates[depth] = _normalize_markup_string(
                entry_cfg["open"]
            )
        if "close" in entry_cfg:
            cfg.entry_close_templates[depth] = _normalize_markup_string(
                entry_cfg["close"]
            )
        if "template" in entry_cfg:
            cfg.entry_templates_by_depth[depth] = entry_cfg["template"]

    locref_opts = opts.get("locref", {})
    default_locref = locref_opts.get("__default__", {})
    cfg.default_locref_format = _update_locfmt(
        cfg.default_locref_format,
        default_locref,
    )
    for attr, raw_cfg in locref_opts.items():
        if attr == "__default__":
            continue
        cfg.locref_formats[attr] = _update_locfmt(LocrefFormat(), raw_cfg)

    locref_list = opts.get("locref_list", {})
    if locref_list.get("sep"):
        cfg.default_locref_format.separator = locref_list["sep"]
    locclass_list = opts.get("locclass_list", {})
    if locclass_list.get("open"):
        cfg.default_locref_format.prefix = _normalize_markup_string(locclass_list["open"])

    crossref_opts = opts.get("crossref_list", {})
    if "open" in crossref_opts:
        cfg.crossref_prefix = crossref_opts["open"]
    if "sep" in crossref_opts:
        cfg.crossref_separator = crossref_opts["sep"]

    range_opts = opts.get("range", {})
    if "sep" in range_opts:
        cfg.range_separator = range_opts["sep"]

    return cfg


def _update_locfmt(locfmt: LocrefFormat, data: dict[str, object]) -> LocrefFormat:
    if "sep" in data:
        locfmt.separator = data["sep"]
    if "open" in data:
        locfmt.open = data["open"]
    if "close" in data:
        locfmt.close = data["close"]
    if "prefix" in data:
        locfmt.prefix = data["prefix"]
    return locfmt


def _normalize_markup_string(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.replace("~n", "\n")
    return str(value)


__all__ = ["MarkupConfig", "render_index"]
