"""Structural invariants over states and chains, with proof of detection.

Every check returns violation messages instead of booleans so a failure is
actionable, and :func:`defect_battery` runs each check against a state built
to defeat exactly it — a guard that has never rejected anything is not
protection, so this module carries its own rejections.

These are checks on the register's bookkeeping only: distinctness of ids,
digest shapes, references that resolve, seals that re-derive, promotions
that carry their human decision. None of them evaluates the truth of any
line's report.
"""

from __future__ import annotations

from collections.abc import Sequence

from .envelopes import EnvelopeRecord, ENVELOPE_SCHEMA
from .held import UnclassifiedHeld
from .projection import Projection, project
from .relations import RelationRecord, RelationType
from .returns import ReturnContractRecord
from .serialization import sha256_hex
from .state import (
    WitnessState,
    genesis_state,
    raw_state,
    verify_chain,
)


from .validation import (
    check_distinct_ids,
    check_digest_shapes,
    check_refs_resolve,
    check_seal,
    validate_state,
)


def check_state(state: WitnessState) -> tuple[str, ...]:
    """Compatibility message surface for the shared typed structural validator."""
    return tuple(issue.message for issue in validate_state(state))


def check_chain(states: Sequence[WitnessState]) -> tuple[str, ...]:
    """Local structure plus full genesis linkage, identity and append-only replay."""
    errors = [
        f"state {n}: {message}"
        for n, state in enumerate(states)
        for message in check_state(state)
    ]
    return tuple(errors) + verify_chain(states)


def check_projection_binding(
    projection: Projection, state: WitnessState
) -> tuple[str, ...]:
    """Digest/seal binding only; no structural or semantic replay claim."""
    errors = (
        []
        if projection.state_ref == state.state_digest
        else ["projection state_ref does not name this state's digest"]
    )
    return tuple(errors) + check_seal(state)


def check_projection(projection: Projection, state: WitnessState) -> tuple[str, ...]:
    """Replay every stored input; a well-bound fabricated posture still fails."""
    errors = check_projection_binding(projection, state) + check_state(state)
    if errors:
        return errors
    replayed = project(
        state, projection.declared_next_use, projection.human_decision_ref
    )
    return (
        ()
        if replayed == projection
        else ("projection value/reasons do not match semantic replay",)
    )


def _hex(seed: str) -> str:
    """A deterministic 64-hex value for building battery fixtures."""

    return sha256_hex(seed)


def _envelope(report_ref: str, line_id: str = "black_line") -> EnvelopeRecord:
    """A minimal structurally valid envelope for battery fixtures."""

    return EnvelopeRecord(
        schema_version=ENVELOPE_SCHEMA,
        line_id=line_id,
        subject_id="battery-subject",
        review_date="2026-07-29",
        registry_version="1.0.0",
        registry_digest=_hex("registry"),
        native_status={"verdict": "opaque-to-the-register"},
        report_ref=report_ref,
        source_snapshot_refs=("snapshot:battery",),
        scope_and_nonclaims=("asserts nothing beyond its own report",),
    )


class InvariantDefeatError(AssertionError):
    """Raised when a planted defect goes undetected by its own check."""


