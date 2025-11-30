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
    locclasses = _resolve_location_classes(style_state, default_locclass)
    entries: list[IndexEntry] = []
    for raw in raw_entries:
        attr_token, dropped = _apply_merge_rules(raw.attr, style_state)
        if dropped:
            continue
        attr_name, catattr = _resolve_attribute(style_state, attr_token)
        if catattr is None:
            raise IndexBuilderError("No category attribute available for entry")
        xref_target = _parse_xref_target(raw.extras.get("xref"))
        locrefs = []
        if xref_target is None:
            if raw.locref is None:
                raise IndexBuilderError("Missing :locref for non-crossref entry")
            locref = None
            for loccls in locclasses:
                locref = build_location_reference(
                    loccls, raw.locref, catattr, attr_name
                )
                if locref:
                    break
            if locref:
                locrefs.append(locref)
            else:
                raise IndexBuilderError(
                    f"Could not build location reference for {raw.locref!r}"
                )
        entry = IndexEntry(
            key=raw.key,
            attribute=attr_name,
            xref_target=xref_target,
        )
        for locref in locrefs:
            entry.add_location_reference(locref)
        entries.append(entry)
    grouped = group_entries_by_letter(entries, style_state)
    progress = _compute_progress_markers(len(entries))
    return Index(groups=grouped, total_entries=len(entries), progress_markers=progress)


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


def _resolve_location_classes(
    style_state: StyleState,
    provided: str | None,
) -> list[LayeredLocationClass]:
    if provided:
        return [_resolve_location_class(style_state, provided)]
    return list(style_state.location_classes.values())


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


def _apply_merge_rules(
    attr_name: str | None,
    style_state: StyleState,
) -> tuple[str | None, bool]:
    if attr_name is None:
        return None, False
    current = attr_name
    for source, target, drop in style_state.merge_rules:
        if current == source:
            if drop:
                return None, True
            current = target
    return current, False


def _parse_xref_target(value: object | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, list):
        if not value:
            return None
        return tuple(str(item) for item in value)
    if isinstance(value, str):
        return (value,)
    raise IndexBuilderError("Unsupported xref format")


def _compute_progress_markers(total_entries: int) -> list[int]:
    if total_entries == 0:
        return []
    markers = []
    for percent in range(10, 110, 10):
        markers.append(max(1, int(total_entries * (percent / 100))))
    return markers


__all__ = ["IndexBuilderError", "build_index_entries"]
