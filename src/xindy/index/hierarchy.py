"""Utilities to build hierarchical index nodes from flat entries."""

from __future__ import annotations

from typing import Iterable, List

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
            node.extend_locrefs(entry.locrefs)
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


__all__ = ["build_hierarchy"]