def defect_battery() -> tuple[str, ...]:
    """Run every check against a state built to defeat exactly it.

    Returns the names of the defects that were detected — all of them, or
    this function raises :class:`InvariantDefeatError`. A clean pass over
    real data proves little if the checks cannot reject; this battery is the
    proof of detection.
    """

    ref_a, ref_b = _hex("envelope-a"), _hex("envelope-b")
    detected: list[str] = []

    def expect(
        name: str, violations: tuple[str, ...], state: WitnessState | None = None
    ) -> None:
        if not violations:
            raise InvariantDefeatError(f"planted defect {name!r} went undetected")
        if state is not None:
            try:
                project(state, "structural rejection control")
            except ValueError:
                pass
            else:
                raise InvariantDefeatError(
                    f"planted defect {name!r} passed public projection"
                )
        detected.append(name)

    duplicate_envelopes = raw_state(
        "s", "2026-07-29", envelopes=(_envelope(ref_a), _envelope(ref_a))
    )
    expect(
        "duplicate_envelope_refs",
        check_distinct_ids(duplicate_envelopes),
        duplicate_envelopes,
    )

    relation = RelationRecord(
        relation_id="r1",
        subject_id="s",
        source_report_refs=(ref_a,),
        relation_type=RelationType.AGREES,
        bounded_description="both reports name the same subject",
    )
    duplicate_relations = raw_state(
        "s",
        "2026-07-29",
        envelopes=(_envelope(ref_a),),
        relations=(relation, relation),
    )
    expect(
        "duplicate_relation_ids",
        check_distinct_ids(duplicate_relations),
        duplicate_relations,
    )

    holding = UnclassifiedHeld(
        held_id="h1",
        raw_observation="an input that fits no category",
        provenance="battery",
        candidate_relations=(),
        reason_unclassified="no current category fits",
        review_moment="2026-07-29",
    )
    duplicate_held = raw_state("s", "2026-07-29", unclassified=(holding, holding))
    expect("duplicate_held_ids", check_distinct_ids(duplicate_held), duplicate_held)

    open_contract = ReturnContractRecord(
        contract_id="c1",
        subject_id="s",
        why_held="held for the battery",
        alternatives_live=("wait",),
        change_condition="a dated re-observation",
        standing="the exporting line",
        protected="nothing",
        trigger="next review",
        acceptance_condition="a dated record enters the register",
    )
    mismatched_completion = ReturnContractRecord(
        contract_id="c1",
        subject_id="s",
        why_held="a DIFFERENT rationale",
        alternatives_live=("wait",),
        change_condition="a dated re-observation",
        standing="the exporting line",
        protected="nothing",
        trigger="next review",
        acceptance_condition="a dated record enters the register",
        verification_result="something came back",
    )
    rewritten_pair = raw_state(
        "s", "2026-07-29", returns=(open_contract, mismatched_completion)
    )
    expect(
        "return_pair_rewrites_rationale",
        check_distinct_ids(rewritten_pair),
        rewritten_pair,
    )

    bad_hex = raw_state("s", "2026-07-29", envelopes=(_envelope("not-a-digest"),))
    expect("digest_shape", check_digest_shapes(bad_hex), bad_hex)

    dangling_source = raw_state(
        "s",
        "2026-07-29",
        envelopes=(_envelope(ref_a),),
        relations=(
            RelationRecord(
                relation_id="r-dangling",
                subject_id="s",
                source_report_refs=(ref_b,),
                relation_type=RelationType.AGREES,
                bounded_description="points at an envelope that is not here",
            ),
        ),
    )
    expect(
        "unresolved_source_ref", check_refs_resolve(dangling_source), dangling_source
    )

    dangling_return = raw_state(
        "s",
        "2026-07-29",
        envelopes=(_envelope(ref_a),),
        relations=(
            RelationRecord(
                relation_id="r-return",
                subject_id="s",
                source_report_refs=(ref_a,),
                relation_type=RelationType.RETURN_DUE,
                bounded_description="a return is due",
                return_contract_ref="no-such-contract",
            ),
        ),
    )
    expect(
        "unresolved_return_contract",
        check_refs_resolve(dangling_return),
        dangling_return,
    )

    unpromoted = raw_state(
        "s",
        "2026-07-29",
        envelopes=(_envelope(ref_a),),
        relations=(
            RelationRecord(
                relation_id="r-promo",
                subject_id="s",
                source_report_refs=(ref_a,),
                relation_type=RelationType.UNCLASSIFIED_OBSERVATION,
                bounded_description="claims promotion without a human",
                promoted_from_ref="h-missing",
            ),
        ),
    )
    promotion_violations = check_refs_resolve(unpromoted)
    expect("promotion_unresolvable", promotion_violations, unpromoted)
    if not any("human_decision_ref" in item for item in promotion_violations):
        raise InvariantDefeatError(
            "planted defect 'promotion_without_human_ref' went undetected"
        )
    detected.append("promotion_without_human_ref")

    sound = genesis_state("s", "2026-07-29", envelopes=(_envelope(ref_a),))
    broken_seal = WitnessState(
        subject_id=sound.subject_id,
        review_moment=sound.review_moment,
        envelopes=sound.envelopes,
        relations=sound.relations,
        unclassified=sound.unclassified,
        returns=sound.returns,
        prior_ref=sound.prior_ref,
        state_digest=_hex("a seal over nothing"),
    )
    expect("broken_seal", check_seal(broken_seal), broken_seal)

    orphan = raw_state("s", "2026-07-30", envelopes=(_envelope(ref_b),))
    expect("broken_chain_link", tuple(verify_chain((sound, orphan))))

    posture = Projection(
        value=0,
        declared_next_use="battery probe",
        state_ref=_hex("some other state"),
        reasons=("battery",),
    )
    expect("projection_ref_mismatch", check_projection(posture, sound))

    clean = check_state(sound)
    if clean:
        raise InvariantDefeatError(
            f"the battery's own sound fixture fails checks: {clean}"
        )
    return tuple(detected)
