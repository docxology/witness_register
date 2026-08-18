"""Bind manuscript/02a_formalism.md to the running package.

Each test derives a fact from the code — field rosters via
``dataclasses.fields``, behaviour via real calls — and then asserts the
manuscript states exactly that. Corrupting a definition fails the matching
test here; corrupting the code fails the derivation inside it. Blocks carry
no hand-written numbers; a planted literal is rejected by its own guard.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

import pytest

from witness_register import EnvelopeRecord, WitnessState

FORMALISM = Path(__file__).resolve().parents[1] / "manuscript" / "02a_formalism.md"

_COUNT_WORDS = {8: "eight", 9: "nine", 10: "ten", 11: "eleven"}


def _normalized() -> str:
    return " ".join(FORMALISM.read_text(encoding="utf-8").split())


def _tuple_arity(left_hand_side: str) -> int:
    match = re.search(
        rf"{re.escape(left_hand_side)} = \((?P<body>[^)]*)\)", _normalized()
    )
    assert match is not None, left_hand_side
    return len(re.split(r",\\ ", match.group("body")))


def test_envelope_record_tuple_matches_the_dataclass() -> None:
    fields = [field.name for field in dataclasses.fields(EnvelopeRecord)]
    assert _tuple_arity("e") == len(fields)
    text = _normalized()
    assert f"exactly those {_COUNT_WORDS[len(fields)]} fields, in order" in text
    for name in fields:
        assert name.replace("_", "\\_") in text, name


def test_witness_state_tuple_matches_the_dataclass() -> None:
    fields = [field.name for field in dataclasses.fields(WitnessState)]
    assert _tuple_arity("X") == len(fields)
    text = _normalized()
    assert f"exactly those {_COUNT_WORDS[len(fields)]} fields" in text
    for name in fields:
        assert name.replace("_", "\\_") in text, name


def test_strict_json_claim_is_the_intake_behaviour() -> None:
    """The NaN/Infinity sentence is measured, not transcribed."""

    from witness_register import intake_envelope

    payload = {
        "schema_version": "line.report-envelope/1.0",
        "line_id": "red_line",
        "subject_id": "s",
        "review_date": "2026-07-29",
        "registry_version": "1.0",
        "registry_digest": "a" * 64,
        "native_status": {"score": float("nan")},
        "report_ref": "b" * 64,
        "source_snapshot_refs": ["snap"],
        "scope_and_nonclaims": ["a boundary"],
    }
    record, issues = intake_envelope(payload)
    assert record is None
    assert any(issue.field == "native_status" for issue in issues)
    assert "`NaN` or `Infinity` in its status is refused" in _normalized()


def test_projection_precedence_sentences_are_the_measured_order() -> None:
    """Every clause the projection definition states is exercised live."""

    from witness_register import (
        RelationRecord,
        RelationType,
        genesis_state,
        intake_envelope,
        project,
    )

    payload = {
        "schema_version": "line.report-envelope/1.0",
        "line_id": "black_line",
        "subject_id": "s",
        "review_date": "2026-07-29",
        "registry_version": "1.0",
        "registry_digest": "a" * 64,
        "native_status": "OPAQUE",
        "report_ref": "b" * 64,
        "source_snapshot_refs": ["snap"],
        "scope_and_nonclaims": ["a boundary"],
    }
    envelope, issues = intake_envelope(payload)
    assert envelope is not None, issues

    empty = genesis_state("s", "2026-07-29")
    assert project(empty, "u").value == -1

    block = RelationRecord(
        relation_id="b1",
        subject_id="s",
        source_report_refs=("b" * 64,),
        relation_type=RelationType.NON_COMPENSATORY_BLOCK,
        bounded_description="a blocked route",
    )
    blocked = genesis_state(
        "s", "2026-07-29", envelopes=(envelope,), relations=(block,)
    )
    assert project(blocked, "u").value == -1

    clean = genesis_state("s", "2026-07-29", envelopes=(envelope,))
    assert project(clean, "u").value == 1

    with pytest.raises(ValueError, match="declared"):
        project(clean, "   ")

    text = _normalized()
    assert "blank $u$ raises" in text
    assert "nothing to witness is not permission" in text
    assert "$+1$ is reachable only when at least one envelope record" in text


#: Shared so the positive-control test can never use a different pattern than
#: the real gate and silently become vacuous.
_HAND_NUMBER_PATTERN = re.compile(r"\b(Definition|Proposition)\s+\d+\b")


def test_no_hand_written_formalism_numbers() -> None:
    """The renderer numbers the blocks; the source must not."""

    assert _HAND_NUMBER_PATTERN.search(FORMALISM.read_text(encoding="utf-8")) is None


def test_the_hand_number_guard_rejects_a_planted_literal() -> None:
    assert _HAND_NUMBER_PATTERN.search("as Definition 3 states") is not None


def test_worked_example_numbers_in_prose_match_the_measured_run() -> None:
    """The worked-co-registration paragraph quotes the measured outcomes."""

    text = _normalized()
    assert "return recoverability $1.0$" in text
    assert "relation fidelity $1.0$" in text
    assert "held at $0$" in text
    # The measured facts themselves are re-derived in tests/test_worked_example.py;
    # here the prose is pinned to the same outcomes so the two cannot drift apart
    # silently while both stay green.
    from tests.test_worked_example import _worked_chain

    from witness_register import project, relation_fidelity, return_recoverability

    first, second = _worked_chain()
    projection = project(second, "treat this co-registration as a live subject record")
    assert projection.value == 0
    assert relation_fidelity(projection, second) == 1.0
    assert return_recoverability((first, second)) == 1.0
