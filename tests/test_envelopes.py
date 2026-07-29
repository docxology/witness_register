"""Intake acceptance and every typed rejection path."""

from __future__ import annotations

from conftest import accept, make_payload

from witness_register import (
    ENVELOPE_SCHEMA,
    IssueCode,
    REQUIRED_FIELDS,
    intake_envelope,
)


def test_a_valid_payload_is_accepted_verbatim() -> None:
    payload = make_payload()
    record = accept(payload)
    assert record.schema_version == ENVELOPE_SCHEMA
    assert record.line_id == "black_line"
    assert record.subject_id == "subject-1"
    assert record.review_date == "2026-07-29"
    assert record.registry_version == "2.0.0"
    assert record.native_status == payload["native_status"]
    assert record.source_snapshot_refs == tuple(payload["source_snapshot_refs"])
    assert record.scope_and_nonclaims == tuple(payload["scope_and_nonclaims"])


def test_native_status_is_stored_verbatim_not_normalized() -> None:
    """The register never interprets native vocabulary — any JSON shape rides."""

    for native in (
        "STRONG_YES",
        [["r1", "NAMED"], ["r2", "WITHHELD"]],
        {"nested": {"deep": [1, 2.5, None, True]}},
        None,
        42,
    ):
        record = accept(make_payload(native_status=native))
        assert record.native_status == native


def test_non_dict_payload_is_refused_with_a_typed_issue() -> None:
    record, issues = intake_envelope("not a dict")  # type: ignore[arg-type]
    assert record is None
    assert [issue.code for issue in issues] == [IssueCode.MALFORMED_FIELD]
    assert issues[0].field == ""


def test_every_missing_field_is_named() -> None:
    record, issues = intake_envelope({})
    assert record is None
    assert {issue.field for issue in issues} == set(REQUIRED_FIELDS)
    assert all(issue.code is IssueCode.MISSING_FIELD for issue in issues)


def test_one_missing_field_is_the_only_issue_reported() -> None:
    payload = make_payload()
    del payload["report_ref"]
    record, issues = intake_envelope(payload)
    assert record is None
    assert [(issue.code, issue.field) for issue in issues] == [
        (IssueCode.MISSING_FIELD, "report_ref")
    ]


def test_wrong_schema_string_is_refused() -> None:
    record, issues = intake_envelope(
        make_payload(schema_version="line.report-envelope/2.0")
    )
    assert record is None
    assert [issue.code for issue in issues] == [IssueCode.WRONG_SCHEMA]


def test_blank_line_id_is_refused() -> None:
    for bad in ("", "   ", 7):
        record, issues = intake_envelope(make_payload(line_id=bad))
        assert record is None
        assert issues[0].code is IssueCode.MALFORMED_FIELD
        assert issues[0].field == "line_id"


def test_non_string_subject_id_is_refused_but_empty_is_allowed() -> None:
    record, issues = intake_envelope(make_payload(subject_id=17))
    assert record is None
    assert issues[0].field == "subject_id"
    assert accept(make_payload(subject_id="")).subject_id == ""


def test_review_date_must_be_a_real_iso_calendar_date() -> None:
    for bad in ("2026-7-29", "20260729", "2026-13-01", "2026-02-30", "yesterday", 5):
        record, issues = intake_envelope(make_payload(review_date=bad))
        assert record is None, bad
        assert issues[0].field == "review_date"
        assert issues[0].code is IssueCode.MALFORMED_FIELD


def test_non_string_registry_version_is_refused() -> None:
    record, issues = intake_envelope(make_payload(registry_version=2))
    assert record is None
    assert issues[0].field == "registry_version"


def test_digest_fields_must_be_64_lowercase_hex() -> None:
    for field in ("registry_digest", "report_ref"):
        for bad in ("abc", "G" * 64, ("A" * 64), 12, "a" * 63):
            record, issues = intake_envelope(make_payload(**{field: bad}))
            assert record is None, (field, bad)
            assert issues[0].field == field


def test_non_json_native_status_is_refused() -> None:
    record, issues = intake_envelope(make_payload(native_status={1, 2}))
    assert record is None
    assert issues[0].field == "native_status"
    assert "verbatim" in issues[0].message


def test_snapshot_refs_must_be_a_sequence_of_non_blank_strings() -> None:
    record, issues = intake_envelope(make_payload(source_snapshot_refs="git:abc"))
    assert record is None
    assert issues[0].field == "source_snapshot_refs"

    record, issues = intake_envelope(make_payload(source_snapshot_refs=["ok", "  "]))
    assert record is None
    assert issues[0].field == "source_snapshot_refs"

    assert accept(make_payload(source_snapshot_refs=[])).source_snapshot_refs == ()


def test_empty_nonclaims_is_its_own_code() -> None:
    record, issues = intake_envelope(make_payload(scope_and_nonclaims=[]))
    assert record is None
    assert IssueCode.EMPTY_NONCLAIMS in {issue.code for issue in issues}


def test_blank_nonclaim_entries_are_malformed_not_empty() -> None:
    record, issues = intake_envelope(make_payload(scope_and_nonclaims=["", "x"]))
    assert record is None
    codes = {issue.code for issue in issues}
    assert IssueCode.MALFORMED_FIELD in codes
    assert IssueCode.EMPTY_NONCLAIMS not in codes


def test_multiple_defects_are_all_reported_not_only_the_first() -> None:
    record, issues = intake_envelope(
        make_payload(line_id="", review_date="not-a-date", report_ref="short")
    )
    assert record is None
    assert {issue.field for issue in issues} == {
        "line_id",
        "review_date",
        "report_ref",
    }


def test_every_stored_export_carries_the_identical_sorted_key_set() -> None:
    """Cross-exporter consistency, checked over the stored corpus.

    All five repositories serialize the envelope with sorted keys by
    convention; this test reads every envelope actually stored under
    ``data/envelopes/`` and requires one identical ten-key set, serialized
    in sorted order. A sibling exporter drifting its field roster or its
    serialization order fails here the next time its export is stored.
    """

    import json
    import re
    from pathlib import Path

    from witness_register import REQUIRED_FIELDS

    base = Path(__file__).resolve().parents[1] / "data" / "envelopes"
    files = sorted(base.glob("*.json")) + sorted((base / "same_subject").glob("*.json"))
    assert len(files) >= 8, "the stored corpus shrank; this gate would go vacuous"
    for path in files:
        raw = path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        assert set(payload) == set(REQUIRED_FIELDS), path.name
        serialized_order = re.findall(r'"(\w+)":', raw)
        top_level = [key for key in serialized_order if key in REQUIRED_FIELDS]
        deduped = list(dict.fromkeys(top_level))
        assert deduped == sorted(REQUIRED_FIELDS), path.name
