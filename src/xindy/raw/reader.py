"""Facilities to parse xindy .raw files into Python data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Mapping

from xindy.dsl.sexpr import Keyword, Symbol, loads


class RawIndexSyntaxError(ValueError):
    """Raised when a .raw file contains malformed data."""


@dataclass(slots=True)
class RawIndexEntry:
    """Representation of one ``(indexentry ...)`` S-expression."""

    key: tuple[str, ...]
    locref: str | None
    attr: str | None = None
    extras: Mapping[str, object] = field(default_factory=dict)


def parse_raw_index(text: str) -> list[RawIndexEntry]:
    """Parse the contents of a raw index file provided as a string."""
    forms = loads(text)
    return [_entry_from_form(form) for form in forms]


def load_raw_index(path: str | PathLike[str]) -> list[RawIndexEntry]:
    """Read ``path`` and parse every index entry."""
    try:
        content = Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = Path(path).read_text(encoding="latin-1")
    return parse_raw_index(content)


def _entry_from_form(form: object) -> RawIndexEntry:
    if not isinstance(form, list) or not form:
        raise RawIndexSyntaxError("indexentry must be a non-empty list")
    head, *rest = form
    if not isinstance(head, Symbol) or head.name != "indexentry":
        raise RawIndexSyntaxError("Unsupported form; only indexentry is allowed")
    if len(rest) % 2 != 0:
        raise RawIndexSyntaxError("indexentry property list must have even length")

    properties: dict[str, object] = {}
    for i in range(0, len(rest), 2):
        key = rest[i]
        if not isinstance(key, Keyword):
            raise RawIndexSyntaxError("indexentry properties must start with keywords")
        properties[key.name] = rest[i + 1]

    key = _coerce_key(properties.get("key"))
    locref = _coerce_optional_string(properties.get("locref"))
    attr = _coerce_optional_string(properties.get("attr"))
    extras = {
        name: value
        for name, value in properties.items()
        if name not in {"key", "locref", "attr"}
    }
    return RawIndexEntry(key=key, locref=locref, attr=attr, extras=extras)


def _coerce_key(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise RawIndexSyntaxError(":key must be a non-empty list")
    coerced: list[str] = []
    for part in value:
        if not isinstance(part, str):
            raise RawIndexSyntaxError(":key entries must be strings")
        coerced.append(part)
    return tuple(coerced)


def _coerce_optional_string(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise RawIndexSyntaxError("attribute values must be strings if provided")
    return value


__all__ = ["RawIndexEntry", "RawIndexSyntaxError", "load_raw_index", "parse_raw_index"]
