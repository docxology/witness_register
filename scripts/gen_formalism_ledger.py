#!/usr/bin/env python3
"""Regenerate ``data/formalism_claim_ledger.json``.

Thin orchestrator: parsing and derivation live in
``witness_register.formalism_ledger``; this file only parses the command line.
"""

from __future__ import annotations

import argparse
import sys

from witness_register.formalism_ledger import build_ledger


def build_parser() -> argparse.ArgumentParser:
    """The CLI: no arguments are honoured besides ``--help``."""

    return argparse.ArgumentParser(
        prog="gen_formalism_ledger.py",
        description="Regenerate data/formalism_claim_ledger.json.",
    )


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    print(build_ledger())
    return 0


if __name__ == "__main__":
    sys.exit(main())
