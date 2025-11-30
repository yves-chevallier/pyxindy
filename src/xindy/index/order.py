"""Sorting and grouping helpers for index entries."""

from __future__ import annotations

import re
from typing import Iterable

from xindy.dsl.interpreter import StyleState

from .models import IndexEntry


def _apply_run(text: str, rules: list[tuple[str, str, bool]]) -> str:
    result = text
    for pattern, replacement, repeat in rules:
        if not repeat:
            result = re.sub(pattern, replacement, result)
            continue
        while True:
            updated = re.sub(pattern, replacement, result)
            if updated == result:
                break
            result = updated
    return result


def apply_sort_rules(text: str, style_state: StyleState) -> str:
    grouped: dict[int, list[tuple[str, str, bool]]] = {}
    for pattern, replacement, repeat, run_idx in style_state.sort_rules:
        grouped.setdefault(run_idx, []).append((pattern, replacement, repeat))
    result = text
    if not grouped:
        return result
    for run_idx in sorted(grouped):
        orientation = "forward"
        if style_state.sort_rule_orientations:
            try:
                orientation = style_state.sort_rule_orientations[run_idx]
            except IndexError:
                orientation = style_state.sort_rule_orientations[-1]
        working = result[::-1] if orientation == "backward" else result
        working = _apply_run(working, grouped[run_idx])
        result = working[::-1] if orientation == "backward" else working
    return result


def sort_entries(
    entries: Iterable[IndexEntry],
    style_state: StyleState,
) -> list[IndexEntry]:
    """Sort entries alphabetically applying style-defined rules."""

    def sort_key(entry: IndexEntry) -> tuple[str, ...]:
        return tuple(apply_sort_rules(part, style_state) for part in entry.key)

    return sorted(entries, key=sort_key)


__all__ = ["apply_sort_rules", "sort_entries"]
