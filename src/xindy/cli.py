"""Command-line entry point for the Python xindy port."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import os
from pathlib import Path
import subprocess
import sys

from . import __version__
from .dsl.interpreter import StyleError, StyleInterpreter
from .dsl.sexpr import SExprSyntaxError
from .index import build_index_entries
from .markup import render_index
from .raw.reader import load_raw_index, parse_raw_index


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
        "-f",
        "--filter",
        dest="filter_cmd",
        help="Filter program to preprocess raw input (read from stdin, emit raw).",
    )
    parser.add_argument(
        "-L",
        "--searchpath",
        action="append",
        default=[],
        help="Additional style search path (can be given multiple times).",
    )
    parser.add_argument(
        "--log-level",
        "-V",
        dest="loglevel",
        type=int,
        default=None,
        help="Logging verbosity level (compat xindy.in -L).",
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
        "--markup-trace",
        action="store_true",
        help="Enable markup tracing (compat -t from xindy.in; best-effort).",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Compatibility flag (interactive mode not supported; ignored with warning).",
    )
    parser.add_argument(
        "-n",
        "--try-run",
        action="store_true",
        help="Compatibility flag (try-run/skip checks; ignored with warning).",
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

    raw_arg = args.raw[0]
    if raw_arg == "-":
        raw_path = None
    else:
        raw_path = Path(raw_arg).resolve()
        if not raw_path.exists():
            parser.error(f"raw file not found: {raw_path}")

    style_path = (
        Path(args.style).resolve()
        if args.style
        else (raw_path.with_suffix(".xdy") if raw_path else None)
    )
    if style_path is None or not style_path.exists():
        parser.error(f"style file not found: {style_path}")

    search_paths: list[Path] = []
    env_search = os.environ.get("XINDY_SEARCHPATH")
    if env_search:
        search_paths.extend(Path(p).resolve() for p in env_search.split(os.pathsep) if p.strip())
    search_paths.extend(Path(p).resolve() for p in args.searchpath)
    # ensure style directory is always searched for relative requires
    search_paths.append(style_path.parent)

    logfile = Path(args.logfile).resolve() if args.logfile else None

    def _log(message: str) -> None:
        if logfile:
            logfile.parent.mkdir(parents=True, exist_ok=True)
            with logfile.open("a", encoding="utf-8") as fh:
                fh.write(message + "\n")
        elif args.loglevel:
            sys.stderr.write(message + "\n")

    try:
        interpreter = StyleInterpreter()
        state = interpreter.load(style_path, extra_search_paths=search_paths)
        if args.markup_trace:
            state.markup_options.setdefault("trace", {})["enabled"] = True
        if args.interactive:
            print(
                "warning: interactive mode (-i) not supported in Python port; ignoring",
                file=sys.stderr,
            )
        if args.try_run:
            print("note: try-run (-n) has no effect in Python port", file=sys.stderr)
        if args.loglevel is not None:
            _log(f"log level set to {args.loglevel}")

        if args.filter_cmd:
            raw_text = _read_raw_text(raw_path, args.codepage)
            filtered = subprocess.run(
                args.filter_cmd,
                input=raw_text.encode(args.codepage),
                capture_output=True,
                shell=True,
            )
            if filtered.returncode != 0:
                raise RuntimeError(
                    f"filter command failed ({filtered.returncode}): {filtered.stderr.decode(errors='ignore')}"
                ) from None
            raw_entries = parse_raw_index(filtered.stdout.decode(args.codepage))
        elif raw_path is None:
            raw_text = sys.stdin.buffer.read().decode(args.codepage)
            raw_entries = parse_raw_index(raw_text)
        else:
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


def _read_raw_text(raw_path: Path | None, encoding: str) -> str:
    if raw_path is None:
        return sys.stdin.buffer.read().decode(encoding)
    try:
        return raw_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        return raw_path.read_text(encoding="latin-1")


if __name__ == "__main__":
    raise SystemExit(main())
