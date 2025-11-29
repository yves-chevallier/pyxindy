"""Data structures describing processed index entries."""

from __future__ import annotations

from dataclasses import dataclass, field

from xindy.locref import LayeredLocationReference


@dataclass(slots=True)
class IndexEntry:
    """Represents a single index entry after applying style semantics."""

    key: tuple[str, ...]
    attribute: str | None
    locrefs: list[LayeredLocationReference] = field(default_factory=list)

    def add_location_reference(self, locref: LayeredLocationReference) -> None:
        self.locrefs.append(locref)


__all__ = ["IndexEntry"]
