"""The review's 3x3 canonical witness battery, shipped and self-doubting.

Nine cases — three about STATE, three about RELATION, three about RETURN —
each of which constructs minimal envelope, relation, holding, and contract
inputs, runs the REAL register functions on them, and checks the required
behavior. :func:`run_battery` refuses to return unless every check holds.

A guard that has never rejected anything is not protection, so the battery
also accepts an injected-wrong variant: pass ``defeat=<case id>`` and that
case's observed behavior is deliberately falsified before checking, which
must make the battery raise. The tests prove both directions — green on the
real register, rejection on every injected wrong.
"""

from __future__ import annotations

from dataclasses import dataclass

from .envelopes import ENVELOPE_SCHEMA, EnvelopeRecord, intake_envelope
from .held import UnclassifiedHeld
from .metrics import relation_fidelity
from .projection import project, witness_hold_reasons
from .relations import RelationRecord, RelationType
from .returns import ReturnContractRecord, record_return
from .serialization import canonical_envelope, sha256_hex
from .state import (
    genesis_state,
    promote_unclassified,
    update_state,
    verify_chain,
)

#: The nine case identifiers, in the review's 3x3 order.
CASE_IDS: tuple[str, ...] = (
    "S1",
    "S2",
    "S3",
    "R4",
    "R5",
    "R6",
    "T7",
    "T8",
    "T9",
)

_USE = "battery: declared next use for posture checks"


class BatteryError(AssertionError):
    """Raised when any case's required behavior does not hold."""


@dataclass(frozen=True)
class CaseCheck:
    """One named check inside one case, with its observed outcome."""

    case_id: str
    check: str
    passed: bool
    detail: str


def _envelope(line_id: str, seed: str, subject_id: str = "s") -> EnvelopeRecord:
    """Intake a minimal, published-shape payload through the REAL intake."""

    payload = {
        "schema_version": ENVELOPE_SCHEMA,
        "line_id": line_id,
        "subject_id": subject_id,
        "review_date": "2026-07-29",
        "registry_version": "1.0.0",
        "registry_digest": sha256_hex(f"registry:{line_id}"),
        "native_status": {"native": f"opaque report of {line_id} ({seed})"},
        "report_ref": sha256_hex(f"report:{line_id}:{seed}"),
        "source_snapshot_refs": [f"snapshot:{seed}"],
        "scope_and_nonclaims": [
            "asserts nothing beyond its own native report",
        ],
    }
    record, issues = intake_envelope(payload)
    if record is None:
        raise BatteryError(f"battery fixture failed real intake: {issues}")
    return record


def _contract(
    contract_id: str,
    why_held: str,
    alternatives: tuple[str, ...],
    prior_state_ref: str = "",
) -> ReturnContractRecord:
    """A minimal open contract for battery fixtures."""

    return ReturnContractRecord(
        contract_id=contract_id,
        subject_id="s",
        why_held=why_held,
        alternatives_live=alternatives,
        change_condition="a dated observation that answers the hold",
        standing="the exporting line's maintainer",
        protected="the boundary named in the hold, if any",
        trigger="the naming has aged past its stated horizon",
        acceptance_condition="a dated record enters the register and is sealed",
        prior_state_ref=prior_state_ref,
    )


def _check(case_id: str, check: str, passed: bool, detail: str) -> CaseCheck:
    return CaseCheck(case_id=case_id, check=check, passed=passed, detail=detail)


