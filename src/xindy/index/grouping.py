"""Letter grouping utilities."""

from __future__ import annotations

from typing import Dict, Iterable, Sequence

from xindy.dsl.interpreter import StyleState

from .hierarchy import build_hierarchy
from .models import IndexEntry, IndexLetterGroup
from .order import sort_entries


def group_entries_by_letter(
    entries: Iterable[IndexEntry],
    style_state: StyleState,
) -> list[IndexLetterGroup]:
    sorted_entries = sort_entries(entries, style_state)
    groups = _resolve_letter_groups(style_state)
    buckets: Dict[str, list[IndexEntry]] = {label: [] for label in groups}
    extra_labels: list[str] = []
    fallback_label = groups[0] if groups else "#"
    for entry in sorted_entries:
        label = _letter_label_for_entry(entry, groups)
        if label not in buckets:
            buckets[label] = []
            extra_labels.append(label)
        buckets[label].append(entry)
    result: list[IndexLetterGroup] = []
    ordered_labels = list(groups) + extra_labels
    for label in ordered_labels:
        entries = buckets.get(label, [])
        nodes = build_hierarchy(entries)
        if nodes:
            result.append(
                IndexLetterGroup(
                    label=label,
                    nodes=nodes,
                    entry_count=len(entries),
                )
            )
    if not result and sorted_entries:
        nodes = build_hierarchy(sorted_entries)
        result.append(
            IndexLetterGroup(
                label=fallback_label,
                nodes=nodes,
                entry_count=len(sorted_entries),
            )
        )
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
    text = entry.key[0].lower()
    # prefer longest matching group prefix
    sorted_groups = sorted(groups, key=lambda g: (-len(g), groups.index(g)))
    for label in sorted_groups:
        if text.startswith(label.lower()):
            return label
    return groups[0] if groups else "#"


__all__ = ["group_entries_by_letter"]
