"""TeX conversion utilities."""

from .tex2xindy import convert_idx_to_raw_entries, parse_idx, parse_idx_line


def makeindex4_main(argv=None):
    """Lazy wrapper to avoid pre-importing makeindex4 during package import."""
    from .makeindex4 import main

    return main(argv)


__all__ = ["convert_idx_to_raw_entries", "makeindex4_main", "parse_idx", "parse_idx_line"]
