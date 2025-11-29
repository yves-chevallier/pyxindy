"""Letter grouping utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from xindy.dsl.interpreter import StyleState

from .models import IndexEntry
from .order import sort_entries


@dataclass(slots=True)
class LetterGroup:
    label: str
    entries: list[IndexEntry] = field(default_factory=list)


def group_entries_by_letter(
    entries: Iterable[IndexEntry],
    style_state: StyleState,
) -> list[LetterGroup]:
    sorted_entries = sort_entries(entries)
    groups = _resolve_letter_groups(style_state)
    buckets: dict[str, LetterGroup] = {label: LetterGroup(label) for label in groups}
    fallback = buckets[groups[0]] if groups else LetterGroup("#")
    for entry in sorted_entries:
        label = _letter_label_for_entry(entry, groups)
        target = buckets.get(label, fallback)
        target.entries.append(entry)
    return [group for group in buckets.values() if group.entries]


def _resolve_letter_groups(state: StyleState) -> list[str]:
    if state.letter_groups:
        return state.letter_groups
    # fallback to base alphabet of first basetype
    if state.basetypes:
        first = next(iter(state.basetypes.values()))
        return list(first.base_alphabet)
    return []


def _letter_label_for_entry(entry: IndexEntry, groups: Sequence[str]) -> str:
    first_char = entry.key[0][0].lower()
    for label in groups:
        if label.startswith(first_char):
            return label
    return groups[0] if groups else "#"


__all__ = ["LetterGroup", "group_entries_by_letter"]
