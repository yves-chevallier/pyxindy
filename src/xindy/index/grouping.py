"""Letter grouping utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from xindy.dsl.interpreter import StyleState

from .hierarchy import build_hierarchy
from .models import IndexEntry, IndexNode
from .order import sort_entries


@dataclass(slots=True)
class LetterGroup:
    label: str
    nodes: list[IndexNode] = field(default_factory=list)


def group_entries_by_letter(
    entries: Iterable[IndexEntry],
    style_state: StyleState,
) -> list[LetterGroup]:
    sorted_entries = sort_entries(entries)
    groups = _resolve_letter_groups(style_state)
    buckets: dict[str, list[IndexEntry]] = {label: [] for label in groups}
    extra_labels: list[str] = []
    fallback_label = groups[0] if groups else "#"
    for entry in sorted_entries:
        label = _letter_label_for_entry(entry, groups)
        if label not in buckets:
            buckets[label] = []
            extra_labels.append(label)
        buckets[label].append(entry)
    result: list[LetterGroup] = []
    ordered_labels = list(groups) + extra_labels
    for label in ordered_labels:
        entries = buckets.get(label, [])
        nodes = build_hierarchy(entries)
        if nodes:
            result.append(LetterGroup(label=label, nodes=nodes))
    if not result and sorted_entries:
        nodes = build_hierarchy(sorted_entries)
        result.append(LetterGroup(label=fallback_label, nodes=nodes))
    return result


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