def _case_s1(wrong: bool) -> tuple[CaseCheck, ...]:
    """STATE 1: a missing required report is held as unobserved.

    Absence of an envelope is neither a contradiction nor a withholding: it
    is held outside every category, no relation is auto-created, and the
    posture is 0 (held), not -1 (condemned) and not +1 (excused).
    """

    envelope = _envelope("golden_line", "s1")
    holding = UnclassifiedHeld(
        held_id="s1-h1",
        raw_observation="black_line supplied no envelope for subject s at 2026-07-29",
        provenance="battery intake sweep",
        candidate_relations=("UNRESOLVED_DEPENDENCY", "CANNOT_COMPARE"),
        reason_unclassified=(
            "the absence of a report is an unobserved input, not a "
            "contradiction and not a withholding"
        ),
        review_moment="2026-07-29",
    )
    state = genesis_state("s", "2026-07-29", (envelope,), (), (holding,))
    posture = project(state, _USE)
    observed_value = 1 if wrong else posture.value
    return (
        _check(
            "S1",
            "no relation is auto-created for the absence",
            len(state.relations) == 0,
            f"relations={len(state.relations)}",
        ),
        _check(
            "S1",
            "the absence is held as unobserved, so the posture is 0",
            observed_value == 0,
            f"value={observed_value}",
        ),
        _check(
            "S1",
            "the hold reason names the unclassified holding, not a verdict",
            any("held outside every category" in reason for reason in posture.reasons),
            f"reasons={posture.reasons}",
        ),
    )


def _case_s2(wrong: bool) -> tuple[CaseCheck, ...]:
    """STATE 2: strong support and strong resistance stay co-present.

    Conflict is first-class: both surfaces survive as separate refs on one
    typed relation, and after projection the whole structure is still
    recoverable from the state the scalar points back to.
    """

    supporter = _envelope("black_line", "s2-support")
    resister = _envelope("white_line", "s2-resist")
    tension = RelationRecord(
        relation_id="s2-r1",
        subject_id="s",
        source_report_refs=(supporter.report_ref, resister.report_ref),
        relation_type=RelationType.DIRECTIONAL_TENSION,
        bounded_description=(
            "black_line reports strong support while white_line records a "
            "strong open absence in the same territory"
        ),
        support_refs=(supporter.report_ref,),
        resistance_refs=(resister.report_ref,),
    )
    state = genesis_state("s", "2026-07-29", (supporter, resister), (tension,))
    posture = project(state, _USE)
    stored = state.relations[0]
    fidelity = 0.0 if wrong else relation_fidelity(posture, state)
    return (
        _check(
            "S2",
            "both surfaces are preserved as separate refs",
            stored.support_refs == (supporter.report_ref,)
            and stored.resistance_refs == (resister.report_ref,),
            f"support={stored.support_refs} resistance={stored.resistance_refs}",
        ),
        _check(
            "S2",
            "co-present conflict is not collapsed to no-evidence: value is 0",
            posture.value == 0,
            f"value={posture.value}",
        ),
        _check(
            "S2",
            "the structure is recoverable after projection",
            fidelity == 1.0,
            f"relation_fidelity={fidelity}",
        ),
    )


def _case_s3(wrong: bool) -> tuple[CaseCheck, ...]:
    """STATE 3: protected material honors its boundary; +1 is forbidden.

    Protection is not missing evidence to be mined, and no decision
    reference offered at projection time lifts it.
    """

    envelope = _envelope("white_line", "s3")
    protection = RelationRecord(
        relation_id="s3-r1",
        subject_id="s",
        source_report_refs=(envelope.report_ref,),
        relation_type=RelationType.PROTECTED_ABSENCE,
        bounded_description="the material is withheld behind a consent boundary",
        protected_boundary_refs=("consent:s3-boundary",),
    )
    state = genesis_state("s", "2026-07-29", (envelope,), (protection,))
    plain = project(state, _USE)
    with_ref = project(state, _USE, human_decision_ref="decision:s3-attempt")
    observed_with_ref = 1 if wrong else with_ref.value
    return (
        _check(
            "S3",
            "protection forbids +1",
            plain.value == 0,
            f"value={plain.value}",
        ),
        _check(
            "S3",
            "a projection-time decision ref does not lift protection",
            observed_with_ref == 0,
            f"value={observed_with_ref}",
        ),
        _check(
            "S3",
            "the reason says protection is not missing evidence",
            any("not missing evidence" in reason for reason in plain.reasons),
            f"reasons={plain.reasons}",
        ),
    )


