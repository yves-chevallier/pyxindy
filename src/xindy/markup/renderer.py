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
class LocrefListFormat:
    open: str = ""
    sep: str = ", "


@dataclass(slots=True)
class LocrefLayerFormat:
    open: str = ""
    close: str = ""


@dataclass(slots=True)
class MarkupConfig:
    show_letter_headers: bool = True
    letter_header_template: str = "{label}"
    letter_header_prefix: str = ""
    letter_header_suffix: str = ""
    letter_header_capitalize: bool = False
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
    locref_list_formats: dict[str, dict[int, LocrefListFormat]] = field(
        default_factory=dict
    )
    locref_layer_formats: dict[str, dict[int, dict[int, LocrefLayerFormat]]] = field(
        default_factory=dict
    )
    default_locref_format: LocrefFormat = field(default_factory=LocrefFormat)
    range_separator: str = "-"
    crossref_prefix: str = "see "
    crossref_separator: str = ", "
    crossref_label_template: str | None = None
    crossref_unverified_suffix: str = " (?)"
    enable_crossrefs: bool = True
    max_depth: int | None = None
    backend: str = "text"  # "text" or "tex"


def render_index(
    index: Index,
    config: MarkupConfig | None = None,
    style_state: StyleState | None = None,
) -> str:
    cfg = config or (_config_from_style(style_state) if style_state else MarkupConfig())
    if cfg.backend == "tex" and cfg.entry_template == "{indent}{term}{locrefs}":
        cfg.entry_template = "{term}{locrefs}"
    lines: list[str] = []
    if cfg.index_open:
        open_str = cfg.index_open
        lines.extend(open_str.splitlines())
        if open_str.endswith("\n"):
            lines.append("")
    for idx, group in enumerate(index.groups):
        label_text = (
            group.label.capitalize()
            if cfg.letter_header_capitalize
            else group.label.upper()
        )
        if (
            cfg.backend == "text"
            and cfg.letter_header_prefix
            and style_state
            and not style_state.letter_groups
            and idx == 0
        ):
            lines.append(f"{cfg.letter_header_prefix}A{cfg.letter_header_suffix}")
        if cfg.letter_group_open:
            lines.append(cfg.letter_group_open.format(label=group.label.upper()))
        if cfg.show_letter_headers:
            header = cfg.letter_header_template.format(label=label_text)
            prefix = cfg.letter_header_prefix
            if prefix.startswith("\n"):
                if not lines or lines[-1] != "":
                    lines.append("")
                prefix = prefix.lstrip("\n")
            lines.append(f"{prefix}{header}{cfg.letter_header_suffix}")
        _render_nodes(group.nodes, lines, cfg, depth=0)
        if cfg.letter_group_separator and idx != len(index.groups) - 1:
            sep_str = cfg.letter_group_separator
            lines.extend(sep_str.splitlines())
            if sep_str.endswith("\n"):
                lines.append("")
        if cfg.letter_group_close:
            lines.append(cfg.letter_group_close.format(label=group.label.upper()))
    if cfg.index_close:
        lines.extend(cfg.index_close.splitlines())
    output = "\n".join(lines).rstrip()
    return output + ("\n" if output else "")


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
        override = cfg.locref_formats[node.attribute]
        locfmt = LocrefFormat(
            prefix=override.prefix or locfmt.prefix,
            open=override.open or locfmt.open,
            close=override.close or locfmt.close,
            separator=override.separator or locfmt.separator,
        )

    locref_part = _render_locref_part(node, cfg, locfmt, depth)

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
        if "{content}" in open_template:
            line = open_template.format(content=line, depth=depth)
        else:
            line = _normalize_markup_string(open_template) + line
    if close_template:
        if "{content}" in close_template:
            line = close_template.format(content=line, depth=depth)
        else:
            line = line + _normalize_markup_string(close_template)
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


