"""Minimal TeX ``.idx`` to xindy ``.raw`` converter."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from xindy.raw.reader import RawIndexEntry

_ENTRY_PATTERN = re.compile(r"\\indexentry\{(.+?)\}\{(.+?)\}")


@dataclass(slots=True)
class IdxEntry:
    term: str
    attr: str | None
    loc: str

    def to_raw(self) -> RawIndexEntry:
        key = tuple(part.strip() for part in self.term.split("!") if part.strip())
        return RawIndexEntry(key=key, locref=self.loc, attr=self.attr, extras={})


def parse_idx_line(line: str) -> IdxEntry | None:
    """Parse a single ``\\indexentry{...}{...}`` line."""
    match = _ENTRY_PATTERN.search(line)
    if not match:
        return None
    body, loc = match.groups()
    term, attr = _split_attr(body)
    return IdxEntry(term=term, attr=attr, loc=loc)


def _split_attr(body: str) -> tuple[str, str | None]:
    attr: str | None = None
    term = body
    if "|" in body:
        term, attr = body.split("|", 1)
    if "@" in term:
        term = term.split("@", 1)[0]
    return term, attr


def parse_idx(text: str) -> list[IdxEntry]:
    """Parse an entire .idx file text into IdxEntry objects."""
    entries: list[IdxEntry] = []
    for line in text.splitlines():
        parsed = parse_idx_line(line)
        if parsed:
            entries.append(parsed)
    return entries


def convert_idx_to_raw_entries(
    path: str | Path,
    *,
    encoding: str = "latin-1",
) -> list[RawIndexEntry]:
    """Read an .idx file and return corresponding RawIndexEntry objects."""
    text = Path(path).read_text(encoding=encoding)
    idx_entries = parse_idx(text)
    return [entry.to_raw() for entry in idx_entries]


def write_raw(
    entries: Iterable[RawIndexEntry],
    dest: str | Path,
    *,
    encoding: str = "utf-8",
) -> None:
    """Serialize raw entries to ``dest`` as xindy ``.raw`` S-expressions."""
    lines = []
    for entry in entries:
        props = [':key ("' + '" "'.join(_escape(s) for s in entry.key) + '")']
        if entry.attr:
            props.append(f':attr "{_escape(entry.attr)}"')
        if entry.locref:
            props.append(f':locref "{_escape(entry.locref)}"')
        # extras ignored for now
        props_str = " ".join(props)
        lines.append(f"(indexentry {props_str})")
    Path(dest).write_text("\n".join(lines) + "\n", encoding=encoding)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="tex2xindy",
        description="Minimal TeX .idx to xindy .raw converter (Python port).",
    )
    parser.add_argument("idx", help="Input .idx file")
    parser.add_argument("-o", "--output", help="Output .raw file (default: stdout)")
    parser.add_argument(
        "--input-encoding",
        default="latin-1",
        help="Encoding of the .idx file (default: latin-1)",
    )
    parser.add_argument(
        "--output-encoding",
        default="utf-8",
        help="Encoding of the .raw output (default: utf-8)",
    )
    parser.add_argument("--log", help="Optional log file.")
    args = parser.parse_args(argv)

    entries = convert_idx_to_raw_entries(args.idx, encoding=args.input_encoding)
    if args.log:
        Path(args.log).write_text(f"converted {len(entries)} entries\n", encoding="utf-8")
    if args.output:
        write_raw(entries, args.output, encoding=args.output_encoding)
    else:
        for e in entries:
            props = [':key ("' + '" "'.join(_escape(s) for s in e.key) + '")']
            if e.attr:
                props.append(f':attr "{_escape(e.attr)}"')
            if e.locref:
                props.append(f':locref "{_escape(e.locref)}"')
            print(f"(indexentry {' '.join(props)})")
    return 0


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    raise SystemExit(main())
