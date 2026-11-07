"""Public intake and projection behavior, independent of manuscript wording."""

from __future__ import annotations

import pytest


def test_strict_json_intake_refuses_nonfinite_status() -> None:
    """Nonfinite native data cannot receive a canonical report identity."""

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


def test_projection_precedence_and_declared_use() -> None:
    """Empty, blocked, and clean states preserve their distinct postures."""

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
