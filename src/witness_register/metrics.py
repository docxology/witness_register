"""First-pass measures of the register's OWN bookkeeping.

Three measures from the design review, made inspectable. Every one of them
evaluates the register's record-keeping — whether structure survived
projection, whether updates preserved history, whether the posture ever
exceeded what a reviewer says it should have been. NONE of them measures
the truth of any line's report, the quality of any subject, or the wisdom
of any human decision.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from .projection import Projection, project
from .state import WitnessState, state_content_digest, verify_chain

#: The declared use under which premature_crowning_rate probes a state. A
#: projection cannot exist without a declared use; this one names itself as
#: a measurement probe so it can never be mistaken for a real posture.
MEASUREMENT_PROBE_USE = "premature-crowning measurement probe (not a real use)"


def relation_fidelity(projection: Projection, state: WitnessState) -> float:
    """1.0 when a reviewer can still recover the full structure; else 0.0.

    Checks that the projection's ``state_ref`` resolves to exactly this
    state AND that the state's relations are intact — its live content still
    re-derives to the digest the projection points at. When this holds, who
    agreed, who conflicted, what depended on what, and what is protected are
    all recoverable from the state the scalar points back to; the projection
    destroyed no information.
    """

    if projection.state_ref != state.state_digest:
        return 0.0
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
        return 0.0
    return 1.0


def return_recoverability(chain: Sequence[WitnessState]) -> float:
    """The fraction of chain links that preserved all prior records.

    Walks the chain with the same checks :func:`verify_chain` applies —
    seals re-derived, linkage intact, every prior record unchanged and in
    place — and returns ``kept / links``. A single-state chain has no links
    and scores 1.0 vacuously; an empty chain raises, because there is
    nothing to measure. When every update preserved prior rationale,
    provenance, and open remainders, the score is 1.0.
    """

    if not chain:
        raise ValueError("an empty chain has no recoverability to measure")

    def reseals(state: WitnessState) -> bool:
        return (
            state_content_digest(
                state.subject_id,
                state.review_moment,
                state.envelopes,
                state.relations,
                state.unclassified,
                state.returns,
                state.prior_ref,
            )
            == state.state_digest
        )

    if len(chain) == 1:
        return 1.0 if not verify_chain(chain) else 0.0
    kept = 0
    for position in range(1, len(chain)):
        previous, state = chain[position - 1], chain[position]
        preserved = all(
            getattr(state, kind)[: len(getattr(previous, kind))]
            == getattr(previous, kind)
            for kind in ("envelopes", "relations", "unclassified", "returns")
        )
        if (
            reseals(previous)
            and reseals(state)
            and state.prior_ref == previous.state_digest
            and preserved
        ):
            kept += 1
    return kept / (len(chain) - 1)


def premature_crowning_rate(
    cases: Iterable[tuple[WitnessState, int]],
) -> float:
    """The rate at which the projection exceeded the reviewer's posture.

    ``cases`` is (state, correct_posture) pairs, where ``correct_posture``
    is what a reviewer holding the full record says the bounded value should
    have been. Each state is projected under a self-naming measurement-probe
    use, and a case counts as premature crowning when ``project`` returned a
    value STRICTLY GREATER than the reviewer's. Returning a lower value is
    not crowning — caution is not the failure this measures. An empty case
    set raises rather than reporting a flattering 0.0.
    """

    materialized = tuple(cases)
    if not materialized:
        raise ValueError(
            "premature_crowning_rate needs at least one case; an empty set "
            "measured as 0.0 would be a fabricated clean bill"
        )
    crowned = 0
    for state, correct_posture in materialized:
        if correct_posture not in (-1, 0, 1):
            raise ValueError("correct_posture must be -1, 0, or +1")
        observed = project(state, MEASUREMENT_PROBE_USE)
        if observed.value > correct_posture:
            crowned += 1
    return crowned / len(materialized)