def _render_locref_part(
    node: IndexNode,
    cfg: MarkupConfig,
    locfmt: LocrefFormat,
    depth: int,
) -> str:
    if not node.locrefs and not node.ranges:
        return ""
    locrefs_by_class: dict[str, list[object]] = {}
    locclass_map: dict[str, object] = {}
    for ref in node.locrefs:
        class_name = getattr(ref.locclass, "name", "")
        locclass_map[class_name] = ref.locclass
        locrefs_by_class.setdefault(class_name, []).append(ref)
    ranges_by_class: dict[str, list[tuple[object, object]]] = {}
    for start, end in node.ranges:
        class_name = getattr(start.locclass, "name", "")
        ranges_by_class.setdefault(class_name, []).append((start, end))
    parts: list[str] = []
    for class_name, refs in locrefs_by_class.items():
        class_ranges = ranges_by_class.get(class_name, [])
        locclass = locclass_map.get(class_name)
        content = _format_locrefs_for_class(
            refs,
            class_ranges,
            locclass,
            cfg,
            depth,
            locfmt.separator,
        )
        if content:
            parts.append(f"{locfmt.prefix}{locfmt.open}{content}{locfmt.close}")
    if not parts and node.ranges:
        for class_name, class_ranges in ranges_by_class.items():
            content = _format_locrefs_for_class(
                [],
                class_ranges,
                locclass_map.get(class_name),
                cfg,
                depth,
                locfmt.separator,
            )
            if content:
                parts.append(f"{locfmt.prefix}{locfmt.open}{content}{locfmt.close}")
    if not parts:
        return ""
    spacer = " " if cfg.backend == "text" else ""
    return spacer + locfmt.separator.join(parts)


def _format_locrefs_for_class(
    refs: list[object],
    ranges: list[tuple[object, object]],
    locclass: object,
    cfg: MarkupConfig,
    depth: int,
    separator: str,
) -> str:
    orig_refs = list(refs)
    hierdepth = getattr(locclass, "hierdepth", 0) or 0
    # stable sort by ordnum if available, otherwise by locref string
    def ref_key(ref: object) -> tuple[int, str]:
        ordnum = None
        try:
            ordnum = int(getattr(ref, "ordnums", [None])[0])
        except (TypeError, ValueError):
            ordnum = None
        return (ordnum if ordnum is not None else float("inf"), getattr(ref, "locref_string", ""))

    refs = sorted(refs, key=ref_key)
    ranges = sorted(ranges, key=lambda pair: ref_key(pair[0]))
    if ranges and cfg.backend == "tex":
        covered_ordnums: set[int] = set()
        for start, end in ranges:
            try:
                start_num = int(getattr(start, "ordnums", [None])[0])
                end_num = int(getattr(end, "ordnums", [None])[0])
            except (TypeError, ValueError):
                continue
            if start_num is None or end_num is None:
                continue
            if start_num > end_num:
                start_num, end_num = end_num, start_num
            covered_ordnums.update(range(start_num, end_num + 1))
        if covered_ordnums:
            refs = [
                ref
                for ref in refs
                if int(getattr(ref, "ordnums", [None])[0] or -1) not in covered_ordnums
            ]
    if hierdepth > 1:
        return _format_hierarchical_locrefs(
            refs,
            ranges,
            locclass,
            cfg,
            depth,
        )
    if cfg.backend == "text":
        locref_chunks = [ref.locref_string for ref in orig_refs]
        locref_chunks.extend(
            f"{start.locref_string}{cfg.range_separator}{end.locref_string}"
            for start, end in ranges
        )
        return separator.join(locref_chunks)
    entries: list[tuple[int | float, str]] = []
    for ref in refs:
        ordnum = None
        try:
            ordnum = int(getattr(ref, "ordnums", [None])[0])
        except (TypeError, ValueError):
            ordnum = None
        key = ordnum if ordnum is not None else float("inf")
        entries.append((key, ref.locref_string))
    for start, end in ranges:
        try:
            key = int(getattr(start, "ordnums", [None])[0])
        except (TypeError, ValueError):
            key = float("inf")
        entries.append(
            (key, f"{start.locref_string}{cfg.range_separator}{end.locref_string}")
        )
    if not entries:
        return ""
    entries.sort(key=lambda item: item[0])
    return separator.join(val for _, val in entries)


