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
from .state import WitnessState, verify_chain
from .validation import check_seal
from .invariants import check_projection_binding, check_chain
from dataclasses import dataclass

#: The declared use under which premature_crowning_rate probes a state. A
#: projection cannot exist without a declared use; this one names itself as
#: a measurement probe so it can never be mistaken for a real posture.
MEASUREMENT_PROBE_USE = "premature-crowning measurement probe (not a real use)"


def state_binding_fidelity(projection: Projection, state: WitnessState) -> float:
    """Digest/seal binding only, never structural validity, replay or truth."""
    return 0.0 if check_projection_binding(projection, state) else 1.0


def relation_fidelity(projection: Projection, state: WitnessState) -> float:
    """Compatibility name for state_binding_fidelity; no semantic fidelity claim."""
    return state_binding_fidelity(projection, state)


@dataclass(frozen=True)
class ChainCoverage:
    """Preserved-link denominator separate from genesis and external-anchor coverage.

    An external_anchor_ref is only an operator claim, never evidence that
    this package checked off-machine independence or current tip freshness.
    """

    preserved_links: int
    total_links: int
    genesis_covered: bool
    full_chain_valid: bool
    external_anchor_ref: str
    single_state_sealed: bool

    @property
    def preservation_fraction(self) -> float:
        """Segment preservation, not a combined register quality or truth score."""
        if not self.total_links:
            return 1.0 if self.single_state_sealed else 0.0
        return self.preserved_links / self.total_links


def chain_coverage(
    chain: Sequence[WitnessState], external_anchor_ref: str = ""
) -> ChainCoverage:
    """Label a full genesis chain or a segment and expose the actual denominator."""
    if not chain:
        raise ValueError("an empty chain has no recoverability to measure")
    kept = 0
    for previous, state in zip(chain, chain[1:]):
        preserved = all(
            getattr(state, kind)[: len(getattr(previous, kind))]
            == getattr(previous, kind)
            for kind in (
                "envelopes",
                "relations",
                "unclassified",
                "returns",
                "decisions",
            )
        )
        if (
            not check_seal(previous)
            and not check_seal(state)
            and state.prior_ref == previous.state_digest
            and state.subject_id == previous.subject_id
            and state.history_refs == previous.history_refs + (previous.state_digest,)
            and preserved
        ):
            kept += 1
    return ChainCoverage(
        kept,
        len(chain) - 1,
        not chain[0].prior_ref and not chain[0].history_refs,
        not check_chain(chain),
        external_anchor_ref,
        not check_seal(chain[0]),
    )


def return_recoverability(chain: Sequence[WitnessState]) -> float:
    """Fraction of preserved links in a genesis-present chain; use chain_coverage for segments.

    This compatibility scalar does not assert full chain validity or anchor
    coverage. Read the structured denominator and coverage report for either.
    """
    report = chain_coverage(chain)
    if not report.genesis_covered:
        raise ValueError(
            "a non-genesis segment requires the explicit chain_coverage report"
        )
    if not report.total_links:
        return 1.0 if not verify_chain(chain) else 0.0
    return report.preservation_fraction


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
