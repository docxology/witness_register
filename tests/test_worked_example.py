"""The worked example: four REAL exported envelopes through the real register.

The JSON files under ``data/envelopes/`` were generated on 2026-07-29 by
running each line's own public API in that line's own repository (provenance
in ``data/envelopes/README.md``) and are stored by value under the published
``line.report-envelope/1.0`` schema. This module is the first cross-work data
flow in the set, and it keeps the register's boundaries explicit: the four
envelopes describe four DIFFERENT worked subjects, so the honest relations
between them are incomparability and an open return contract, and the honest
posture for treating the co-registration as a live subject record is held.
"""

from __future__ import annotations

import json
from pathlib import Path

from witness_register import (
    RelationRecord,
    RelationType,
    ReturnContractRecord,
    genesis_state,
    intake_envelope,
    project,
    relation_fidelity,
    return_recoverability,
    seal_tip,
    update_state,
    verify_chain,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "envelopes"
FILES = (
    "red_line_worked.json",
    "black_line_worked.json",
    "golden_line_worked.json",
    "white_line_worked.json",
    "silver_line_worked.json",
    "violet_line_worked.json",
    "blue_line_worked.json",
    "green_line_worked.json",
)


def _payloads() -> list[dict]:
    payloads = [json.loads((DATA / name).read_text(encoding="utf-8")) for name in FILES]
    assert len(payloads) == len(FILES), "the worked example needs every declared export"
    return payloads


def _accepted_records():
    records = []
    for payload in _payloads():
        record, issues = intake_envelope(payload)
        assert record is not None, issues
        records.append(record)
    return records


def test_all_four_real_exports_pass_intake_unmodified() -> None:
    """Each line's actual exported payload has the published shape."""

    records = _accepted_records()
    assert [record.line_id for record in records] == [
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
        "silver_line",
        "violet_line",
        "blue_line",
        "green_line",
    ]
    for record in records:
        assert record.schema_version == "line.report-envelope/1.0"
        assert record.scope_and_nonclaims, record.line_id


def test_native_status_shapes_differ_and_are_stored_verbatim() -> None:
    """Six export a word, two export a structure; both are opaque here."""

    by_line = {record.line_id: record for record in _accepted_records()}
    assert isinstance(by_line["red_line"].native_status, str)
    assert isinstance(by_line["black_line"].native_status, str)
    assert isinstance(by_line["golden_line"].native_status, list)
    assert isinstance(by_line["white_line"].native_status, list)
    assert isinstance(by_line["silver_line"].native_status, str)
    assert isinstance(by_line["violet_line"].native_status, str)
    assert isinstance(by_line["blue_line"].native_status, str)
    assert isinstance(by_line["green_line"].native_status, str)
    for name, payload in zip(FILES, _payloads()):
        record, _ = intake_envelope(payload)
        assert record is not None
        assert record.native_status == payload["native_status"], name


def _worked_chain():
    """Genesis with the four envelopes; an update adding the honest records."""

    records = _accepted_records()
    refs = [record.report_ref for record in records]
    first = genesis_state(
        "line-set-worked-examples-2026-07-29", "2026-07-29", envelopes=records
    )
    cannot_compare = RelationRecord(
        relation_id="worked-cannot-compare-1",
        subject_id=first.subject_id,
        source_report_refs=(refs[0], refs[1]),
        relation_type=RelationType.CANNOT_COMPARE,
        bounded_description=(
            "red_line and black_line both spell a token OUTSIDE_SCOPE, and "
            "these two envelopes carry one word each; the comparison the "
            "shared spelling invites is not admitted — different instruments, "
            "different questions, different worked subjects"
        ),
    )
    contract = ReturnContractRecord(
        contract_id="worked-same-subject-return",
        subject_id=first.subject_id,
        why_held=(
            "the four envelopes describe four different worked cases; a "
            "same-subject co-registration does not exist yet"
        ),
        alternatives_live=(
            "use this state as a mechanics demonstration over real exports",
        ),
        change_condition=("all four lines export envelopes about one declared work"),
        standing="whoever runs the four reviews about one work",
        protected="nothing in this case",
        trigger="a same-subject export set enters data/envelopes/",
        acceptance_condition=(
            "four envelopes whose registrar declares one subject "
            "correspondence, co-registered in one state"
        ),
    )
    due = RelationRecord(
        relation_id="worked-return-due-1",
        subject_id=first.subject_id,
        source_report_refs=tuple(refs),
        relation_type=RelationType.RETURN_DUE,
        bounded_description=(
            "treating this co-registration as a live subject record owes a "
            "same-subject export set first"
        ),
        return_contract_ref=contract.contract_id,
    )
    second = update_state(
        first, "2026-07-29", relations=(cannot_compare, due), returns=(contract,)
    )
    return first, second


def test_the_worked_chain_is_sound_and_recoverable() -> None:
    first, second = _worked_chain()
    assert verify_chain((first, second)) == ()
    assert return_recoverability((first, second)) == 1.0
    assert seal_tip(second) == second.state_digest


def test_the_worked_projection_is_held_with_named_reasons() -> None:
    """Four real envelopes plus honest relations project to 0, not +1."""

    _, second = _worked_chain()
    projection = project(second, "treat this co-registration as a live subject record")
    assert projection.value == 0
    assert projection.state_ref == second.state_digest
    assert any("worked-cannot-compare-1" in reason for reason in projection.reasons)
    assert any("worked-return-due-1" in reason for reason in projection.reasons)
    assert relation_fidelity(projection, second) == 1.0


def test_a_mechanics_demonstration_use_is_also_answered_not_assumed() -> None:
    """Even the modest declared use gets the same held posture: the relations
    are unresolved for every declared use, which is the non-compensatory
    design working as stated — the register does not scope reasons to uses."""

    _, second = _worked_chain()
    projection = project(
        second, "demonstrate intake, relations, and projection over real exports"
    )
    assert projection.value == 0
    assert projection.reasons


def test_intake_rejects_a_tampered_export_loudly() -> None:
    """Bit-flip one real export's report_ref shape and intake refuses, typed."""

    payload = _payloads()[0]
    payload["report_ref"] = payload["report_ref"][:-1] + "Z"
    record, issues = intake_envelope(payload)
    assert record is None
    assert any(issue.field == "report_ref" for issue in issues)
