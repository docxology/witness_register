"""The optional next-use posture: a bounded interface value, never the state.

A projection answers exactly one question — "may this subject move toward
the declared next use right now?" — with one of three interface values:
``-1`` (route resisted), ``0`` (held), ``+1`` (nothing recorded forbids it).
The symbols are interface values, not the ontology: a projection always
carries the digest of the state that earned it and the reasons it holds, so
the scalar can never quietly replace the state it projects.

The invariants are enforced in code and are driven ONLY by relation records.
The register never parses, compares, or ranks any line's ``native_status``;
if a line's finding should constrain the posture, that constraint enters as
a typed relation, described by whoever registered it.

Non-compensatory means non-compensatory: no strength recorded anywhere in
the state can buy back a blocked route, a protected boundary, or an unmet
return. And "nothing to witness" is not permission — an empty state projects
to ``-1``, not to a benefit-of-the-doubt ``+1``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .relations import RelationRecord, RelationType
from .state import WitnessState, state_content_digest

#: Relation types that, while carrying no recorded human decision, hold the
#: posture at 0: they name live tension, dependency, incomparability, or
#: unreviewed observation. A recorded human decision on the relation resolves
#: it for posture purposes only — the relation record itself is unchanged.
_HOLDING_TYPES = (
    RelationType.UNRESOLVED_DEPENDENCY,
    RelationType.DIRECTIONAL_TENSION,
    RelationType.CANNOT_COMPARE,
    RelationType.UNCLASSIFIED_OBSERVATION,
)


@dataclass(frozen=True)
class HoldReason:
    """One structured reason a state's posture is held at 0.

    ``kind`` is the machine-checkable category, ``ref`` the id of the record
    that raised it, ``message`` the human sentence. A held posture is an
    enumeration of these, never one empty value.
    """

    kind: str
    ref: str
    message: str


@dataclass(frozen=True)
class Projection:
    """A bounded posture that cannot exist apart from its state.

    ``value`` is one of ``-1``, ``0``, ``+1``. ``declared_next_use`` is the
    use the posture was asked for — there is no posture without a declared
    use. ``state_ref`` is the digest of the exact state that earned the
    value, and ``reasons`` is never empty: even a ``+1`` says why.
    """

    value: int
    declared_next_use: str
    state_ref: str
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.value not in (-1, 0, 1):
            raise ValueError("projection value must be -1, 0, or +1")
        if not self.declared_next_use.strip():
            raise ValueError(
                "no posture without a declared use: declared_next_use must be non-blank"
            )
        if not self.state_ref:
            raise ValueError("a projection must carry the state_ref it earned")
        if not self.reasons:
            raise ValueError("a projection must carry at least one reason")


def _contract_met(state: WitnessState, contract_ref: str) -> bool:
    """Whether any record for *contract_ref* carries a fully verified return.

    A partial return — verified result with a non-empty remainder — does not
    meet the contract: only the verified part closed, and the unchanged
    trigger keeps the remainder due. An unresolvable reference is unmet,
    fail-closed.
    """

    return any(
        record.contract_id == contract_ref and record.is_met for record in state.returns
    )


def _unresolved_blocks(state: WitnessState) -> tuple[RelationRecord, ...]:
    """Blocks with no recorded human decision. These force -1."""

    return tuple(
        relation
        for relation in state.relations
        if relation.relation_type is RelationType.NON_COMPENSATORY_BLOCK
        and not relation.human_decision_ref.strip()
    )


def witness_hold_reasons(state: WitnessState) -> tuple[HoldReason, ...]:
    """Enumerate WHY this state's posture is held at 0 — structured, complete.

    The enumeration respects human decisions already recorded ON relation
    records, because those are part of the state; it knows nothing about any
    rescope offered at projection time. Protected absences are always
    enumerated: protection is not missing evidence to be mined, and no
    decision reference lifts it here.
    """

    holds: list[HoldReason] = []
    for relation in state.relations:
        if relation.relation_type is RelationType.PROTECTED_ABSENCE:
            holds.append(
                HoldReason(
                    kind="protected_absence",
                    ref=relation.relation_id,
                    message=(
                        "a boundary protects this material; protection is "
                        "not missing evidence to be mined, so +1 is "
                        f"forbidden: {relation.bounded_description}"
                    ),
                )
            )
        elif relation.relation_type is RelationType.RETURN_DUE:
            if relation.human_decision_ref.strip():
                continue
            if not _contract_met(state, relation.return_contract_ref):
                holds.append(
                    HoldReason(
                        kind="return_due",
                        ref=relation.relation_id,
                        message=(
                            "a return contract "
                            f"({relation.return_contract_ref or 'unnamed'}) "
                            "is outstanding or only partially verified; +1 "
                            "is forbidden until the return condition is met "
                            "or a human decision explicitly rescopes"
                        ),
                    )
                )
        elif relation.relation_type in _HOLDING_TYPES:
            if not relation.human_decision_ref.strip():
                holds.append(
                    HoldReason(
                        kind="unresolved_relation",
                        ref=relation.relation_id,
                        message=(
                            f"{relation.relation_type.value} with no "
                            "recorded human decision holds the posture: "
                            f"{relation.bounded_description}"
                        ),
                    )
                )
    promoted = {
        relation.promoted_from_ref
        for relation in state.relations
        if relation.promoted_from_ref and relation.human_decision_ref.strip()
    }
    for holding in state.unclassified:
        if holding.held_id not in promoted:
            holds.append(
                HoldReason(
                    kind="unclassified_held",
                    ref=holding.held_id,
                    message=(
                        "an observation is held outside every category and "
                        "has not been reviewed; holding is not permission"
                    ),
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
    state: WitnessState,
    declared_next_use: str,
    human_decision_ref: str = "",
) -> Projection:
    """Compute the bounded posture for one declared next use.

    Enforced, in order:

    - No declared use, no posture: a blank ``declared_next_use`` raises.
    - No posture for rewritten history: the state's seal is RE-DERIVED from
      its live content here, exactly as ``update_state`` and ``seal_tip``
      re-derive it, and a mismatch raises. Without this, a record mutated
      after sealing would earn a projection stamped with a ``state_ref``
      that no longer names the content it vouches for.
    - Any NON_COMPENSATORY_BLOCK with no human decision recorded on the
      relation forces ``-1``; nothing compensates.
    - A state with no relations and no envelopes is ``-1``: nothing to
      witness is not permission.
    - Any hold from :func:`witness_hold_reasons` caps the value at ``0``.
      A non-empty ``human_decision_ref`` argument lifts ONLY ``return_due``
      holds — an explicit, referenced rescope of an outstanding return — and
      is recorded in the reasons. It never lifts a protected absence and
      never resolves a block.
    - ``+1`` only when nothing forbids it AND at least one envelope exists.

    The scalar never erases the state: the result carries ``state_ref`` and
    at least one reason on every path.
    """

    if not declared_next_use.strip():
        raise ValueError(
            "no posture without a declared use: declared_next_use must be non-blank"
        )

    rederived = state_content_digest(
        state.subject_id,
        state.review_moment,
        state.envelopes,
        state.relations,
        state.unclassified,
        state.returns,
        state.prior_ref,
    )
    if rederived != state.state_digest:
        raise ValueError(
            "state content no longer matches its seal: a record was mutated "
            "after sealing; refusing to project rewritten history"
        )

    blocks = _unresolved_blocks(state)
    if blocks:
        reasons = tuple(
            "non-compensatory block with no recorded human decision forces "
            f"-1 ({relation.relation_id}): {relation.bounded_description}"
            for relation in blocks
        )
        return Projection(-1, declared_next_use, state.state_digest, reasons)

    if not state.relations and not state.envelopes:
        return Projection(
            -1,
            declared_next_use,
            state.state_digest,
            (
                "nothing is co-registered for this subject; nothing to "
                "witness is not permission",
            ),
        )

    holds = witness_hold_reasons(state)
    reasons: list[str] = []
    effective: list[HoldReason] = []
    for hold in holds:
        if hold.kind == "return_due" and human_decision_ref.strip():
            reasons.append(
                f"return_due hold on {hold.ref} rescoped by human decision "
                f"{human_decision_ref}"
            )
            continue
        effective.append(hold)
        reasons.append(f"{hold.kind} ({hold.ref}): {hold.message}")

    if effective:
        return Projection(0, declared_next_use, state.state_digest, tuple(reasons))

    reasons.append(
        f"{len(state.envelopes)} envelope(s) co-registered and no recorded "
        "relation forbids the declared next use; +1 states only that "
        "nothing recorded forbids it"
    )
    return Projection(1, declared_next_use, state.state_digest, tuple(reasons))
