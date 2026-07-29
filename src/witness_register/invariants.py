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

from collections import Counter
from collections.abc import Sequence

from .envelopes import EnvelopeRecord, ENVELOPE_SCHEMA, HEX_DIGEST_RE
from .held import UnclassifiedHeld
from .projection import Projection
from .relations import RelationRecord, RelationType
from .returns import ReturnContractRecord
from .serialization import sha256_hex
from .state import (
    WitnessState,
    genesis_state,
    state_content_digest,
    verify_chain,
)


def _duplicates(values: Sequence[str]) -> tuple[str, ...]:
    """The values that occur more than once, each named once."""

    return tuple(sorted(value for value, count in Counter(values).items() if count > 1))


def check_distinct_ids(state: WitnessState) -> tuple[str, ...]:
    """Envelope refs, relation ids, and held ids are distinct.

    Return contracts are the stated exception: one contract id may appear
    exactly twice — once open (empty ``verification_result``) and once with
    a verified return — because a completed return is a NEW record beside
    the open one, never a rewrite of it. The pair must agree on ``why_held``
    and ``trigger`` so the remainder keeps its trigger and rationale.
    """

    violations: list[str] = []
    for value in _duplicates([item.report_ref for item in state.envelopes]):
        violations.append(f"duplicate envelope report_ref {value}")
    for value in _duplicates([item.relation_id for item in state.relations]):
        violations.append(f"duplicate relation_id {value}")
    for value in _duplicates([item.held_id for item in state.unclassified]):
        violations.append(f"duplicate held_id {value}")
    by_contract: dict[str, list[ReturnContractRecord]] = {}
    for record in state.returns:
        by_contract.setdefault(record.contract_id, []).append(record)
    for contract_id, records in by_contract.items():
        open_records = [r for r in records if not r.verification_result]
        completed = [r for r in records if r.verification_result]
        if len(open_records) > 1 or len(completed) > 1 or len(records) > 2:
            violations.append(
                f"contract {contract_id}: more than one open or one completed record"
            )
        elif len(records) == 2:
            first, second = records
            if first.why_held != second.why_held or first.trigger != second.trigger:
                violations.append(
                    f"contract {contract_id}: the completed record does not "
                    "keep the open record's why_held and trigger"
                )
    return tuple(violations)


def check_digest_shapes(state: WitnessState) -> tuple[str, ...]:
    """Every stored digest field is 64 lowercase hex (or empty where allowed)."""

    violations: list[str] = []
    for envelope in state.envelopes:
        for field in ("registry_digest", "report_ref"):
            value = getattr(envelope, field)
            if not HEX_DIGEST_RE.match(value):
                violations.append(
                    f"envelope {envelope.line_id}: {field} {value!r} is not "
                    "64 lowercase hex"
                )
    if state.prior_ref and not HEX_DIGEST_RE.match(state.prior_ref):
        violations.append(f"prior_ref {state.prior_ref!r} is not 64 lowercase hex")
    if not HEX_DIGEST_RE.match(state.state_digest):
        violations.append(
            f"state_digest {state.state_digest!r} is not 64 lowercase hex"
        )
    return tuple(violations)


def check_refs_resolve(state: WitnessState) -> tuple[str, ...]:
    """Relation references resolve to records IN this state.

    ``source_report_refs``, ``support_refs``, and ``resistance_refs`` must
    name co-registered envelopes; a ``RETURN_DUE`` relation must name a
    contract held in the state; a promotion must name a holding in the
    state. ``protected_boundary_refs`` are boundary names, not record refs,
    and are deliberately not resolved here.
    """

    envelope_refs = {item.report_ref for item in state.envelopes}
    contract_ids = {item.contract_id for item in state.returns}
    held_ids = {item.held_id for item in state.unclassified}
    violations: list[str] = []
    for relation in state.relations:
        for field in ("source_report_refs", "support_refs", "resistance_refs"):
            for ref in getattr(relation, field):
                if ref not in envelope_refs:
                    violations.append(
                        f"relation {relation.relation_id}: {field} entry "
                        f"{ref} does not resolve to a co-registered envelope"
                    )
        if relation.relation_type is RelationType.RETURN_DUE:
            if relation.return_contract_ref not in contract_ids:
                violations.append(
                    f"relation {relation.relation_id}: RETURN_DUE names "
                    f"contract {relation.return_contract_ref!r}, which is "
                    "not held in this state"
                )
        if relation.promoted_from_ref:
            if relation.promoted_from_ref not in held_ids:
                violations.append(
                    f"relation {relation.relation_id}: promoted_from_ref "
                    f"{relation.promoted_from_ref!r} does not resolve to a "
                    "held record in this state"
                )
            if not relation.human_decision_ref.strip():
                violations.append(
                    f"relation {relation.relation_id}: a promotion must "
                    "carry a non-empty human_decision_ref; the register "
                    "never auto-creates a category"
                )
    return tuple(violations)


