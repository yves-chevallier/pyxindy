"""Utilities to build hierarchical index nodes from flat entries."""

from __future__ import annotations

from typing import Iterable

from xindy.locref import LayeredLocationReference

from .models import IndexEntry, IndexNode


def build_hierarchy(entries: Iterable[IndexEntry]) -> list[IndexNode]:
    roots: list[IndexNode] = []
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
                _detect_numeric_ranges(node)
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


def _detect_numeric_ranges(node: IndexNode) -> None:
    if len(node.locrefs) < 3:
        return
    node.ranges.clear()
    join_length = getattr(node.locrefs[0].locclass, "join_length", 2)

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

    numeric = [(ref, to_ordnum(ref)) for ref in node.locrefs]
    numeric = [(ref, value) for ref, value in numeric if value is not None]
    if len(numeric) < 2:
        return
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


__all__ = ["build_hierarchy"]
