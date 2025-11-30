"""Sorting and grouping helpers for index entries."""

from __future__ import annotations

import re
from typing import Iterable

from xindy.dsl.interpreter import StyleState

from .models import IndexEntry


def apply_sort_rules(text: str, style_state: StyleState) -> str:
    result = text
    for pattern, replacement, repeat in style_state.sort_rules:
        if not repeat:
            result = re.sub(pattern, replacement, result)
            continue
        while True:
            updated = re.sub(pattern, replacement, result)
            if updated == result:
                break
            result = updated
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
