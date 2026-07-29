"""witness_register — co-registration without aggregation.

The Shared Witness Register sits BESIDE the line set. It is not a line: it
has no colour, no substantive question of its own, and no verdict. It
accepts each line's published report envelope by value, stores it verbatim,
records cross-line relations as separate records, keeps history append-only,
and — when explicitly asked, for one declared next use — emits a bounded
posture that always points back at the state that earned it. Precedence
without information destruction; no crown without return.

The register's own non-claims, stated once and enforced in code and tests:

- It NEVER imports any line package. Envelopes arrive by value under the
  published schema string ``line.report-envelope/1.0``; the string is
  aligned across repositories by convention, not by import.
- It NEVER parses, compares, ranks, averages, merges, or otherwise
  interprets any line's ``native_status``. The exporting line remains
  authoritative about its own vocabulary; a projection is driven only by
  typed relation records.
- It NEVER auto-creates a category. An input that fits nothing is held
  raw, and promotion requires a non-empty human decision reference.
- It NEVER infers consent or permission. A protected absence forbids the
  favorable posture; an empty register is refusal, not permission.
- It NEVER mutates or rewrites history. Updates append; tampering is
  refused fail-closed; completed returns close only their verified part.
- It NEVER emits any score other than the bounded posture ``-1 | 0 | +1``,
  and never emits that without a declared next use, a state reference, and
  reasons. The symbols are interface values, not the ontology.

Known limitation, stated rather than solved: an append-only chain's tip is
unbound without EXTERNAL anchoring. ``seal_tip`` hands you the value to
anchor elsewhere; nothing inside the chain can notice a discarded tip.
"""

from __future__ import annotations

from .battery import CASE_IDS, BatteryError, CaseCheck, run_battery
from .envelopes import (
    ENVELOPE_SCHEMA,
    EnvelopeRecord,
    HEX_DIGEST_RE,
    IntakeIssue,
    IssueCode,
    REQUIRED_FIELDS,
    intake_envelope,
)
from .held import UnclassifiedHeld
from .invariants import (
    InvariantDefeatError,
    check_chain,
    check_digest_shapes,
    check_distinct_ids,
    check_projection,
    check_refs_resolve,
    check_seal,
    check_state,
    defect_battery,
)
from .metrics import (
    MEASUREMENT_PROBE_USE,
    premature_crowning_rate,
    relation_fidelity,
    return_recoverability,
)
from .projection import HoldReason, Projection, project, witness_hold_reasons
from .relations import NOT_RECORDED, RelationRecord, RelationType
from .returns import ReturnContractRecord, record_return
from .serialization import (
    ENVELOPE_RECORD_SCHEMA,
    PROJECTION_SCHEMA,
    RELATION_SCHEMA,
    RETURN_CONTRACT_SCHEMA,
    STATE_SCHEMA,
    UNCLASSIFIED_SCHEMA,
    canonical_envelope,
    canonical_json,
    canonical_relation,
    canonical_return_contract,
    canonical_state_payload,
    canonical_unclassified,
    envelope_digest,
    payload_digest,
    relation_digest,
    return_contract_digest,
    sha256_hex,
    unclassified_digest,
)
from .state import (
    ANCHOR_STATEMENT_SCHEMA,
    WitnessState,
    anchor_statement,
    genesis_state,
    promote_unclassified,
    seal_tip,
    state_content_digest,
    update_state,
    verify_chain,
)
from .version import __version__

__all__ = [
    "ANCHOR_STATEMENT_SCHEMA",
    "BatteryError",
    "CASE_IDS",
    "CaseCheck",
    "ENVELOPE_RECORD_SCHEMA",
    "ENVELOPE_SCHEMA",
    "EnvelopeRecord",
    "HEX_DIGEST_RE",
    "HoldReason",
    "IntakeIssue",
    "InvariantDefeatError",
    "IssueCode",
    "MEASUREMENT_PROBE_USE",
    "NOT_RECORDED",
    "PROJECTION_SCHEMA",
    "Projection",
    "RELATION_SCHEMA",
    "REQUIRED_FIELDS",
    "RETURN_CONTRACT_SCHEMA",
    "RelationRecord",
    "RelationType",
    "ReturnContractRecord",
    "STATE_SCHEMA",
    "UNCLASSIFIED_SCHEMA",
    "UnclassifiedHeld",
    "WitnessState",
    "__version__",
    "anchor_statement",
    "canonical_envelope",
    "canonical_json",
    "canonical_relation",
    "canonical_return_contract",
    "canonical_state_payload",
    "canonical_unclassified",
    "check_chain",
    "check_digest_shapes",
    "check_distinct_ids",
    "check_projection",
    "check_refs_resolve",
    "check_seal",
    "check_state",
    "defect_battery",
    "envelope_digest",
    "genesis_state",
    "intake_envelope",
    "payload_digest",
    "premature_crowning_rate",
    "project",
    "promote_unclassified",
    "record_return",
    "relation_digest",
    "relation_fidelity",
    "return_contract_digest",
    "return_recoverability",
    "run_battery",
    "seal_tip",
    "sha256_hex",
    "state_content_digest",
    "unclassified_digest",
    "update_state",
    "verify_chain",
    "witness_hold_reasons",
]
