"""Data structures describing processed index entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from xindy.locref import LayeredLocationReference


@dataclass(slots=True)
class IndexEntry:
    """Represents a single index entry after applying style semantics."""

    key: tuple[str, ...]
    attribute: str | None
    locrefs: list[LayeredLocationReference] = field(default_factory=list)

    def add_location_reference(self, locref: LayeredLocationReference) -> None:
        self.locrefs.append(locref)


@dataclass(slots=True)
class IndexNode:
    """Node in the hierarchical index tree."""

    term: str
    key: tuple[str, ...]
    attribute: str | None = None
    locrefs: list[LayeredLocationReference] = field(default_factory=list)
    ranges: list[tuple[LayeredLocationReference, LayeredLocationReference]] = field(
        default_factory=list
    )
    children: list["IndexNode"] = field(default_factory=list)

    def add_child(self, node: "IndexNode") -> None:
        self.children.append(node)

    def extend_locrefs(self, refs: list[LayeredLocationReference]) -> None:
        self.locrefs.extend(refs)

    def add_locrefs(self, refs: Iterable[LayeredLocationReference]) -> bool:
        added = False
        existing = {
            (ref.locref_string, ref.attribute)
            for ref in self.locrefs
        }
        for ref in refs:
            signature = (ref.locref_string, ref.attribute)
            if signature in existing:
                continue
            self.locrefs.append(ref)
            existing.add(signature)
            added = True
        return added


@dataclass(slots=True)
class IndexLetterGroup:
    label: str
    nodes: list[IndexNode]
    entry_count: int


@dataclass(slots=True)
class Index:
    groups: list[IndexLetterGroup]
    total_entries: int


__all__ = ["Index", "IndexEntry", "IndexLetterGroup", "IndexNode"]
