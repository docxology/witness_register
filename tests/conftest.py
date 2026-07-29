"""Shared real-record builders for the test suite. No mocks anywhere.

Envelope payload dicts copy the published ``line.report-envelope/1.0`` field
names by value — that is the point of a published schema — and every record
is built through the register's own public API.
"""

from __future__ import annotations

import subprocess
import sys
import warnings
from pathlib import Path

import pytest

from witness_register import (
    ENVELOPE_SCHEMA,
    EnvelopeRecord,
    RelationRecord,
    RelationType,
    ReturnContractRecord,
    UnclassifiedHeld,
    intake_envelope,
    sha256_hex,
)


@pytest.fixture(scope="session", autouse=True)
def build_figures_before_tests() -> None:
    """Build figures into output/figures/ before the link-resolution gate runs.

    Required for
    test_standalone.py::test_every_relative_markdown_link_points_at_a_file_that_exists,
    which checks that output/figures/*.png embeds in manuscript/ resolve. The
    output/ directory is gitignored; a fresh clone must build before testing.
    """

    root = Path(__file__).resolve().parents[1]
    build_script = root / "scripts" / "build_figures.py"
    if not build_script.exists():
        return
    result = subprocess.run(
        [sys.executable, str(build_script)],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        warnings.warn(
            f"build_figures.py exited {result.returncode}: {result.stderr[:200]}",
            stacklevel=1,
        )


def make_payload(**overrides) -> dict:
    """A valid published-shape envelope payload, with per-test overrides."""

    payload = {
        "schema_version": ENVELOPE_SCHEMA,
        "line_id": "black_line",
        "subject_id": "subject-1",
        "review_date": "2026-07-29",
        "registry_version": "2.0.0",
        "registry_digest": sha256_hex("registry"),
        "native_status": {"verdict": "STRONG_YES", "detail": ["opaque", 3]},
        "report_ref": sha256_hex("report"),
        "source_snapshot_refs": ["git:abc123", "doc:intake-note"],
        "scope_and_nonclaims": [
            "asserts nothing beyond its own native report",
            "not a moral authority",
        ],
    }
    payload.update(overrides)
    return payload


def accept(payload: dict) -> EnvelopeRecord:
    """Intake a payload that must be accepted, failing the test otherwise."""

    record, issues = intake_envelope(payload)
    assert record is not None, issues
    assert issues == ()
    return record


@pytest.fixture
def envelope() -> EnvelopeRecord:
    return accept(make_payload())


@pytest.fixture
def second_envelope() -> EnvelopeRecord:
    return accept(make_payload(line_id="white_line", report_ref=sha256_hex("report-2")))


def make_relation(
    envelope: EnvelopeRecord,
    relation_type: RelationType = RelationType.AGREES,
    relation_id: str = "rel-1",
    **overrides,
) -> RelationRecord:
    fields = {
        "relation_id": relation_id,
        "subject_id": "subject-1",
        "source_report_refs": (envelope.report_ref,),
        "relation_type": relation_type,
        "bounded_description": "a bounded description of the relation",
    }
    fields.update(overrides)
    return RelationRecord(**fields)


def make_contract(contract_id: str = "con-1", **overrides) -> ReturnContractRecord:
    fields = {
        "contract_id": contract_id,
        "subject_id": "subject-1",
        "why_held": "held pending a dated re-observation",
        "alternatives_live": ("wait for the return",),
        "change_condition": "a dated observation answering the hold",
        "standing": "the exporting line's maintainer",
        "protected": "nothing in this case",
        "trigger": "the review horizon lapses",
        "acceptance_condition": "a dated record enters the register",
    }
    fields.update(overrides)
    return ReturnContractRecord(**fields)


def make_holding(held_id: str = "held-1", **overrides) -> UnclassifiedHeld:
    fields = {
        "held_id": held_id,
        "raw_observation": "an input that fits no current category",
        "provenance": "test intake sweep",
        "candidate_relations": ("DIRECTIONAL_TENSION",),
        "reason_unclassified": "no current category fits without forcing",
        "review_moment": "2026-07-29",
    }
    fields.update(overrides)
    return UnclassifiedHeld(**fields)
