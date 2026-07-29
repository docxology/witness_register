"""The same-subject co-registration: the first worked chain's return, met.

The four records under ``data/envelopes/same_subject/`` are each line's real
evaluator output about ONE declared work — witness_register 0.1.0 itself —
with registrar-authored inputs whose provenance is recorded in
``data/envelopes/README.md`` and inside each envelope's ``subject_id``.
This module proves three things end to end: the exports pass intake
unmodified; completing the first chain's return contract lifts exactly the
``return_due`` hold and no other; and the same-subject state's own posture
is held at 0 for an honest reason (white_line's open question, recorded as
an unresolved dependency) rather than crowned because most readings look
favorable.
"""

from __future__ import annotations

import json
from pathlib import Path

from test_worked_example import _worked_chain

from witness_register import (
    RelationRecord,
    RelationType,
    genesis_state,
    intake_envelope,
    project,
    record_return,
    relation_fidelity,
    return_recoverability,
    update_state,
    verify_chain,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "envelopes" / "same_subject"
FILES = (
    "red_line_same_subject.json",
    "black_line_same_subject.json",
    "golden_line_same_subject.json",
    "white_line_same_subject.json",
)
SUBJECT = "witness_register-0.1.0-as-declared-2026-07-29"


def _records():
    records = []
    for name in FILES:
        payload = json.loads((DATA / name).read_text(encoding="utf-8"))
        record, issues = intake_envelope(payload)
        assert record is not None, (name, issues)
        records.append(record)
    return records


def test_all_four_same_subject_exports_pass_intake_unmodified() -> None:
    records = _records()
    assert [r.line_id for r in records] == [
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
    ]
    for record in records:
        assert "witness_register 0.1.0" in record.subject_id, record.line_id
        assert (
            "registrar-authored" in record.subject_id
            or "registrar" in record.subject_id
        )


def _same_subject_state():
    records = _records()
    refs = [r.report_ref for r in records]
    state = genesis_state(SUBJECT, "2026-07-29", envelopes=records)
    dependency = RelationRecord(
        relation_id="same-subject-open-question",
        subject_id=SUBJECT,
        source_report_refs=tuple(refs),
        relation_type=RelationType.UNRESOLVED_DEPENDENCY,
        bounded_description=(
            "white_line's report records an UNRESOLVED question — whether "
            "co-registering four instruments over one work quietly invites "
            "the aggregate reading the set refuses; the meaning of any "
            "favorable posture for this co-registration depends on it"
        ),
    )
    agrees = RelationRecord(
        relation_id="same-subject-agrees-1",
        subject_id=SUBJECT,
        source_report_refs=(refs[1], refs[2]),
        relation_type=RelationType.AGREES,
        bounded_description=(
            "black_line's declaration-coverage reading and golden_line's two "
            "directional readings independently point the same way about this "
            "window; stated as a relation, never merged into one number"
        ),
        human_decision_ref="registrar-read-2026-07-29",
    )
    return update_state(state, "2026-07-29", relations=(dependency, agrees))


def test_the_same_subject_posture_is_held_for_the_honest_reason() -> None:
    """Three favorable readings and one open question: held, not crowned."""

    state = _same_subject_state()
    projection = project(state, "hold these four reports as one work's witness record")
    assert projection.value == 0
    assert any("same-subject-open-question" in reason for reason in projection.reasons)
    assert relation_fidelity(projection, state) == 1.0


def test_completing_the_return_lifts_exactly_the_return_due_hold() -> None:
    """The first chain's contract is met by a NEW record; only that hold moves."""

    first, second = _worked_chain()
    before = project(second, "treat this co-registration as a live subject record")
    assert before.value == 0
    kinds_before = {reason.split(" ")[0] for reason in before.reasons if "(" in reason}

    open_contract = second.returns[0]
    completed = record_return(
        open_contract,
        verification_result=(
            "four same-subject envelopes about witness_register 0.1.0 exist "
            "under data/envelopes/same_subject/ and pass intake unmodified; "
            "provenance in data/envelopes/README.md"
        ),
        open_remainder="",
    )
    assert completed.is_met
    third = update_state(second, "2026-07-29", returns=(completed,))
    assert verify_chain((first, second, third)) == ()
    assert return_recoverability((first, second, third)) == 1.0

    after = project(third, "treat this co-registration as a live subject record")
    assert after.value == 0, (
        "CANNOT_COMPARE still holds; the return lifted only its own hold"
    )
    assert not any("return_due" in reason for reason in after.reasons)
    assert any(
        "cannot-compare" in reason.lower() or "CANNOT_COMPARE" in reason
        for reason in after.reasons
    )
    assert len(after.reasons) < len(before.reasons)
    assert kinds_before  # the before-state really did carry named holds


def test_the_open_record_is_untouched_by_its_completion() -> None:
    _first, second = _worked_chain()
    open_contract = second.returns[0]
    record_return(open_contract, "met", "")
    assert open_contract.verification_result == ""
