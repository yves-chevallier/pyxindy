"""Command-line entry point for the Python xindy port."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Sequence

from . import __version__
from .dsl.interpreter import StyleError, StyleInterpreter
from .dsl.sexpr import SExprSyntaxError
from .index import build_index_entries
from .markup import render_index
from .raw.reader import load_raw_index


def build_argument_parser() -> argparse.ArgumentParser:
    """Return the argparse configuration used by the CLI."""
    parser = argparse.ArgumentParser(
        prog="xindy",
        description="Experimental Python port of the xindy index processor.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"xindy {__version__}",
        help="Print the xindy version and exit.",
    )
    parser.add_argument("-o", "--output", help="Write output to FILE instead of stdout.")
    parser.add_argument(
        "-M",
        "--module",
        dest="style",
        help="Style file (.xdy). Defaults to <raw>.xdy if omitted.",
    )
    parser.add_argument(
        "-L",
        "--searchpath",
        action="append",
        default=[],
        help="Additional style search path (can be given multiple times).",
    )
    parser.add_argument(
        "-C",
        "--codepage",
        default="utf-8",
        help="Encoding used to write the output (default: utf-8).",
    )
    parser.add_argument(
        "-l",
        "--log",
        dest="logfile",
        help="Write a brief log to FILE (best-effort).",
    )
    parser.add_argument(
        "-t",
        "--trace",
        action="store_true",
        help="Print tracebacks on errors.",
    )
    parser.add_argument(
        "raw",
        nargs=1,
        help="Raw index file (.raw) to process.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by both python -m xindy and console scripts."""
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    raw_path = Path(args.raw[0]).resolve()
    if not raw_path.exists():
        parser.error(f"raw file not found: {raw_path}")

    style_path = Path(args.style).resolve() if args.style else raw_path.with_suffix(".xdy")
    if not style_path.exists():
        parser.error(f"style file not found: {style_path}")

    search_paths: list[Path] = []
    env_search = os.environ.get("XINDY_SEARCHPATH")
    if env_search:
        search_paths.extend(
            Path(p).resolve() for p in env_search.split(os.pathsep) if p.strip()
        )
    search_paths.extend(Path(p).resolve() for p in args.searchpath)
    # ensure style directory is always searched for relative requires
    search_paths.append(style_path.parent)

    logfile = Path(args.logfile).resolve() if args.logfile else None

    def _log(message: str) -> None:
        if logfile:
            logfile.parent.mkdir(parents=True, exist_ok=True)
            with logfile.open("a", encoding="utf-8") as fh:
                fh.write(message + "\n")

    try:
        interpreter = StyleInterpreter()
        state = interpreter.load(style_path, extra_search_paths=search_paths)
        raw_entries = load_raw_index(raw_path)
        index = build_index_entries(raw_entries, state)
        output = render_index(index, style_state=state)
    except (FileNotFoundError, StyleError, SExprSyntaxError) as exc:
        print(f"xindy error: {exc}", file=sys.stderr)
        _log(f"error: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - defensive path
        if args.trace:
            raise
        print(f"xindy error: {exc}", file=sys.stderr)
        _log(f"error: {exc}")
        return 1

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding=args.codepage)
        _log(f"wrote {out_path}")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