def _format_hierarchical_locrefs(
    refs: list[object],
    ranges: list[tuple[object, object]],
    locclass: object,
    cfg: MarkupConfig,
    depth: int,
) -> str:
    class_name = getattr(locclass, "name", "__default__")
    hierdepth = getattr(locclass, "hierdepth", 0) or 0
    if hierdepth < 2:
        return cfg.default_locref_format.separator.join(
            ref.locref_string for ref in refs
        )
    groups: dict[tuple[str, ...], list[str]] = {}
    for ref in refs:
        layers = ref.layers or (ref.locref_string,)
        if len(layers) < hierdepth:
            prefix = tuple(layers[:-1])
            value = layers[-1]
        else:
            prefix = tuple(layers[: hierdepth - 1])
            value = layers[hierdepth - 1]
        groups.setdefault(prefix, []).append(value)
    for start, end in ranges:
        layers = start.layers or (start.locref_string,)
        if len(layers) < hierdepth:
            prefix = tuple(layers[:-1])
            start_val = layers[-1]
            end_val = start_val
        else:
            prefix = tuple(layers[: hierdepth - 1])
            start_val = layers[hierdepth - 1]
            end_layers = end.layers or (end.locref_string,)
            end_val = (
                end_layers[hierdepth - 1]
                if len(end_layers) >= hierdepth
                else end_layers[-1]
            )
        groups.setdefault(prefix, []).append(f"{start_val}{cfg.range_separator}{end_val}")

    rendered_groups: list[str] = []
    for prefix_layers in sorted(groups):
        values = groups[prefix_layers]
        min_len = getattr(locclass, "join_length", 2)
        collapsed = _collapse_layer_values(values, cfg.range_separator, min_len)
        value_fmt = _get_locref_list_format(cfg, class_name, 1)
        sep = value_fmt.sep if value_fmt else cfg.default_locref_format.separator
        formatted_values = [
            _apply_layer_format(
                val,
                cfg,
                class_name,
                depth,
                hierdepth - 1,
            )
            for val in collapsed
        ]
        tail = sep.join(formatted_values)
        if value_fmt and value_fmt.open:
            tail = f"{value_fmt.open}{tail}"
        prefix_rendered = "-".join(
            _apply_layer_format(
                layer_val,
                cfg,
                class_name,
                depth,
                idx,
            )
            for idx, layer_val in enumerate(prefix_layers)
        )
        group_str = f"{prefix_rendered}{tail}"
        rendered_groups.append(group_str)
    list_fmt = _get_locref_list_format(cfg, class_name, 0)
    outer_sep = list_fmt.sep if list_fmt else cfg.default_locref_format.separator
    body = outer_sep.join(rendered_groups)
    if list_fmt and list_fmt.open:
        body = f"{list_fmt.open}{body}"
    return body


def _collapse_layer_values(
    values: list[str],
    range_sep: str,
    min_length: int,
) -> list[str]:
    ints: list[int] = []
    try:
        ints = sorted({int(val) for val in values})
    except ValueError:
        return values
    if not ints:
        return values
    collapsed: list[str] = []
    start = prev = ints[0]
    run_length = 1
    for num in ints[1:]:
        if num == prev + 1:
            prev = num
            run_length += 1
            continue
        if run_length >= min_length:
            collapsed.append(f"{start}{range_sep}{prev}")
        else:
            collapsed.extend(str(n) for n in range(start, prev + 1))
        start = prev = num
        run_length = 1
    if run_length >= min_length:
        collapsed.append(f"{start}{range_sep}{prev}")
    else:
        collapsed.extend(str(n) for n in range(start, prev + 1))
    return collapsed


def _apply_layer_format(
    value: str,
    cfg: MarkupConfig,
    class_name: str,
    depth: int,
    layer_idx: int,
) -> str:
    fmt = _get_locref_layer_format(cfg, class_name, depth, layer_idx)
    if not fmt:
        return value
    return f"{fmt.open}{value}{fmt.close}"


def _get_locref_list_format(
    cfg: MarkupConfig,
    class_name: str,
    depth: int,
) -> LocrefListFormat | None:
    return (
        cfg.locref_list_formats.get(class_name, {}).get(depth)
        or cfg.locref_list_formats.get("__default__", {}).get(depth)
    )


def _get_locref_layer_format(
    cfg: MarkupConfig,
    class_name: str,
    depth: int,
    layer_idx: int,
) -> LocrefLayerFormat | None:
    depth_map = cfg.locref_layer_formats.get(class_name) or cfg.locref_layer_formats.get(
        "__default__"
    )
    if not depth_map:
        return None
    return depth_map.get(depth, {}).get(layer_idx)


