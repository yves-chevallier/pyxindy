"""Bridge between raw entries and structured index data."""

from __future__ import annotations

from typing import Iterable

from xindy.dsl.interpreter import StyleState
from xindy.locref import (
    CategoryAttribute,
    LayeredLocationClass,
    build_location_reference,
    make_category_attribute,
)
from xindy.raw.reader import RawIndexEntry

from .grouping import group_entries_by_letter
from .models import Index, IndexEntry


class IndexBuilderError(RuntimeError):
    """Raised when raw entries cannot be mapped to style constructs."""


def build_index_entries(
    raw_entries: Iterable[RawIndexEntry],
    style_state: StyleState,
    *,
    default_locclass: str | None = None,
) -> Index:
    """Convert raw entries into structured :class:`IndexEntry` objects."""
    locclass = _resolve_location_class(style_state, default_locclass)
    entries: list[IndexEntry] = []
    for raw in raw_entries:
        attr_name, catattr = _resolve_attribute(style_state, raw.attr)
        if catattr is None:
            raise IndexBuilderError("No category attribute available for entry")
        locref = build_location_reference(locclass, raw.locref, catattr, attr_name)
        if not locref:
            raise IndexBuilderError(
                f"Could not build location reference for {raw.locref!r}"
            )
        entry = IndexEntry(
            key=raw.key,
            attribute=attr_name,
        )
        entry.add_location_reference(locref)
        entries.append(entry)
    grouped = group_entries_by_letter(entries, style_state)
    return Index(groups=grouped, total_entries=len(entries))


def _resolve_location_class(
    style_state: StyleState,
    provided: str | None,
) -> LayeredLocationClass:
    if provided:
        loccls = style_state.location_classes.get(provided)
        if not loccls:
            raise IndexBuilderError(f"Unknown location class {provided!r}")
        return loccls
    if not style_state.location_classes:
        raise IndexBuilderError("No location classes defined in style")
    # dict preserves insertion order -> first defined class becomes default
    return next(iter(style_state.location_classes.values()))


def _resolve_attribute(
    style_state: StyleState,
    attribute_name: str | None,
) -> tuple[str | None, CategoryAttribute | None]:
    name = attribute_name
    if name is None:
        name = _default_attribute_name(style_state)
    if name is None:
        return None, None
    catattr = style_state.attributes.get(name)
    if catattr is None:
        catattr = make_category_attribute(name)
        style_state.attributes[name] = catattr
    return name, catattr


def _default_attribute_name(state: StyleState) -> str | None:
    if "default" in state.attributes:
        return "default"
    if state.attributes:
        return next(iter(state.attributes))
    return None


__all__ = ["IndexBuilderError", "build_index_entries"]
