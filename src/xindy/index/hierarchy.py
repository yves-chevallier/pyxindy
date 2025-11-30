"""Utilities to build hierarchical index nodes from flat entries."""

from __future__ import annotations

from typing import Iterable, Sequence

from xindy.locref import LayeredLocationReference

from .models import IndexEntry, IndexNode


def build_hierarchy(
    entries: Iterable[IndexEntry],
    allowed_range_attrs: Sequence[str] | None = None,
) -> list[IndexNode]:
    roots: list[IndexNode] = []
    range_allowed = set(allowed_range_attrs or [])
    allow_all_ranges = not range_allowed
    for entry in entries:
        if not entry.key:
            continue
        current_level = roots
        prefix: list[str] = []
        node: IndexNode | None = None
        for token in entry.key:
            prefix.append(token)
            node = _find_or_create_node(current_level, token, tuple(prefix))
            current_level = node.children
        if node:
            if entry.attribute and node.attribute is None:
                node.attribute = entry.attribute
            if entry.xref_target:
                node.add_crossref(entry.xref_target, entry.attribute)
                continue
            changed = node.add_locrefs(entry.locrefs)
            if changed:
                _detect_numeric_ranges(node, range_allowed, allow_all_ranges)
    for node in roots:
        _finalize_ranges(node, range_allowed, allow_all_ranges)
    return roots


def _find_or_create_node(
    nodes: list[IndexNode],
    term: str,
    key: tuple[str, ...],
) -> IndexNode:
    for node in nodes:
        if node.term == term:
            return node
    new_node = IndexNode(term=term, key=key)
    nodes.append(new_node)
    return new_node


def _detect_numeric_ranges(
    node: IndexNode,
    allowed_range_attrs: set[str],
    allow_all: bool,
) -> None:
    if len(node.locrefs) < 3:
        return
    node.ranges.clear()

    def to_ordnum(ref: LayeredLocationReference) -> int | None:
        if ref.ordnums:
            try:
                return int(ref.ordnums[0])
            except (TypeError, ValueError):
                pass
        try:
            return int(ref.locref_string)
        except ValueError:
            return None

    grouped: dict[tuple[str | None, str], list[tuple[LayeredLocationReference, int]]] = {}
    class_lookup: dict[tuple[str | None, str], LayeredLocationReference] = {}
    for ref in node.locrefs:
        ordnum = to_ordnum(ref)
        if ordnum is None:
            continue
        key = (ref.attribute, getattr(ref.locclass, "name", ""))
        grouped.setdefault(key, []).append((ref, ordnum))
        class_lookup[key] = ref.locclass

    for key, numeric in grouped.items():
        attr, _ = key
        if len(numeric) < 2:
            continue
        if not allow_all and attr not in allowed_range_attrs:
            continue
        locclass = class_lookup[key]
        join_length = getattr(locclass, "join_length", 2)
        numeric.sort(key=lambda item: item[1])
        start_ref, start_val = numeric[0]
        prev_ref, prev_val = start_ref, start_val
        run_length = 1
        for ref, value in numeric[1:]:
            if value == prev_val + 1:
                prev_ref, prev_val = ref, value
                run_length += 1
                continue
            if run_length >= join_length:
                node.ranges.append((start_ref, prev_ref))
            start_ref, start_val = ref, value
            prev_ref, prev_val = ref, value
            run_length = 1
        if run_length >= join_length:
            node.ranges.append((start_ref, prev_ref))


def _finalize_ranges(
    node: IndexNode,
    allowed_range_attrs: set[str],
    allow_all: bool,
) -> None:
    _detect_numeric_ranges(node, allowed_range_attrs, allow_all)
    for child in node.children:
        _finalize_ranges(child, allowed_range_attrs, allow_all)


__all__ = ["build_hierarchy"]
