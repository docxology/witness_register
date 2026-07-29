"""Regression tests for the wave-3 adversarial pass (2026-07-29).

Each test here binds a defect the hostile pass actually produced against the
public API before the fix, or a resistance the pass confirmed under a fresh
hostile construction. No mocks; every case builds real records and exercises
the real functions.
"""

from __future__ import annotations

import json

import pytest

from witness_register import (
    IssueCode,
    RelationType,
    canonical_json,
    genesis_state,
    intake_envelope,
    project,
)

from conftest import accept, make_contract, make_payload, make_relation


def test_whitespace_only_verification_result_is_refused_at_construction() -> None:
    """Before the fix, ``verification_result='   '`` made ``is_met`` True.

    Measured 2026-07-29: a directly constructed contract with a
    whitespace-only verification lifted a RETURN_DUE hold all the way to +1
    — a crown without a return. The record type now refuses the ambiguous
    value: empty means open, content means a return happened, whitespace-only
    means nothing and raises.
    """

    with pytest.raises(ValueError, match="verification_result"):
        make_contract(verification_result="   ")


def test_whitespace_only_open_remainder_is_refused_at_construction() -> None:
    with pytest.raises(ValueError, match="open_remainder"):
        make_contract(verification_result="verified in full", open_remainder="   ")


def test_return_due_with_unverified_contract_still_holds_under_agreement(
    envelope,
) -> None:
    """Agreement volume never buys back an outstanding return."""

    contract = make_contract()
    due = make_relation(
        envelope,
        relation_type=RelationType.RETURN_DUE,
        relation_id="due-1",
        return_contract_ref="con-1",
    )
    agrees = tuple(
        make_relation(
            envelope,
            relation_id=f"agree-{index}",
            human_decision_ref=f"decision-{index}",
        )
        for index in range(50)
    )
    state = genesis_state(
        "subject-1",
        "2026-07-29",
        envelopes=(envelope,),
        relations=agrees + (due,),
        returns=(contract,),
    )
    assert project(state, "proceed as if returned").value == 0


def test_nan_and_infinity_are_refused_at_intake() -> None:
    """Before the fix, ``json.dumps`` default ``allow_nan=True`` accepted
    ``float('nan')`` and the canonical form of the sealed state carried a
    bare ``NaN`` literal that no strict JSON parser reads back."""

    for poison in (float("nan"), float("inf"), float("-inf")):
        record, issues = intake_envelope(make_payload(native_status={"score": poison}))
        assert record is None
        assert any(
            issue.code is IssueCode.MALFORMED_FIELD and issue.field == "native_status"
            for issue in issues
        )


def test_canonical_json_refuses_nan_rather_than_emitting_it() -> None:
    with pytest.raises(ValueError):
        canonical_json({"value": float("nan")})


def test_canonical_json_output_is_strict_json_round_trippable() -> None:
    payload = {"a": [1, 2.5, "x"], "b": {"nested": True, "n": None}}
    assert json.loads(canonical_json(payload)) == payload


def test_project_refuses_a_state_whose_content_was_mutated_after_sealing(
    envelope,
) -> None:
    """Before the fix, ``project`` stamped ``state_ref`` onto rewritten
    history: mutating a stored envelope's ``native_status`` dict in place
    left the seal stale and the projection still carried it as if it named
    the live content."""

    state = genesis_state("subject-1", "2026-07-29", envelopes=(envelope,))
    assert project(state, "any declared use").value == 1
    envelope.native_status["verdict"] = "rewritten-after-sealing"
    with pytest.raises(ValueError, match="seal"):
        project(state, "any declared use")


def test_project_on_an_untampered_state_still_works_after_the_seal_check(
    second_envelope,
) -> None:
    state = genesis_state("subject-1", "2026-07-29", envelopes=(second_envelope,))
    projection = project(state, "any declared use")
    assert projection.value == 1
    assert projection.state_ref == state.state_digest


def test_subject_correspondence_is_declared_not_checked() -> None:
    """The stated non-check, bound so it cannot silently become a check.

    Two lines spell the same work's subject differently; the register
    stores both spellings verbatim and leaves the correspondence to the
    registration decision and its review. ``genesis_state``'s docstring
    states this; if enforcement is ever added, this test and that docstring
    must move together.
    """

    foreign = accept(make_payload(subject_id="the-same-work-spelled-redly"))
    state = genesis_state("subject-1", "2026-07-29", envelopes=(foreign,))
    assert state.envelopes[0].subject_id == "the-same-work-spelled-redly"
    assert state.subject_id == "subject-1"
    from witness_register.state import genesis_state as documented

    assert "NOT required to equal" in (documented.__doc__ or "")
