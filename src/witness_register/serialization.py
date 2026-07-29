"""Canonical JSON and SHA-256 for every register record and the state.

The digests here are change-review and drift-detection aids for the
register's own bookkeeping: they let a stored state be compared against a
later checkout so silent edits surface during review. They carry no security
or safety semantics, and — like everything in this package — they say nothing
about the truth of any line's report.

Schema identifiers are namespaced per payload shape under
``witness-register.<thing>/1.0`` so a stored JSON document names exactly
which shape it is. The one exception is the envelope INTAKE shape, which is
the lines' own published ``line.report-envelope/1.0`` and is declared in
:mod:`witness_register.envelopes`.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .envelopes import EnvelopeRecord
from .held import UnclassifiedHeld
from .relations import RelationRecord
from .returns import ReturnContractRecord

ENVELOPE_RECORD_SCHEMA = "witness-register.envelope-record/1.0"
RELATION_SCHEMA = "witness-register.relation/1.0"
RETURN_CONTRACT_SCHEMA = "witness-register.return-contract/1.0"
UNCLASSIFIED_SCHEMA = "witness-register.unclassified/1.0"
STATE_SCHEMA = "witness-register.state/1.0"
PROJECTION_SCHEMA = "witness-register.projection/1.0"


def canonical_json(payload: Any) -> str:
    """Compact, key-sorted, non-ASCII-preserving JSON.

    Two equal payloads produce byte-identical output regardless of the key
    order they were built in, which is what makes a digest over this text a
    statement about content rather than construction order.

    Strict JSON only: ``NaN`` and ``Infinity`` raise instead of being
    emitted. Python's ``json`` would otherwise write them as bare literals
    no strict JSON parser accepts, and a digest over text that is not JSON
    would launder a non-interchangeable value into a sealed state.
    """

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_hex(text: str) -> str:
    """SHA-256 of UTF-8 text as 64 lowercase hex characters."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def payload_digest(payload: Any) -> str:
    """SHA-256 over the canonical JSON of *payload*."""

    return sha256_hex(canonical_json(payload))


def canonical_envelope(record: EnvelopeRecord) -> dict:
    """The stored form of an accepted envelope, verbatim fields included."""

    return {
        "record_schema": ENVELOPE_RECORD_SCHEMA,
        "schema_version": record.schema_version,
        "line_id": record.line_id,
        "subject_id": record.subject_id,
        "review_date": record.review_date,
        "registry_version": record.registry_version,
        "registry_digest": record.registry_digest,
        "native_status": record.native_status,
        "report_ref": record.report_ref,
        "source_snapshot_refs": list(record.source_snapshot_refs),
        "scope_and_nonclaims": list(record.scope_and_nonclaims),
    }


def canonical_relation(record: RelationRecord) -> dict:
    """The stored form of a relation record."""

    return {
        "record_schema": RELATION_SCHEMA,
        "relation_id": record.relation_id,
        "subject_id": record.subject_id,
        "source_report_refs": list(record.source_report_refs),
        "relation_type": record.relation_type.value,
        "bounded_description": record.bounded_description,
        "support_refs": list(record.support_refs),
        "resistance_refs": list(record.resistance_refs),
        "protected_boundary_refs": list(record.protected_boundary_refs),
        "return_contract_ref": record.return_contract_ref,
        "human_decision_ref": record.human_decision_ref,
        "promoted_from_ref": record.promoted_from_ref,
    }


def canonical_return_contract(record: ReturnContractRecord) -> dict:
    """The stored form of a return contract record."""

    return {
        "record_schema": RETURN_CONTRACT_SCHEMA,
        "contract_id": record.contract_id,
        "subject_id": record.subject_id,
        "why_held": record.why_held,
        "alternatives_live": list(record.alternatives_live),
        "change_condition": record.change_condition,
        "standing": record.standing,
        "protected": record.protected,
        "trigger": record.trigger,
        "acceptance_condition": record.acceptance_condition,
        "verification_result": record.verification_result,
        "open_remainder": record.open_remainder,
        "prior_state_ref": record.prior_state_ref,
    }


def canonical_unclassified(record: UnclassifiedHeld) -> dict:
    """The stored form of an unclassified holding."""

    return {
        "record_schema": UNCLASSIFIED_SCHEMA,
        "held_id": record.held_id,
        "raw_observation": record.raw_observation,
        "provenance": record.provenance,
        "candidate_relations": list(record.candidate_relations),
        "reason_unclassified": record.reason_unclassified,
        "review_moment": record.review_moment,
    }


def envelope_digest(record: EnvelopeRecord) -> str:
    """SHA-256 over the canonical form of an envelope record."""

    return payload_digest(canonical_envelope(record))


def relation_digest(record: RelationRecord) -> str:
    """SHA-256 over the canonical form of a relation record."""

    return payload_digest(canonical_relation(record))


def return_contract_digest(record: ReturnContractRecord) -> str:
    """SHA-256 over the canonical form of a return contract record."""

    return payload_digest(canonical_return_contract(record))


def unclassified_digest(record: UnclassifiedHeld) -> str:
    """SHA-256 over the canonical form of an unclassified holding."""

    return payload_digest(canonical_unclassified(record))


def canonical_state_payload(
    subject_id: str,
    review_moment: str,
    envelopes: tuple[EnvelopeRecord, ...],
    relations: tuple[RelationRecord, ...],
    unclassified: tuple[UnclassifiedHeld, ...],
    returns: tuple[ReturnContractRecord, ...],
    prior_ref: str,
) -> dict:
    """The complete canonical content of one witness state, pre-seal.

    Record ORDER is part of the content: an append-only chain's guarantee is
    that prior records stay in place unchanged, so the payload lists them in
    stored order rather than re-sorting, and the digest binds that order.
    """

    return {
        "record_schema": STATE_SCHEMA,
        "subject_id": subject_id,
        "review_moment": review_moment,
        "envelopes": [canonical_envelope(item) for item in envelopes],
        "relations": [canonical_relation(item) for item in relations],
        "unclassified": [canonical_unclassified(item) for item in unclassified],
        "returns": [canonical_return_contract(item) for item in returns],
        "prior_ref": prior_ref,
    }
