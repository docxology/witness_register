#!/usr/bin/env python3
"""Build the register's deterministic figure plates and registry.

Thin CLI: the package owns every drawing decision and every live derivation;
this script names an output directory and reports what was written. Two runs
produce byte-identical artifacts; ``tests/test_figures.py`` gates that.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from witness_register.figures import OUTPUT_DIR, build_figures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="directory that receives the SVG/PNG plates and figure_registry.json",
    )
    args = parser.parse_args(argv)
    written = build_figures(args.output)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
