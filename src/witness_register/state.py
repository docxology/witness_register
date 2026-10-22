"""The witness state: an append-only, sealed co-registration of records.

A :class:`WitnessState` holds, for one subject at one review moment, the
envelopes co-registered so far, the relations described among them, the
unclassified holdings, and the return contracts — sealed by a digest over
the canonical JSON of everything it contains. States form a chain:
each non-genesis state carries ``prior_ref`` — the digest of the state it
extends — and must contain every prior record unchanged and in place.
:func:`update_state` enforces that fail-closed; :func:`verify_chain` checks
a stored chain's linkage and digests after the fact.

The chain's known limitation is stated, not solved: an append-only chain's
TIP is unbound without external anchoring. :func:`seal_tip` hands you the
tip digest to anchor elsewhere; nothing in this package can stop a holder of
the whole chain from discarding recent states and presenting an earlier tip
as current.

Nothing here ranks, averages, merges, scores, or overrides the lines whose
envelopes it holds. Promotion of an unclassified holding into the relation
vocabulary is a human act: :func:`promote_unclassified` refuses to run
without a non-empty human decision reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable, Sequence

from .envelopes import EnvelopeRecord, valid_calendar_date
from .decisions import DecisionEvent, TargetKind
from .validation import require_valid_state, validate_state
from .held import UnclassifiedHeld
from .relations import RelationRecord, RelationType
from .returns import ReturnContractRecord
from .serialization import (
    canonical_state_payload,
    payload_digest,
    relation_digest,
    return_contract_digest,
    record_prefix_preserved,
)


@dataclass(frozen=True)
class WitnessState:
    """One sealed co-registration for one subject at one review moment.

    ``prior_ref`` is empty for a genesis state and otherwise the
    ``state_digest`` of the state this one extends. ``state_digest`` is the
    SHA-256 over the canonical JSON of every other field, including record
    order. Construct states through :func:`genesis_state` and
    :func:`update_state`; a hand-built state with a wrong digest is exactly
    what :func:`verify_chain` and the invariant battery exist to reject.
    ``decisions`` retains authority events; ``history_refs`` declares all
    predecessor digests. Only full-chain verification binds that declaration
    to actual states. Neither local structure nor a sound chain proves freshness.
    """

    subject_id: str
    review_moment: str
    envelopes: tuple[EnvelopeRecord, ...]
    relations: tuple[RelationRecord, ...]
    unclassified: tuple[UnclassifiedHeld, ...]
    returns: tuple[ReturnContractRecord, ...]
    prior_ref: str
    state_digest: str
    decisions: tuple[DecisionEvent, ...] = ()
    history_refs: tuple[str, ...] = ()


def state_content_digest(
    subject_id: str,
    review_moment: str,
    envelopes: tuple[EnvelopeRecord, ...],
    relations: tuple[RelationRecord, ...],
    unclassified: tuple[UnclassifiedHeld, ...],
    returns: tuple[ReturnContractRecord, ...],
    prior_ref: str,
    decisions: tuple[DecisionEvent, ...] = (),
    history_refs: tuple[str, ...] = (),
) -> str:
    """The seal a state with exactly this content must carry."""

    return payload_digest(
        canonical_state_payload(
            subject_id,
            review_moment,
            envelopes,
            relations,
            unclassified,
            returns,
            prior_ref,
            decisions,
            history_refs,
        )
    )


def _sealed(
    subject_id: str,
    review_moment: str,
    envelopes: tuple[EnvelopeRecord, ...],
    relations: tuple[RelationRecord, ...],
    unclassified: tuple[UnclassifiedHeld, ...],
    returns: tuple[ReturnContractRecord, ...],
    prior_ref: str,
    decisions: tuple[DecisionEvent, ...] = (),
    history_refs: tuple[str, ...] = (),
) -> WitnessState:
    """Build a state and seal it over its own canonical content."""

    digest = state_content_digest(
        subject_id,
        review_moment,
        envelopes,
        relations,
        unclassified,
        returns,
        prior_ref,
        decisions,
        history_refs,
    )
    return WitnessState(
        subject_id=subject_id,
        review_moment=review_moment,
        envelopes=envelopes,
        relations=relations,
        unclassified=unclassified,
        returns=returns,
        prior_ref=prior_ref,
        state_digest=digest,
        decisions=decisions,
        history_refs=history_refs,
    )


def raw_state(
    subject_id: str,
    review_moment: str,
    envelopes: Iterable[EnvelopeRecord] = (),
    relations: Iterable[RelationRecord] = (),
    unclassified: Iterable[UnclassifiedHeld] = (),
    returns: Iterable[ReturnContractRecord] = (),
    decisions: Iterable[DecisionEvent] = (),
) -> WitnessState:
    """Unvalidated seal-only inspection constructor with empty ``prior_ref``.

    This may seal invalid bookkeeping for inspection or planted-defect tests.
    Public projection independently validates it; a seal grants no authority.

    Stated non-check: an envelope's ``subject_id`` is NOT required to equal
    the state's. Each line names its subject in its own vocabulary, and two
    envelopes about the same work may spell their subjects differently, so
    string equality is not the correspondence that matters. That an envelope
    belongs under this state's subject is DECLARED by whoever registers it —
    it is a registration decision on the record, not a property this
    function can verify. A mis-filed envelope is a mis-registration to be
    caught in review, and the verbatim record keeps both spellings visible
    for exactly that review.
    """

    return _sealed(
        subject_id,
        review_moment,
        tuple(envelopes),
        tuple(relations),
        tuple(unclassified),
        tuple(returns),
        prior_ref="",
        decisions=tuple(decisions),
    )


def genesis_state(
    subject_id: str,
    review_moment: str,
    envelopes: Iterable[EnvelopeRecord] = (),
    relations: Iterable[RelationRecord] = (),
    unclassified: Iterable[UnclassifiedHeld] = (),
    returns: Iterable[ReturnContractRecord] = (),
) -> WitnessState:
    """Validated genesis; native subjects are NOT required to equal the register subject.

    Registration declares correspondence, not semantic equivalence. Use
    raw_state only to inspect refused imports or construct defect controls.
    """
    state = raw_state(
        subject_id, review_moment, envelopes, relations, unclassified, returns
    )
    require_valid_state(state)
    return state


def update_state(
    prior: WitnessState,
    review_moment: str,
    envelopes: Iterable[EnvelopeRecord] = (),
    relations: Iterable[RelationRecord] = (),
    unclassified: Iterable[UnclassifiedHeld] = (),
    returns: Iterable[ReturnContractRecord] = (),
    decisions: Iterable[DecisionEvent] = (),
) -> WitnessState:
    """Append records to a chain, refusing to build on tampered history.

    The new state carries ``prior_ref = prior.state_digest`` and contains
    every prior record unchanged, in place, before any addition. The check
    is fail-closed and real: the prior state's digest is RE-DERIVED from its
    live content here, so an in-place mutation of any prior record — for
    example, editing an envelope's ``native_status`` dict after sealing —
    raises instead of being silently carried forward.
    """

    rederived = state_content_digest(
        prior.subject_id,
        prior.review_moment,
        prior.envelopes,
        prior.relations,
        prior.unclassified,
        prior.returns,
        prior.prior_ref,
        prior.decisions,
        prior.history_refs,
    )
    if rederived != prior.state_digest:
        raise ValueError(
            "prior state content no longer matches its seal: a record was "
            "mutated after sealing; refusing to extend rewritten history"
        )
    require_valid_state(prior)
    added_decisions = tuple(decisions)
    added_returns = tuple(returns)
    relation_targets = {relation_digest(r) for r in prior.relations}
    contract_targets = {
        return_contract_digest(r) for r in prior.returns if not r.verification_result
    }
    for event in added_decisions:
        targets = (
            relation_targets
            if event.target_kind is TargetKind.RELATION
            else contract_targets
        )
        if (
            event.basis_state_ref != prior.state_digest
            or event.target_ref not in targets
        ):
            raise ValueError(
                "decision must target a record in its exact prior basis state"
            )
    for contract in added_returns:
        if (
            not contract.verification_result
            and contract.prior_state_ref
            and contract.prior_state_ref != prior.state_digest
        ):
            raise ValueError(
                "new obligation prior_state_ref must name the actual prior state"
            )
    state = _sealed(
        prior.subject_id,
        review_moment,
        prior.envelopes + tuple(envelopes),
        prior.relations + tuple(relations),
        prior.unclassified + tuple(unclassified),
        prior.returns + added_returns,
        prior_ref=prior.state_digest,
        decisions=prior.decisions + added_decisions,
        history_refs=prior.history_refs + (prior.state_digest,),
    )
    require_valid_state(state)
    return state


def verify_chain(states: Sequence[WitnessState]) -> tuple[str, ...]:
    """Check a stored chain's digests, linkage, and record preservation.

    Returns an empty tuple for a sound chain, and otherwise one message per
    violation: a state whose content no longer matches its seal, a genesis
    with a non-empty ``prior_ref``, a link whose ``prior_ref`` is not the
    previous state's digest, or a state that dropped or reordered a prior
    record. Verification never repairs anything.
    """

    violations: list[str] = []
    for position, state in enumerate(states):
        violations.extend(
            f"state {position}: {issue.message}" for issue in validate_state(state)
        )
        if position == 0:
            if state.history_refs or state.decisions:
                violations.append("state 0: genesis cannot carry ancestry or decisions")
            if state.prior_ref != "":
                violations.append("state 0: genesis must carry an empty prior_ref")
            continue
        previous = states[position - 1]
        if (
            type(state.subject_id) is not str
            or type(previous.subject_id) is not str
            or state.subject_id != previous.subject_id
        ):
            violations.append(f"state {position}: register subject identity changed")
        if state.history_refs != previous.history_refs + (previous.state_digest,):
            violations.append(
                f"state {position}: history_refs do not preserve actual ancestry"
            )
        try:
            prior_targets = {relation_digest(r) for r in previous.relations} | {
                return_contract_digest(r)
                for r in previous.returns
                if not r.verification_result
            }
        except (ValueError, TypeError) as exc:
            prior_targets = set()
            violations.append(
                f"state {position}: prior targets cannot form strict JSON: {exc}"
            )
        for event in state.decisions[len(previous.decisions) :]:
            if (
                event.basis_state_ref != previous.state_digest
                or event.target_ref not in prior_targets
            ):
                violations.append(
                    f"state {position}: decision basis/target was not in the prior state"
                )
        for contract in state.returns[len(previous.returns) :]:
            if (
                not contract.verification_result
                and contract.prior_state_ref
                and contract.prior_state_ref != previous.state_digest
            ):
                violations.append(
                    f"state {position}: obligation prior_state_ref is not the actual prior state"
                )
        if state.prior_ref != previous.state_digest:
            violations.append(
                f"state {position}: prior_ref does not name state "
                f"{position - 1}'s digest"
            )
        for kind in ("envelopes", "relations", "unclassified", "returns", "decisions"):
            before: tuple = getattr(previous, kind)
            after: tuple = getattr(state, kind)
            if not record_prefix_preserved(kind, before, after):
                violations.append(
                    f"state {position}: prior {kind} were dropped, "
                    "reordered, or altered"
                )
    return tuple(violations)


def seal_tip(state: WitnessState) -> str:
    """Return the chain tip's digest for EXTERNAL anchoring.

    An append-only chain's tip is unbound without external anchoring: every
    internal digest can be perfectly self-consistent while the most recent
    states have simply been discarded, and nothing inside the chain can
    detect that. This function only re-derives and hands you the value to
    anchor elsewhere — a signed message, an independent log, another
    system's record. The register states this limitation; it does not solve
    it.
    """

    rederived = state_content_digest(
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
    if rederived != state.state_digest:
        raise ValueError(
            "tip content does not match its seal; refusing to hand out a "
            "digest for anchoring"
        )
    return state.state_digest


#: The anchor statement's own schema string, versioned like every stored shape.
ANCHOR_STATEMENT_SCHEMA = "witness-register.anchor-statement/1.0"


def anchor_statement(chain: Sequence[WitnessState], anchored_on: str) -> dict:
    """A portable statement of the chain tip, for storage OUTSIDE the chain.

    The register's stated limitation is that nothing inside an append-only
    chain can detect a discarded tip. This helper prepares the code side of
    the remedy without choosing the external system: it verifies the whole
    chain, re-derives the tip's seal through :func:`seal_tip`, and returns a
    small strict-JSON-compatible record — schema string, subject, chain
    length, review moment, tip digest, and the operator-supplied anchoring
    date — to be written into a system the chain does not control (a signed
    note, an independent log, another repository's history). Storing the
    statement inside this repository would anchor nothing; where it goes is
    an operator decision, deliberately not made here. ``anchored_on`` is
    supplied, not read from a clock, so regenerating the statement for the
    same tip on the same declared date is byte-stable.
    """

    if not chain:
        raise ValueError("an empty chain has no tip to anchor")
    if not valid_calendar_date(anchored_on):
        raise ValueError("anchored_on must be an ISO YYYY-MM-DD date")
    violations = verify_chain(chain)
    if violations:
        raise ValueError(
            "refusing to anchor an unsound chain: " + "; ".join(violations)
        )
    tip = chain[-1]
    return {
        "record_schema": ANCHOR_STATEMENT_SCHEMA,
        "subject_id": tip.subject_id,
        "chain_length": len(chain),
        "tip_review_moment": tip.review_moment,
        "tip_digest": seal_tip(tip),
        "anchored_on": anchored_on,
        "boundary": (
            "this statement anchors nothing until it is stored in a system "
            "the chain does not control; it asserts chain-internal "
            "consistency at the stated tip, never the truth of any report"
        ),
    }


def promote_unclassified(
    held: UnclassifiedHeld,
    relation_id: str,
    subject_id: str,
    source_report_refs: Iterable[str],
    relation_type: RelationType,
    bounded_description: str,
    human_decision_ref: str,
    return_contract_ref: str = "",
) -> RelationRecord:
    """Promote a held observation into the relation vocabulary — by a human.

    The register NEVER auto-creates a category. Promotion requires a
    non-empty ``human_decision_ref`` naming the decision that chose the
    category, and the returned relation carries
    ``promoted_from_ref = held.held_id`` so it links back to the original
    holding. ``classification_decision_ref`` records only the category choice,
    never resolution. A promoted return also needs ``return_contract_ref``
    naming an open obligation. The held record itself is untouched: append the new relation to
    a later state and the holding stays in history exactly as it was —
    preserved, never rewritten.
    """

    if not human_decision_ref.strip():
        raise ValueError(
            "promotion requires a non-empty human_decision_ref: the "
            "register never auto-creates a category"
        )
    return RelationRecord(
        relation_id=relation_id,
        subject_id=subject_id,
        source_report_refs=tuple(source_report_refs),
        relation_type=relation_type,
        bounded_description=bounded_description,
        classification_decision_ref=human_decision_ref,
        return_contract_ref=return_contract_ref,
        promoted_from_ref=held.held_id,
    )