def _case_r4(wrong: bool) -> tuple[CaseCheck, ...]:
    """RELATION 4: a block resists the route while the aspiration survives.

    The posture is -1 — non-compensatory — but the worthy aim and the need
    for an alternate path are recorded as fields, not lost in the refusal.
    """

    envelope = _envelope("red_line", "r4")
    block = RelationRecord(
        relation_id="r4-r1",
        subject_id="s",
        source_report_refs=(envelope.report_ref,),
        relation_type=RelationType.NON_COMPENSATORY_BLOCK,
        bounded_description=(
            "red_line's finding blocks this route regardless of any other "
            "line's strength; the aim itself is worthy and remains live"
        ),
    )
    contract = _contract(
        "r4-c1",
        why_held=(
            "the aim is preserved: the blocked route is refused, the "
            "aspiration is not condemned"
        ),
        alternatives=("an alternate path that does not cross the block",),
    )
    state = genesis_state("s", "2026-07-29", (envelope,), (block,), (), (contract,))
    posture = project(state, _USE)
    observed_value = 0 if wrong else posture.value
    stored = state.returns[0]
    return (
        _check(
            "R4",
            "an unresolved block forces -1",
            observed_value == -1,
            f"value={observed_value}",
        ),
        _check(
            "R4",
            "the aspiration is preserved in why_held",
            "aspiration" in stored.why_held,
            f"why_held={stored.why_held!r}",
        ),
        _check(
            "R4",
            "the alternate-path need is recorded",
            len(stored.alternatives_live) > 0,
            f"alternatives_live={stored.alternatives_live}",
        ),
    )


def _case_r5(wrong: bool) -> tuple[CaseCheck, ...]:
    """RELATION 5: a good method cannot manufacture settlement.

    An AGREES relation between two strong reports does not buy back an open
    absence: the unresolved dependency holds the posture at 0.
    """

    strong_a = _envelope("black_line", "r5-a")
    strong_b = _envelope("golden_line", "r5-b")
    agreement = RelationRecord(
        relation_id="r5-r1",
        subject_id="s",
        source_report_refs=(strong_a.report_ref, strong_b.report_ref),
        relation_type=RelationType.AGREES,
        bounded_description="two independent methods point the same way",
    )
    dependency = RelationRecord(
        relation_id="r5-r2",
        subject_id="s",
        source_report_refs=(strong_a.report_ref,),
        relation_type=RelationType.UNRESOLVED_DEPENDENCY,
        bounded_description=(
            "the agreed reading depends on an absence that is still open"
        ),
    )
    state = genesis_state(
        "s", "2026-07-29", (strong_a, strong_b), (agreement, dependency)
    )
    posture = project(state, _USE)
    observed_value = 1 if wrong else posture.value
    return (
        _check(
            "R5",
            "agreement does not settle the open absence: value is 0",
            observed_value == 0,
            f"value={observed_value}",
        ),
        _check(
            "R5",
            "the reason names the dependency, not a manufactured settlement",
            any("UNRESOLVED_DEPENDENCY" in reason for reason in posture.reasons),
            f"reasons={posture.reasons}",
        ),
    )


def _case_r6(wrong: bool) -> tuple[CaseCheck, ...]:
    """RELATION 6: tension with a named boundary is kept, not averaged.

    Direction, counter-signal, and the protecting boundary each survive as
    their own structured hold reason; the 0 is an enumeration, never a
    vague middle.
    """

    forward = _envelope("golden_line", "r6-forward")
    counter = _envelope("white_line", "r6-counter")
    tension = RelationRecord(
        relation_id="r6-r1",
        subject_id="s",
        source_report_refs=(forward.report_ref, counter.report_ref),
        relation_type=RelationType.DIRECTIONAL_TENSION,
        bounded_description="a forward direction with a live counter-signal",
        support_refs=(forward.report_ref,),
        resistance_refs=(counter.report_ref,),
    )
    boundary = RelationRecord(
        relation_id="r6-r2",
        subject_id="s",
        source_report_refs=(counter.report_ref,),
        relation_type=RelationType.PROTECTED_ABSENCE,
        bounded_description="part of the counter-signal sits behind a named boundary",
        protected_boundary_refs=("boundary:r6",),
    )
    state = genesis_state("s", "2026-07-29", (forward, counter), (tension, boundary))
    holds = witness_hold_reasons(state)
    kinds = {hold.kind for hold in holds}
    observed_kinds = {"vague_middle"} if wrong else kinds
    posture = project(state, _USE)
    stored = state.relations[0]
    return (
        _check(
            "R6",
            "the hold is an enumeration of distinct structured reasons",
            {"unresolved_relation", "protected_absence"} <= observed_kinds,
            f"kinds={sorted(observed_kinds)}",
        ),
        _check(
            "R6",
            "the tension keeps both surfaces after posture computation",
            posture.value == 0
            and stored.support_refs == (forward.report_ref,)
            and stored.resistance_refs == (counter.report_ref,),
            f"value={posture.value}",
        ),
    )