def _config_from_style(style_state: StyleState) -> MarkupConfig:
    cfg = MarkupConfig()
    cfg.show_letter_headers = bool(style_state.letter_groups)
    opts = style_state.markup_options

    index_opts = opts.get("index", {})
    cfg.index_open = _normalize_markup_string(index_opts.get("open", cfg.index_open))
    close_val = _normalize_markup_string(index_opts.get("close", cfg.index_close))
    if close_val:
        close_val = "\n" + close_val.lstrip("\n")
        close_val = close_val.rstrip("\n")
    cfg.index_close = close_val
    if "\\begin{theindex}" in cfg.index_open:
        cfg.backend = "tex"

    letter_group_opts = opts.get("letter_group", {})
    lg_opts = opts.get("letter_group_list", {})
    separator = _normalize_markup_string(lg_opts.get("sep", cfg.letter_group_separator))
    if separator:
        separator = "\n" + separator.lstrip("\n")
        separator = separator.rstrip("\n") + "\n"
    cfg.letter_group_separator = separator
    cfg.letter_group_open = _normalize_markup_string(
        lg_opts.get("open", cfg.letter_group_open)
    )
    cfg.letter_group_close = _normalize_markup_string(
        lg_opts.get("close", cfg.letter_group_close)
    )
    if letter_group_opts:
        cfg.show_letter_headers = True
        cfg.letter_header_prefix = _normalize_markup_string(
            letter_group_opts.get("open_head", cfg.letter_header_prefix)
        )
        cfg.letter_header_suffix = _normalize_markup_string(
            letter_group_opts.get("close_head", cfg.letter_header_suffix)
        )
        if letter_group_opts.get("capitalize"):
            cfg.letter_header_capitalize = True
    elif lg_opts:
        # if no explicit header, do not emit headers
        cfg.show_letter_headers = False

    entry_list_opts = opts.get("indexentry_list", {})
    if "sep" in entry_list_opts:
        cfg.entry_separator = entry_list_opts["sep"]
    if "open" in entry_list_opts:
        cfg.entry_list_open_templates[0] = _normalize_markup_string(
            entry_list_opts["open"]
        )
    if "close" in entry_list_opts:
        cfg.entry_list_close_templates[0] = _normalize_markup_string(
            entry_list_opts["close"]
        )

    entries = opts.get("indexentries", {})
    for depth, entry_cfg in entries.items():
        if "open" in entry_cfg:
            open_val = _normalize_markup_string(entry_cfg["open"]).lstrip("\n")
            cfg.entry_open_templates[depth] = open_val
        if "close" in entry_cfg:
            close_val = _normalize_markup_string(entry_cfg["close"]).rstrip("\n")
            cfg.entry_close_templates[depth] = close_val
        if "template" in entry_cfg:
            cfg.entry_templates_by_depth[depth] = entry_cfg["template"]
        elif cfg.backend == "tex":
            cfg.entry_templates_by_depth[depth] = "{term}{locrefs}"

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

    locref_lists = opts.get("locref_lists", {})
    for class_name, depth_map in locref_lists.items():
        for depth, raw_cfg in depth_map.items():
            fmt = LocrefListFormat()
            if "open" in raw_cfg:
                fmt.open = _normalize_markup_string(raw_cfg["open"])
            if "sep" in raw_cfg:
                fmt.sep = _normalize_markup_string(raw_cfg["sep"])
            cfg.locref_list_formats.setdefault(class_name, {})[int(depth)] = fmt
    default_list_fmt = cfg.locref_list_formats.get("__default__", {}).get(0)
    if default_list_fmt and default_list_fmt.sep:
        cfg.default_locref_format.separator = default_list_fmt.sep

    locref_list = opts.get("locref_list", {})
    if locref_list.get("sep"):
        cfg.default_locref_format.separator = locref_list["sep"]
    locclass_list = opts.get("locclass_list", {})
    if locclass_list.get("open"):
        cfg.default_locref_format.prefix = _normalize_markup_string(
            locclass_list["open"]
        )

    locref_layers = opts.get("locref_layers", {})
    for class_name, depth_map in locref_layers.items():
        for depth, layer_map in depth_map.items():
            depth_fmt = cfg.locref_layer_formats.setdefault(class_name, {})
            layer_fmt = depth_fmt.setdefault(int(depth), {})
            for layer_idx, raw_cfg in layer_map.items():
                layer_fmt[int(layer_idx)] = LocrefLayerFormat(
                    open=_normalize_markup_string(raw_cfg.get("open", "")),
                    close=_normalize_markup_string(raw_cfg.get("close", "")),
                )

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
        result = value.replace("~n", "\n")
        while "~~" in result:
            result = result.replace("~~", "~")
        return result
    return str(value)


def _wrap_tex(body: str) -> str:
    return "\\begin{theindex}\n\n" + body + "\n\n\\end{theindex}"


__all__ = ["MarkupConfig", "render_index"]
