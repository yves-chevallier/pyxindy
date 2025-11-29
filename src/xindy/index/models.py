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


@dataclass(slots=True)
class IndexNode:
    """Node in the hierarchical index tree."""

    term: str
    key: tuple[str, ...]
    attribute: str | None = None
    locrefs: list[LayeredLocationReference] = field(default_factory=list)
    children: list["IndexNode"] = field(default_factory=list)

    def add_child(self, node: "IndexNode") -> None:
        self.children.append(node)

    def extend_locrefs(self, refs: list[LayeredLocationReference]) -> None:
        self.locrefs.extend(refs)


__all__ = ["IndexEntry", "IndexNode"]