def _case_t7(wrong: bool) -> tuple[CaseCheck, ...]:
    """RETURN 7: stale naming reopens without condemning.

    The reopening is an appended relation and contract; the prior naming and
    its age are retained verbatim in the chain, and the posture is held, not
    inverted.
    """

    envelope = _envelope("black_line", "t7")
    first = genesis_state("s", "2026-07-01", (envelope,))
    contract = _contract(
        "t7-c1",
        why_held=(
            "the prior naming is retained; it has aged past its horizon and "
            "is due for a fresh dated observation"
        ),
        alternatives=("re-observe and re-name",),
        prior_state_ref=first.state_digest,
    )
    reopening = RelationRecord(
        relation_id="t7-r1",
        subject_id="s",
        source_report_refs=(envelope.report_ref,),
        relation_type=RelationType.RETURN_DUE,
        bounded_description="the naming is stale; a return is due",
        return_contract_ref="t7-c1",
    )
    second = update_state(
        first, "2026-07-29", relations=(reopening,), returns=(contract,)
    )
    chain_violations = verify_chain((first, second))
    prior_preserved = not wrong and canonical_envelope(
        second.envelopes[0]
    ) == canonical_envelope(first.envelopes[0])
    posture = project(second, _USE)
    return (
        _check(
            "T7",
            "the chain stays sound through the reopening",
            chain_violations == (),
            f"violations={chain_violations}",
        ),
        _check(
            "T7",
            "the prior naming and its age are retained verbatim",
            prior_preserved and second.returns[0].prior_state_ref == first.state_digest,
            f"prior_state_ref={second.returns[0].prior_state_ref[:12]}...",
        ),
        _check(
            "T7",
            "reopening holds at 0; it does not condemn to -1",
            posture.value == 0,
            f"value={posture.value}",
        ),
    )


def _case_t8(wrong: bool) -> tuple[CaseCheck, ...]:
    """RETURN 8: a partial repair closes only the verified part.

    The completed record keeps the open record's trigger, carries the
    remainder explicitly, and the posture stays held; a FULL verification of
    a parallel contract shows the cap releasing only when nothing remains.
    """

    envelope = _envelope("white_line", "t8")
    partial_open = _contract(
        "t8-c1", why_held="two parts are due back", alternatives=("wait",)
    )
    first = genesis_state(
        "s",
        "2026-07-01",
        (envelope,),
        (
            RelationRecord(
                relation_id="t8-r1",
                subject_id="s",
                source_report_refs=(envelope.report_ref,),
                relation_type=RelationType.RETURN_DUE,
                bounded_description="a two-part return is due",
                return_contract_ref="t8-c1",
            ),
        ),
        (),
        (partial_open,),
    )
    partial_done = record_return(
        partial_open,
        verification_result="part X returned with a usable date and was verified",
        open_remainder="part Y remains unobserved and keeps its trigger",
    )
    second = update_state(first, "2026-07-29", returns=(partial_done,))
    held_posture = project(second, _USE)

    full_open = _contract(
        "t8-c2", why_held="one part is due back", alternatives=("wait",)
    )
    full_done = record_return(
        full_open,
        verification_result="the single part returned and was verified",
        open_remainder="",
    )
    released = genesis_state(
        "s",
        "2026-07-29",
        (envelope,),
        (
            RelationRecord(
                relation_id="t8-r2",
                subject_id="s",
                source_report_refs=(envelope.report_ref,),
                relation_type=RelationType.RETURN_DUE,
                bounded_description="a one-part return was due and is met",
                return_contract_ref="t8-c2",
            ),
        ),
        (),
        (full_open, full_done),
    )
    released_posture = project(released, _USE)
    observed_trigger = "" if wrong else partial_done.trigger
    return (
        _check(
            "T8",
            "the remainder keeps its trigger",
            observed_trigger == partial_open.trigger,
            f"trigger={observed_trigger!r}",
        ),
        _check(
            "T8",
            "a partial return is not met and holds the posture at 0",
            partial_done.is_met is False and held_posture.value == 0,
            f"is_met={partial_done.is_met} value={held_posture.value}",
        ),
        _check(
            "T8",
            "history keeps both the open record and the completed record",
            len(second.returns) == 2,
            f"returns={len(second.returns)}",
        ),
        _check(
            "T8",
            "a fully verified return releases the cap",
            full_done.is_met is True and released_posture.value == 1,
            f"is_met={full_done.is_met} value={released_posture.value}",
        ),
    )


