"""Command-line entry point for the Python xindy port."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import __version__


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
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (placeholder; functional later).",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Inputs (.xdy/.raw) - accepted later in the porting roadmap.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by both python -m xindy and console scripts."""
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    if args.files:
        missing = ", ".join(args.files)
        parser.error(
            f"input handling not yet implemented; received: {missing}",
        )

    if args.verbose:
        print("Verbose mode is not wired yet.", file=sys.stderr)

    print("xindy Python port scaffolding in place.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
