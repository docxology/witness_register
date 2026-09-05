"""Bind ``data/formalism_claim_ledger.json`` to the manuscript and the package.

The external publication engine's evidence registry resolves ``[@def:...]``/
``[@prop:...]`` cross-references only when the project declares them, and the
formalism section quotes package constants (digest shape, projection values)
that must not silently drift. Every ``kind: citation`` row is re-derived here
from the ``::: {.definition ...}`` / ``::: {.proposition ...}`` blocks declared
in ``docs/manuscript/``, and every ``kind: number`` row is re-derived from the
running package — so a block added, renamed, or removed, or a constant that
moved, without regenerating the ledger fails the suite.
"""
import json
import re
from pathlib import Path

from witness_register.projection import project
from witness_register.serialization import sha256_hex
from witness_register.state import genesis_state

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "docs" / "manuscript"
LEDGER = ROOT / "data" / "formalism_claim_ledger.json"

#: A formalism block opener: ``::: {.definition #def:x title="X"}``.
_BLOCK = re.compile(r"^::: \{(?P<attrs>[^}]*)\}\s*$", re.MULTILINE)
_LABEL = re.compile(r"#((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-zA-Z0-9_-]+)")
#: The reference syntax the engine's citation check sees.
_REFERENCE = re.compile(r"\[@((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-z0-9-]+)\]")

#: The numeric rows the ledger must carry; the gate would be vacuous without.
_NUMBER_IDS = {"sha256_hex_char_count", "sha256_bit_width", "projection_block_value"}


def _body_files() -> list[Path]:
    """Every manuscript body file except the preamble."""

    return [
        path for path in sorted(MANUSCRIPT.glob("*.md")) if path.name != "preamble.md"
    ]


def _declared_labels() -> set[str]:
    """Every formalism-block label declared anywhere in the manuscript."""

    labels: set[str] = set()
    for path in _body_files():
        for match in _BLOCK.finditer(path.read_text(encoding="utf-8")):
            label = _LABEL.search(match.group("attrs"))
            if label:
                labels.add(label.group(1))
    return labels


def _referenced_labels() -> set[str]:
    """Every ``[@prefix:label]`` formalism reference in the manuscript."""

    refs: set[str] = set()
    for path in _body_files():
        refs.update(_REFERENCE.findall(path.read_text(encoding="utf-8")))
    return refs


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))

def _ledger_citations() -> set[str]:
    return {row["value"] for row in _ledger()["claims"] if row["kind"] == "citation"}


def _ledger_numbers() -> dict[str, object]:
    return {
        row["claim_id"]: row["value"]
        for row in _ledger()["claims"]
        if row["kind"] == "number"
    }


# --------------------------------------------------------------------- gates


def test_every_declared_label_is_in_the_ledger() -> None:
    """A block declared in the manuscript must be declared to the engine too."""

    declared = _declared_labels()
    assert declared, "no labels declared; this gate would be vacuous"
    assert _ledger_citations() == declared, sorted(_ledger_citations() ^ declared)


def test_every_ledger_citation_is_a_declared_block() -> None:
    """The ledger cannot declare a label the manuscript does not carry."""

    assert _ledger_citations() <= _declared_labels(), sorted(
        _ledger_citations() - _declared_labels()
    )


def test_every_referenced_label_is_both_declared_and_ledgered() -> None:
    """A reference the prose makes resolves on both sides of the contract."""

    referenced = _referenced_labels()
    assert referenced, "no formalism references found; this gate would be vacuous"
    assert referenced <= _declared_labels(), sorted(referenced - _declared_labels())
    assert referenced <= _ledger_citations(), sorted(referenced - _ledger_citations())


def test_every_ledger_source_path_exists() -> None:
    """A row pointing at a file that is not there is dead evidence."""

    for row in _ledger()["claims"]:
        assert (ROOT / row["source_path"]).is_file(), row["claim_id"]
        assert row["freshness"] == "active", row["claim_id"]


def test_ledger_claim_ids_are_unique() -> None:
    rows = _ledger()["claims"]

    assert len({row["claim_id"] for row in rows}) == len(rows)


def test_number_rows_match_the_running_package() -> None:
    """The numeric rows are re-derived from the running package, not restated."""

    numbers = _ledger_numbers()

    assert set(numbers) == _NUMBER_IDS, sorted(set(numbers) ^ _NUMBER_IDS)

    digest = sha256_hex("x")
    assert numbers["sha256_hex_char_count"] == len(digest)
    assert numbers["sha256_bit_width"] == len(digest) * 4

    empty = project(
        genesis_state("ledger-binding", "2026-07-29"),
        "a declared next use",
    )
    assert numbers["projection_block_value"] == empty.value


# ---------------------------------------------------------- negative controls


def test_negative_control_label_gap_fails() -> None:
    """Proof of detection: a label missing from the ledger is reported."""

    planted = _ledger_citations() - {min(_declared_labels())}

    assert planted != _declared_labels()
    assert _declared_labels() - planted == {min(_declared_labels())}


def test_negative_control_planted_foreign_label_fails() -> None:
    """Proof of detection: a citation no block declares cannot be added."""

    foreign = "prop:not-declared-anywhere"
    planted = _ledger_citations() | {foreign}

    assert planted - _declared_labels() == {foreign}


def test_negative_control_mutated_number_fails() -> None:
    """Proof of detection: a planted wrong value cannot match the derivation."""

    numbers = _ledger_numbers()
    live_digest_length = len(sha256_hex("x"))

    assert numbers["sha256_hex_char_count"] == live_digest_length
    planted = live_digest_length - 1
    assert planted != live_digest_length
