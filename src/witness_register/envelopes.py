"""Typed intake of a line's common report envelope, by value.

Each line in the set exports one envelope under the published schema string
``line.report-envelope/1.0``: a pointer to its complete native report, its
identity, its subject, its review date, its registry provenance, its native
status in its OWN vocabulary, and its non-claims. This module is the
register's side of that contract. It accepts the envelope BY VALUE — the
schema string is aligned across repositories by published convention, never
by import — and stores what it accepted verbatim.

Non-claims of this module:

- Accepting an envelope asserts NOTHING about the truth of its report. Intake
  is a shape check, not a review.
- ``native_status`` is opaque here. The register never parses, compares,
  ranks, merges, or otherwise interprets it; it is carried so a reader can
  return to the exporting line, which remains authoritative about its own
  vocabulary.
- Rejection is typed and total: nothing is rejected silently, and a rejected
  payload leaves a trail of :class:`IntakeIssue` records naming every defect
  found, not only the first.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

#: The cross-instrument envelope shape this register accepts. Declared as this
#: repository's own literal; sibling repositories publish the same string by
#: convention, never by import.
ENVELOPE_SCHEMA = "line.report-envelope/1.0"

#: A SHA-256 digest as the lines publish it: 64 lowercase hex characters.
HEX_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")

#: Exact calendar-date shape; ``date.fromisoformat`` alone accepts more.
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

#: Every field a ``line.report-envelope/1.0`` payload must carry.
REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "line_id",
    "subject_id",
    "review_date",
    "registry_version",
    "registry_digest",
    "native_status",
    "report_ref",
    "source_snapshot_refs",
    "scope_and_nonclaims",
)


class IssueCode(str, Enum):
    """Why an intake refused a payload. Every refusal carries one of these."""

    WRONG_SCHEMA = "WRONG_SCHEMA"
    MISSING_FIELD = "MISSING_FIELD"
    MALFORMED_FIELD = "MALFORMED_FIELD"
    EMPTY_NONCLAIMS = "EMPTY_NONCLAIMS"


@dataclass(frozen=True)
class IntakeIssue:
    """One typed reason an envelope payload was not accepted.

    ``field`` names the offending payload key so the exporting side can fix
    exactly what failed; it is empty only for payload-level defects such as a
    non-dict payload.
    """

    code: IssueCode
    message: str
    field: str


@dataclass(frozen=True)
class EnvelopeRecord:
    """One accepted envelope, held verbatim.

    ``report_ref`` is the exporting line's SHA-256 pointer to its complete
    canonical native report; the register stores the pointer and never
    dereferences or re-derives it. ``native_status`` is whatever
    JSON-compatible value the line exported, unchanged — for one line that is
    an ordered per-record state list, for another a single verdict string;
    the register treats both as opaque. Holding this record asserts only
    that the payload had the published shape, never that its report is true.
    """

    schema_version: str
    line_id: str
    subject_id: str
    review_date: str
    registry_version: str
    registry_digest: str
    native_status: Any
    report_ref: str
    source_snapshot_refs: tuple[str, ...]
    scope_and_nonclaims: tuple[str, ...]


def _string_tuple(
    value: object, field: str, issues: list[IntakeIssue]
) -> tuple[str, ...]:
    """Coerce a list/tuple of non-blank strings, recording every defect."""

    if not isinstance(value, (list, tuple)):
        issues.append(
            IntakeIssue(
                IssueCode.MALFORMED_FIELD,
                f"{field} must be a list or tuple of strings, got "
                f"{type(value).__name__}",
                field,
            )
        )
        return ()
    items: list[str] = []
    for position, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            issues.append(
                IntakeIssue(
                    IssueCode.MALFORMED_FIELD,
                    f"{field}[{position}] must be a non-blank string",
                    field,
                )
            )
        else:
            items.append(item)
    return tuple(items)


def _valid_review_date(value: str) -> bool:
    """Exact ``YYYY-MM-DD`` and a real calendar date."""

    if not ISO_DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def intake_envelope(
    payload: dict,
) -> tuple[EnvelopeRecord | None, tuple[IntakeIssue, ...]]:
    """Validate one envelope payload; accept it verbatim or refuse it typed.

    Returns ``(record, ())`` on acceptance and ``(None, issues)`` on refusal,
    where ``issues`` names every defect found — never only the first, and
    never silently. Acceptance asserts nothing about the truth of the
    referenced report; it asserts only that the payload had the published
    ``line.report-envelope/1.0`` shape.
    """

    issues: list[IntakeIssue] = []
    if not isinstance(payload, dict):
        return None, (
            IntakeIssue(
                IssueCode.MALFORMED_FIELD,
                f"envelope payload must be a dict, got {type(payload).__name__}",
                "",
            ),
        )

    for field in REQUIRED_FIELDS:
        if field not in payload:
            issues.append(
                IntakeIssue(IssueCode.MISSING_FIELD, f"{field} is required", field)
            )
    if issues:
        return None, tuple(issues)

    schema_version = payload["schema_version"]
    if schema_version != ENVELOPE_SCHEMA:
        issues.append(
            IntakeIssue(
                IssueCode.WRONG_SCHEMA,
                f"schema_version must be {ENVELOPE_SCHEMA!r}, got {schema_version!r}",
                "schema_version",
            )
        )

    line_id = payload["line_id"]
    if not isinstance(line_id, str) or not line_id.strip():
        issues.append(
            IntakeIssue(
                IssueCode.MALFORMED_FIELD,
                "line_id must be a non-blank string",
                "line_id",
            )
        )

    subject_id = payload["subject_id"]
    if not isinstance(subject_id, str):
        issues.append(
            IntakeIssue(
                IssueCode.MALFORMED_FIELD,
                "subject_id must be a string",
                "subject_id",
            )
        )

    review_date = payload["review_date"]
    if not isinstance(review_date, str) or not _valid_review_date(review_date):
        issues.append(
            IntakeIssue(
                IssueCode.MALFORMED_FIELD,
                "review_date must be an ISO YYYY-MM-DD calendar date",
                "review_date",
            )
        )

    registry_version = payload["registry_version"]
    if not isinstance(registry_version, str):
        issues.append(
            IntakeIssue(
                IssueCode.MALFORMED_FIELD,
                "registry_version must be a string",
                "registry_version",
            )
        )

    for field in ("registry_digest", "report_ref"):
        value = payload[field]
        if not isinstance(value, str) or not HEX_DIGEST_RE.match(value):
            issues.append(
                IntakeIssue(
                    IssueCode.MALFORMED_FIELD,
                    f"{field} must be 64 lowercase hex characters",
                    field,
                )
            )

    native_status = payload["native_status"]
    try:
        json.dumps(native_status, ensure_ascii=False, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError):
        issues.append(
            IntakeIssue(
                IssueCode.MALFORMED_FIELD,
                "native_status must be strict-JSON-compatible data (no NaN "
                "or Infinity); the register stores it verbatim and never "
                "interprets it",
                "native_status",
            )
        )

    source_snapshot_refs = _string_tuple(
        payload["source_snapshot_refs"], "source_snapshot_refs", issues
    )
    scope_and_nonclaims = _string_tuple(
        payload["scope_and_nonclaims"], "scope_and_nonclaims", issues
    )
    if (
        isinstance(payload["scope_and_nonclaims"], (list, tuple))
        and not payload["scope_and_nonclaims"]
    ):
        issues.append(
            IntakeIssue(
                IssueCode.EMPTY_NONCLAIMS,
                "scope_and_nonclaims must carry at least one non-claim; an "
                "envelope without its instrument's boundary can quietly "
                "outgrow what the instrument was allowed to say",
                "scope_and_nonclaims",
            )
        )

    if issues:
        return None, tuple(issues)

    record = EnvelopeRecord(
        schema_version=schema_version,
        line_id=line_id,
        subject_id=subject_id,
        review_date=review_date,
        registry_version=registry_version,
        registry_digest=payload["registry_digest"],
        native_status=native_status,
        report_ref=payload["report_ref"],
        source_snapshot_refs=source_snapshot_refs,
        scope_and_nonclaims=scope_and_nonclaims,
    )
    return record, ()
