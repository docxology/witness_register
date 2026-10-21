"""Bounded posture over validated authored constraints; never permission.

Free-text uses are auditable declarations, not semantic applicability filters.
Only exact-use, exact-target append-only events affect the global constraints.
Native statuses remain opaque and no volume of support compensates resistance.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from .decisions import decision_status
from .envelopes import HEX_DIGEST_RE
from .relations import RelationRecord, RelationType
from .returns import contract_met
from .serialization import relation_digest, return_contract_digest
from .state import WitnessState, verify_chain
from .validation import require_valid_state, InvalidStateError, StructuralIssue

_HOLDING_TYPES = (
    RelationType.UNRESOLVED_DEPENDENCY,
    RelationType.DIRECTIONAL_TENSION,
    RelationType.CANNOT_COMPARE,
    RelationType.UNCLASSIFIED_OBSERVATION,
)


@dataclass(frozen=True)
class HoldReason:
    """One categorical bookkeeping hold, never an averaged judgment."""

    kind: str
    ref: str
    message: str


@dataclass(frozen=True)
class Projection:
    """Bounded result with its complete replay inputs and unchanged state reference."""

    value: int
    declared_next_use: str
    state_ref: str
    reasons: tuple[str, ...]
    human_decision_ref: str = ""

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value not in (-1, 0, 1):
            raise ValueError("projection value must be -1, 0, or +1")
        if not self.declared_next_use.strip():
            raise ValueError(
                "no posture without a declared use: declared_next_use must be non-blank"
            )
        if not self.state_ref:
            raise ValueError("a projection must carry the state_ref it earned")
        if not HEX_DIGEST_RE.fullmatch(self.state_ref):
            raise ValueError("state_ref must be exactly 64 lowercase hex characters")
        if not self.reasons:
            raise ValueError("a projection must carry at least one reason")


def _relation_status(state: WitnessState, relation: RelationRecord, use: str) -> str:
    return decision_status(state.decisions, relation_digest(relation), use)


def _unresolved_blocks(state: WitnessState, use: str) -> tuple[RelationRecord, ...]:
    return tuple(
        r
        for r in state.relations
        if r.relation_type is RelationType.NON_COMPENSATORY_BLOCK
        and _relation_status(state, r, use) in ("open", "reopened")
    )


def witness_hold_reasons(
    state: WitnessState, declared_next_use: str = ""
) -> tuple[HoldReason, ...]:
    """Enumerate all active global constraints, with exact scoped lifecycle replay.

    Omitting a use applies no scoped clearance. Protected absence is always
    retained. Historic human_decision_ref strings have no discharging power.
    """

    require_valid_state(state)
    holds: list[HoldReason] = []
    for relation in state.relations:
        status = _relation_status(state, relation, declared_next_use)
        if status == "conflict":
            holds.append(
                HoldReason(
                    kind="decision_conflict",
                    ref=relation.relation_id,
                    message="contradictory scoped decisions remain visible; no winner is selected",
                )
            )
        if relation.relation_type is RelationType.PROTECTED_ABSENCE:
            holds.append(
                HoldReason(
                    kind="protected_absence",
                    ref=relation.relation_id,
                    message="a boundary protects this material; protection is not missing evidence to be mined",
                )
            )
        elif relation.relation_type is RelationType.RETURN_DUE:
            contract = next(
                r
                for r in state.returns
                if r.contract_id == relation.return_contract_ref
                and not r.verification_result
            )
            return_status = decision_status(
                state.decisions, return_contract_digest(contract), declared_next_use
            )
            if return_status == "conflict":
                holds.append(
                    HoldReason(
                        kind="decision_conflict",
                        ref=relation.relation_id,
                        message="contradictory return rescope/reopen decisions remain visible",
                    )
                )
            met = contract_met(state.returns, relation.return_contract_ref)
            if return_status != "cleared" and (
                not met or return_status in ("conflict", "reopened")
            ):
                holds.append(
                    HoldReason(
                        kind="return_due",
                        ref=relation.relation_id,
                        message=f"return contract ({relation.return_contract_ref}) is outstanding or only partially verified",
                    )
                )
        elif relation.relation_type in _HOLDING_TYPES and status != "cleared":
            holds.append(
                HoldReason(
                    kind="unresolved_relation",
                    ref=relation.relation_id,
                    message=f"{relation.relation_type.value} holds the posture: {relation.bounded_description}",
                )
            )
    promoted = {
        r.promoted_from_ref
        for r in state.relations
        if r.promoted_from_ref and r.classification_decision_ref.strip()
    }
    for holding in state.unclassified:
        if holding.held_id not in promoted:
            holds.append(
                HoldReason(
                    kind="unclassified_held",
                    ref=holding.held_id,
                    message="an observation is held outside every category; holding is not permission",
                )
            )
    if not state.envelopes:
        holds.append(
            HoldReason(
                kind="no_envelope",
                ref=state.subject_id,
                message="no envelope is co-registered; there is nothing to witness",
            )
        )
    return tuple(holds)


def project(
    state: WitnessState, declared_next_use: str, human_decision_ref: str = ""
) -> Projection:
    """Project validated bookkeeping with categorical, non-compensatory precedence.

    A classification or an unscoped human_decision_ref never clears anything.
    The compatibility argument is retained as a replayable receipt only; append
    DecisionEvent records for scoped authority. Structural defects raise typed
    InvalidStateError, distinct from a substantive -1. Seals prove no truth.
    """

    if not declared_next_use.strip():
        raise ValueError(
            "no posture without a declared use: declared_next_use must be non-blank"
        )
    require_valid_state(state)
    blocks = _unresolved_blocks(state, declared_next_use)
    holds = witness_hold_reasons(state, declared_next_use)
    reasons = [f"{h.kind} ({h.ref}): {h.message}" for h in holds]
    if blocks:
        reasons = [
            f"non-compensatory block forces -1 ({r.relation_id}): {r.bounded_description}"
            for r in blocks
        ] + reasons
        value = -1
    elif not state.envelopes:
        reasons.append(
            "nothing is co-registered for this subject; nothing to witness is not permission"
        )
        value = -1
    elif holds:
        value = 0
    else:
        value = 1
        reasons.append(
            f"{len(state.envelopes)} envelope(s) co-registered and nothing recorded forbids the declared next use"
        )
    for event in state.decisions:
        if event.declared_next_use == declared_next_use:
            reasons.append(
                f"scoped {event.kind.value} ({event.decision_id}): {event.human_decision_ref}; evidence {event.evidence_ref}"
            )
    return Projection(
        value, declared_next_use, state.state_digest, tuple(reasons), human_decision_ref
    )


def project_chain(
    chain: Sequence[WitnessState], declared_next_use: str, human_decision_ref: str = ""
) -> Projection:
    """Project a verified genesis chain tip; still no external freshness claim."""

    if not chain:
        raise ValueError("an empty chain has no tip to project")
    errors = verify_chain(chain)
    if errors:
        raise InvalidStateError(
            tuple(StructuralIssue("CHAIN", chain[-1].state_digest, e) for e in errors)
        )
    return project(chain[-1], declared_next_use, human_decision_ref)
