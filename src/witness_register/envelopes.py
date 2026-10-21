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

from copy import deepcopy

from .json_data import json_domain_issues
from .json_data import MAX_JSON_NODES
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
HEX_DIGEST_RE = re.compile(r"^[0-9a-f]{64}\Z")

#: Exact calendar-date shape; ``date.fromisoformat`` alone accepts more.
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\Z")

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
    if len(value) > MAX_JSON_NODES:
        issues.append(
            IntakeIssue(
                IssueCode.MALFORMED_FIELD, f"{field}: JSON node limit exceeded", field
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


def valid_calendar_date(value: str) -> bool:
    """Exact ``YYYY-MM-DD`` and a real calendar date."""

    if not isinstance(value, str) or not ISO_DATE_RE.fullmatch(value):
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
            continue
        value = payload[field]
        if field == "schema_version":
            if value != ENVELOPE_SCHEMA:
                issues.append(
                    IntakeIssue(
                        IssueCode.WRONG_SCHEMA,
                        f"schema_version must be {ENVELOPE_SCHEMA!r}",
                        field,
                    )
                )
        elif field == "line_id":
            if not isinstance(value, str) or not value.strip():
                issues.append(
                    IntakeIssue(
                        IssueCode.MALFORMED_FIELD,
                        "line_id must be a non-blank string",
                        field,
                    )
                )
        elif field in ("subject_id", "registry_version"):
            if not isinstance(value, str):
                issues.append(
                    IntakeIssue(
                        IssueCode.MALFORMED_FIELD, f"{field} must be a string", field
                    )
                )
        elif field == "review_date":
            if not valid_calendar_date(value):
                issues.append(
                    IntakeIssue(
                        IssueCode.MALFORMED_FIELD,
                        "review_date must be an ISO YYYY-MM-DD calendar date",
                        field,
                    )
                )
        elif field in ("registry_digest", "report_ref"):
            if not isinstance(value, str) or not HEX_DIGEST_RE.fullmatch(value):
                issues.append(
                    IntakeIssue(
                        IssueCode.MALFORMED_FIELD,
                        f"{field} must be 64 lowercase hex characters",
                        field,
                    )
                )
        elif field == "native_status":
            for message in json_domain_issues(value):
                issues.append(
                    IntakeIssue(
                        IssueCode.MALFORMED_FIELD,
                        message
                        + "; native_status is stored verbatim, never coerced or interpreted",
                        field,
                    )
                )
        else:
            _string_tuple(value, field, issues)
            if (
                field == "scope_and_nonclaims"
                and isinstance(value, (list, tuple))
                and not value
            ):
                issues.append(
                    IntakeIssue(
                        IssueCode.EMPTY_NONCLAIMS,
                        "scope_and_nonclaims must carry at least one non-claim",
                        field,
                    )
                )
        if isinstance(value, str) and field != "native_status":
            for message in json_domain_issues(value):
                issues.append(IntakeIssue(IssueCode.MALFORMED_FIELD, message, field))
        elif field in ("source_snapshot_refs", "scope_and_nonclaims") and isinstance(
            value, (list, tuple)
        ):
            for message in json_domain_issues(list(value)):
                issues.append(IntakeIssue(IssueCode.MALFORMED_FIELD, message, field))
    if issues:
        return None, tuple(issues)
    return EnvelopeRecord(
        schema_version=payload["schema_version"],
        line_id=payload["line_id"],
        subject_id=payload["subject_id"],
        review_date=payload["review_date"],
        registry_version=payload["registry_version"],
        registry_digest=payload["registry_digest"],
        native_status=deepcopy(payload["native_status"]),
        report_ref=payload["report_ref"],
        source_snapshot_refs=tuple(payload["source_snapshot_refs"]),
        scope_and_nonclaims=tuple(payload["scope_and_nonclaims"]),
    ), ()