def _case_t9(wrong: bool) -> tuple[CaseCheck, ...]:
    """RETURN 9: an approved unknown links back; history is not rewritten.

    Promotion of a held observation requires a human decision reference and
    yields a NEW relation pointing at the original holding, which stays in
    the chain verbatim.
    """

    envelope = _envelope("golden_line", "t9")
    holding = UnclassifiedHeld(
        held_id="t9-h1",
        raw_observation="an input of a kind none of the four lines names",
        provenance="battery intake sweep",
        candidate_relations=("DIRECTIONAL_TENSION",),
        reason_unclassified="no current category fits without forcing",
        review_moment="2026-07-01",
    )
    first = genesis_state("s", "2026-07-01", (envelope,), (), (holding,))
    refused = False
    try:
        promote_unclassified(
            holding,
            "t9-r1",
            "s",
            (envelope.report_ref,),
            RelationType.DIRECTIONAL_TENSION,
            "the held input reads as a live tension",
            human_decision_ref="",
        )
    except ValueError:
        refused = True
    promoted = promote_unclassified(
        holding,
        "t9-r1",
        "s",
        (envelope.report_ref,),
        RelationType.DIRECTIONAL_TENSION,
        "the held input reads as a live tension",
        human_decision_ref="decision:daniel-2026-07-29",
    )
    second = update_state(first, "2026-07-29", relations=(promoted,))
    linked = "" if wrong else promoted.promoted_from_ref
    return (
        _check(
            "T9",
            "promotion without a human decision reference is refused",
            refused,
            f"refused={refused}",
        ),
        _check(
            "T9",
            "the new relation links back to the original holding",
            linked == holding.held_id,
            f"promoted_from_ref={linked!r}",
        ),
        _check(
            "T9",
            "the holding survives in history verbatim",
            second.unclassified == (holding,) and verify_chain((first, second)) == (),
            f"unclassified={len(second.unclassified)}",
        ),
    )


_CASES = {
    "S1": _case_s1,
    "S2": _case_s2,
    "S3": _case_s3,
    "R4": _case_r4,
    "R5": _case_r5,
    "R6": _case_r6,
    "T7": _case_t7,
    "T8": _case_t8,
    "T9": _case_t9,
}


def run_battery(defeat: str = "") -> tuple[CaseCheck, ...]:
    """Run all nine cases against the real register; refuse to return on failure.

    With ``defeat`` naming a case id, that case's observed behavior is
    deliberately falsified before checking, and this function MUST raise
    :class:`BatteryError` — proving the checks can reject. An unknown
    ``defeat`` value raises ``ValueError`` rather than silently running a
    clean battery under a wrong name.
    """

    if defeat and defeat not in _CASES:
        raise ValueError(f"unknown battery case {defeat!r}; known: {CASE_IDS}")
    results: list[CaseCheck] = []
    for case_id in CASE_IDS:
        results.extend(_CASES[case_id](wrong=(defeat == case_id)))
    failures = [item for item in results if not item.passed]
    if failures:
        lines = "; ".join(
            f"{item.case_id} {item.check} [{item.detail}]" for item in failures
        )
        raise BatteryError(f"battery refused: {lines}")
    return tuple(results)