def check_seal(state: WitnessState) -> tuple[str, ...]:
    """The state's live content still re-derives to its seal."""

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
        return ("state content does not match its seal",)
    return ()


def check_state(state: WitnessState) -> tuple[str, ...]:
    """All structural checks over one state, aggregated."""

    return (
        check_distinct_ids(state)
        + check_digest_shapes(state)
        + check_refs_resolve(state)
        + check_seal(state)
    )


def check_chain(states: Sequence[WitnessState]) -> tuple[str, ...]:
    """Per-state structure plus chain linkage and history preservation."""

    violations: list[str] = []
    for position, state in enumerate(states):
        for message in check_state(state):
            violations.append(f"state {position}: {message}")
    violations.extend(verify_chain(states))
    return tuple(violations)


def check_projection(projection: Projection, state: WitnessState) -> tuple[str, ...]:
    """The projection's state_ref resolves to this exact, still-sealed state."""

    violations: list[str] = []
    if projection.state_ref != state.state_digest:
        violations.append("projection state_ref does not name this state's digest")
    violations.extend(check_seal(state))
    return tuple(violations)


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

    def expect(name: str, violations: tuple[str, ...]) -> None:
        if not violations:
            raise InvariantDefeatError(f"planted defect {name!r} went undetected")
        detected.append(name)

    duplicate_envelopes = genesis_state(
        "s", "2026-07-29", envelopes=(_envelope(ref_a), _envelope(ref_a))
    )
    expect("duplicate_envelope_refs", check_distinct_ids(duplicate_envelopes))

    relation = RelationRecord(
        relation_id="r1",
        subject_id="s",
        source_report_refs=(ref_a,),
        relation_type=RelationType.AGREES,
        bounded_description="both reports name the same subject",
    )
    duplicate_relations = genesis_state(
        "s",
        "2026-07-29",
        envelopes=(_envelope(ref_a),),
        relations=(relation, relation),
    )
    expect("duplicate_relation_ids", check_distinct_ids(duplicate_relations))

    holding = UnclassifiedHeld(
        held_id="h1",
        raw_observation="an input that fits no category",
        provenance="battery",
        candidate_relations=(),
        reason_unclassified="no current category fits",
        review_moment="2026-07-29",
    )
    duplicate_held = genesis_state("s", "2026-07-29", unclassified=(holding, holding))
    expect("duplicate_held_ids", check_distinct_ids(duplicate_held))

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
    rewritten_pair = genesis_state(
        "s", "2026-07-29", returns=(open_contract, mismatched_completion)
    )
    expect("return_pair_rewrites_rationale", check_distinct_ids(rewritten_pair))

    bad_hex = genesis_state("s", "2026-07-29", envelopes=(_envelope("not-a-digest"),))
    expect("digest_shape", check_digest_shapes(bad_hex))

    dangling_source = genesis_state(
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
    expect("unresolved_source_ref", check_refs_resolve(dangling_source))

    dangling_return = genesis_state(
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
    expect("unresolved_return_contract", check_refs_resolve(dangling_return))

    unpromoted = genesis_state(
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
    expect("promotion_unresolvable", promotion_violations)
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
    expect("broken_seal", check_seal(broken_seal))

    orphan = genesis_state("s", "2026-07-30", envelopes=(_envelope(ref_b),))
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
