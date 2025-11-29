"""Sorting and grouping helpers for index entries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .models import IndexEntry


@dataclass(slots=True)
class OrientationRule:
    orientation: str = "forward"

    def apply(self, text: str) -> str:
        if self.orientation == "forward":
            return text
        if self.orientation == "backward":
            return text[::-1]
        raise ValueError(f"Unknown orientation {self.orientation!r}")


def sort_entries(
    entries: Iterable[IndexEntry],
    orientations: Sequence[OrientationRule] | None = None,
) -> list[IndexEntry]:
    """Sort entries alphabetically using the provided orientation rules."""
    orientations = orientations or [OrientationRule()]

    def sort_key(entry: IndexEntry) -> tuple[str, ...]:
        key = entry.key
        return tuple(orientations[0].apply(part) for part in key)

    return sorted(entries, key=sort_key)


__all__ = ["OrientationRule", "sort_entries"]
