"""Dependency-neutral bookkeeping validation; defects are not subject verdicts."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from .decisions import DecisionKind, TargetKind
from .envelopes import HEX_DIGEST_RE, valid_calendar_date, intake_envelope
from .relations import RelationType
from .returns import ReturnContractRecord
from .serialization import (
    canonical_state_payload,
    payload_digest,
    relation_digest,
    return_contract_digest,
    canonical_envelope,
)

if TYPE_CHECKING:
    from .state import WitnessState


@dataclass(frozen=True)
class StructuralIssue:
    """Named bookkeeping defect, retained beside inspectable raw state."""

    code: str
    ref: str
    message: str


class InvalidStateError(ValueError):
    """All structural issues; raising this emits no substantive posture."""

    def __init__(self, issues: tuple[StructuralIssue, ...]) -> None:
        self.issues = issues
        super().__init__(
            "invalid state structure: " + "; ".join(i.message for i in issues)
        )


def check_distinct_ids(state: WitnessState) -> tuple[str, ...]:
    """Distinct identities, with only an immutable open/completed return pair."""

    errors: list[str] = []
    for record in state.returns:
        for term in fields(ReturnContractRecord):
            value = getattr(record, term.name)
            if term.name == "alternatives_live":
                if type(value) is not tuple or any(
                    type(item) is not str for item in value
                ):
                    errors.append(
                        f"contract {record.contract_id}: alternatives_live must be a tuple of strings"
                    )
            elif type(value) is not str:
                errors.append(
                    f"contract {record.contract_id}: {term.name} must be a string"
                )
    for kind, field in (
        ("envelopes", "report_ref"),
        ("relations", "relation_id"),
        ("unclassified", "held_id"),
        ("decisions", "decision_id"),
    ):
        counts = Counter(getattr(item, field) for item in getattr(state, kind))
        errors.extend(
            f"duplicate {field} {key}" for key in sorted(counts) if counts[key] > 1
        )
    by_id: dict[str, list[ReturnContractRecord]] = {}
    for record in state.returns:
        by_id.setdefault(record.contract_id, []).append(record)
    immutable = tuple(
        f.name
        for f in fields(ReturnContractRecord)
        if f.name not in ("verification_result", "open_remainder")
    )
    for ref, records in by_id.items():
        opened = [r for r in records if not r.verification_result]
        completed = [r for r in records if r.verification_result]
        if len(opened) != 1 or len(completed) > 1:
            errors.append(
                f"contract {ref}: requires one open predecessor and at most one completed record"
            )
        elif completed:
            original, done = opened[0], completed[0]
            if records.index(original) > records.index(done):
                errors.append(
                    f"contract {ref}: completion precedes its open predecessor"
                )
            changed = [
                name
                for name in immutable
                if getattr(original, name) != getattr(done, name)
            ]
            if changed:
                errors.append(
                    f"contract {ref}: completed record must keep every immutable field "
                    f"(including why_held and trigger); changed {', '.join(changed)}"
                )
        for record in opened:
            if record.open_remainder:
                errors.append(
                    f"contract {ref}: an open record cannot claim a returned remainder"
                )
    return tuple(errors)


def check_digest_shapes(state: WitnessState) -> tuple[str, ...]:
    """Exact digest lexing, including every event and ancestry reference."""

    errors: list[str] = []

    def digest(value: str, name: str, optional: bool = False) -> None:
        if optional and value == "":
            return
        if not isinstance(value, str) or not HEX_DIGEST_RE.fullmatch(value):
            errors.append(f"{name} {value!r} is not 64 lowercase hex")

    digest(state.state_digest, "state_digest")
    digest(state.prior_ref, "prior_ref", True)
    for ref in state.history_refs:
        digest(ref, "history_refs")
    for envelope in state.envelopes:
        for field in ("registry_digest", "report_ref"):
            digest(getattr(envelope, field), f"envelope {envelope.line_id}: {field}")
    for relation in state.relations:
        for field in ("source_report_refs", "support_refs", "resistance_refs"):
            for ref in getattr(relation, field):
                digest(ref, f"relation {relation.relation_id}: {field}")
    for contract in state.returns:
        digest(
            contract.prior_state_ref,
            f"contract {contract.contract_id}: prior_state_ref",
            True,
        )
        digest(
            contract.parent_return_ref,
            f"contract {contract.contract_id}: parent_return_ref",
            True,
        )
    for event in state.decisions:
        digest(event.target_ref, f"decision {event.decision_id}: target_ref")
        digest(event.basis_state_ref, f"decision {event.decision_id}: basis_state_ref")
    return tuple(errors)


def check_refs_resolve(state: WitnessState) -> tuple[str, ...]:
    """Record references resolve locally; history context is separately replayed."""

    errors: list[str] = []
    envelopes = {e.report_ref for e in state.envelopes}
    contracts = {r.contract_id for r in state.returns if not r.verification_result}
    held = {h.held_id for h in state.unclassified}
    relations = {}
    for relation in state.relations:
        try:
            relations[relation_digest(relation)] = relation
        except (ValueError, TypeError) as exc:
            errors.append(
                f"relation {relation.relation_id}: cannot form a strict JSON target: {exc}"
            )
    obligations = {}
    partials = {}
    for record in state.returns:
        try:
            digest = return_contract_digest(record)
        except (ValueError, TypeError) as exc:
            errors.append(
                f"contract {record.contract_id}: cannot form a strict JSON target: {exc}"
            )
            continue
        if not record.verification_result:
            obligations[digest] = record
        elif record.open_remainder:
            partials[digest] = record
    for relation in state.relations:
        for field in ("source_report_refs", "support_refs", "resistance_refs"):
            for ref in getattr(relation, field):
                if ref not in envelopes:
                    errors.append(
                        f"relation {relation.relation_id}: {field} entry {ref} "
                        "does not resolve to a co-registered envelope"
                    )
        if (
            relation.relation_type is RelationType.RETURN_DUE
            and relation.return_contract_ref not in contracts
        ):
            errors.append(
                f"relation {relation.relation_id}: RETURN_DUE contract does not resolve"
            )
        if relation.promoted_from_ref:
            if relation.promoted_from_ref not in held:
                errors.append(
                    f"relation {relation.relation_id}: promoted_from_ref does not resolve"
                )
            if not relation.classification_decision_ref.strip():
                errors.append(
                    f"relation {relation.relation_id}: promotion requires classification_decision_ref "
                    "(human_decision_ref alone is not classification authority)"
                )
    child_refs: list[str] = []
    for record in state.returns:
        if record.prior_state_ref and record.prior_state_ref not in state.history_refs:
            errors.append(
                f"contract {record.contract_id}: prior_state_ref is not in declared chain context"
            )
        if record.verification_result or not record.parent_return_ref:
            continue
        child_refs.append(record.parent_return_ref)
        parent = partials.get(record.parent_return_ref)
        if parent is None:
            errors.append(
                f"contract {record.contract_id}: parent_return_ref does not resolve to a partial return"
            )
            continue
        if state.returns.index(parent) >= state.returns.index(record):
            errors.append(
                f"contract {record.contract_id}: remainder must follow its partial return"
            )
        for field in (
            "subject_id",
            "alternatives_live",
            "change_condition",
            "standing",
            "protected",
            "trigger",
        ):
            if getattr(record, field) != getattr(parent, field):
                errors.append(
                    f"contract {record.contract_id}: remainder changed {field}"
                )
        if (
            record.why_held != parent.open_remainder
            or record.acceptance_condition != parent.open_remainder
        ):
            errors.append(
                f"contract {record.contract_id}: remainder must name exactly the parent's open subset"
            )
    for ref, count in Counter(child_refs).items():
        if count > 1:
            errors.append(f"ambiguous remainder obligations for {ref}")
    for event in state.decisions:
        targets = relations if event.target_kind is TargetKind.RELATION else obligations
        if event.target_ref not in targets:
            errors.append(
                f"decision {event.decision_id}: target does not resolve to an immutable record"
            )
        if event.basis_state_ref not in state.history_refs:
            errors.append(
                f"decision {event.decision_id}: basis_state_ref is not in declared chain context"
            )
        if (
            event.target_kind is TargetKind.RELATION
            and event.target_ref in relations
            and relations[event.target_ref].relation_type
            in (RelationType.PROTECTED_ABSENCE, RelationType.RETURN_DUE)
            and event.kind is DecisionKind.RESOLVE
        ):
            errors.append(
                f"decision {event.decision_id}: this relation cannot be generically resolved"
            )
    return tuple(errors)


def check_seal(state: WitnessState) -> tuple[str, ...]:
    """The entire live payload reseals; no claim of truth or freshness."""

    try:
        digest = payload_digest(
            canonical_state_payload(
                state.subject_id,
                state.review_moment,
                state.envelopes,
                state.relations,
                state.unclassified,
                state.returns,
                state.prior_ref,
                state.decisions,
                state.history_refs,
            )
        )
    except (ValueError, TypeError) as exc:
        return (f"state content cannot form a strict JSON seal: {exc}",)
    return (
        ()
        if digest == state.state_digest
        else ("state content does not match its seal",)
    )


def validate_state(state: WitnessState) -> tuple[StructuralIssue, ...]:
    """All local structure issues, deterministic and inspectable on refusal."""

    issues: list[StructuralIssue] = []
    if type(state.subject_id) is not str:
        issues.append(
            StructuralIssue(
                "SUBJECT", state.state_digest, "register subject_id must be a string"
            )
        )
    for envelope in state.envelopes:
        _, intake_issues = intake_envelope(canonical_envelope(envelope))
        issues.extend(
            StructuralIssue(
                "ENVELOPE",
                envelope.report_ref,
                f"envelope {envelope.line_id}: {i.field}: {i.message}",
            )
            for i in intake_issues
        )
    for holding in state.unclassified:
        if not valid_calendar_date(holding.review_moment):
            issues.append(
                StructuralIssue(
                    "DATE",
                    holding.held_id,
                    "holding review_moment must be a real calendar date",
                )
            )
    for code, check in (
        ("IDENTITY", check_distinct_ids),
        ("DIGEST", check_digest_shapes),
        ("REFERENCE", check_refs_resolve),
        ("SEAL", check_seal),
    ):
        issues.extend(
            StructuralIssue(code, state.state_digest, message)
            for message in check(state)
        )
    if not valid_calendar_date(state.review_moment):
        issues.append(
            StructuralIssue(
                "DATE",
                state.state_digest,
                "review_moment must be an ISO YYYY-MM-DD real calendar date",
            )
        )
    expected_prior = state.history_refs[-1] if state.history_refs else ""
    if state.prior_ref != expected_prior or len(set(state.history_refs)) != len(
        state.history_refs
    ):
        issues.append(
            StructuralIssue(
                "HISTORY",
                state.state_digest,
                "history_refs must be distinct and end at prior_ref",
            )
        )
    return tuple(issues)


def require_valid_state(state: WitnessState) -> None:
    """Refuse malformed bookkeeping without manufacturing a subject verdict."""

    issues = validate_state(state)
    if issues:
        raise InvalidStateError(issues)
