"""Derivation of ``data/formalism_claim_ledger.json`` from the manuscript and package.

The external publication engine's evidence registry resolves ``[@def:...]``/
``[@prop:...]`` cross-references only when the project declares them, so this
module re-derives the whole declaration from the manuscript's formalism blocks
and writes ``data/formalism_claim_ledger.json``. The ``kind: number`` rows are
re-derived from the running package at generation time. Tests re-derive the
same set, so a block added, renamed, or removed — or a constant that moved —
without regenerating fails the suite.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from witness_register.projection import project
from witness_register.serialization import sha256_hex
from witness_register.state import genesis_state

ROOT = Path(__file__).resolve().parents[2]
MS = ROOT / "docs" / "manuscript"

_LAB = re.compile(
    r"^::: \{[^}]*#((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-zA-Z0-9_-]+)",
    re.MULTILINE,
)


def citation_rows() -> list[dict[str, str]]:
    """Every formalism-block label declared in the manuscript, in text order."""

    rows: list[dict[str, str]] = []
    for f in sorted(MS.glob("*.md")):
        for label in _LAB.findall(f.read_text(encoding="utf-8")):
            cid = label.replace(":", "_").replace("-", "_")
            kind_word = "definition" if label.startswith("def:") else "proposition"
            rows.append(
                {
                    "claim_id": cid,
                    "kind": "citation",
                    "value": label,
                    "source": (
                        f"docs/manuscript/{f.name}: {kind_word} block declared "
                        "with this label"
                    ),
                    "source_path": f"docs/manuscript/{f.name}",
                    "source_tier": "manuscript_formalism_block",
                    "freshness": "active",
                }
            )
    return rows


def number_rows() -> list[dict[str, object]]:
    """The package constants the formalism section states, re-derived live."""

    digest = sha256_hex("x")
    empty = project(
        genesis_state("ledger-derivation", "2026-07-29"),
        "a declared next use",
    )
    return [
        {
            "claim_id": "sha256_hex_char_count",
            "kind": "number",
            "value": len(digest),
            "source": "witness_register.serialization.sha256_hex: hex digest length",
            "source_path": "src/witness_register/serialization.py",
            "source_tier": "package_constant",
            "freshness": "active",
        },
        {
            "claim_id": "sha256_bit_width",
            "kind": "number",
            "value": len(digest) * 4,
            "source": (
                "witness_register.serialization.sha256_hex: hashlib.sha256 "
                "digest width (4 bits per hex character)"
            ),
            "source_path": "src/witness_register/serialization.py",
            "source_tier": "package_constant",
            "freshness": "active",
        },
        {
            "claim_id": "projection_block_value",
            "kind": "number",
            "value": empty.value,
            "source": (
                "witness_register.projection.project: an empty genesis state "
                "projects to -1 — nothing to witness is not permission"
            ),
            "source_path": "src/witness_register/projection.py",
            "source_tier": "package_constant",
            "freshness": "active",
        },
    ]


def build_ledger() -> str:
    """Derive every claim, write the ledger, and return the summary line."""

    claims: list[dict[str, object]] = citation_rows() + number_rows()
    doc = {
        "claim_boundary": (
            "Grounds the manuscript's formalism cross-references and package "
            "constants in the evidence registry. Every `kind: citation` row "
            "re-derives from a formalism block label declared in "
            "docs/manuscript/, and every `kind: number` row re-derives from "
            "the running package, via tests/test_formalism_claim_ledger.py. "
            "These rows support reproducibility of the code description only; "
            "they do not establish that any proposition is universally valid."
        ),
        "schema_version": "1.0",
        "claims": claims,
    }
    out = ROOT / "data" / "formalism_claim_ledger.json"
    out.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return f"wrote {out.relative_to(ROOT)} with {len(claims)} claims"
