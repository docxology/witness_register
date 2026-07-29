"""The three first-pass measures, exercised on worked states and chains."""

from __future__ import annotations

import pytest
from conftest import make_relation

from witness_register import (
    Projection,
    RelationType,
    WitnessState,
    genesis_state,
    premature_crowning_rate,
    project,
    relation_fidelity,
    return_recoverability,
    update_state,
)

USE = "test: declared next use"


def test_relation_fidelity_is_one_on_an_intact_pair(envelope, second_envelope) -> None:
    tension = make_relation(
        envelope,
        RelationType.DIRECTIONAL_TENSION,
        support_refs=(envelope.report_ref,),
        resistance_refs=(second_envelope.report_ref,),
        source_report_refs=(envelope.report_ref, second_envelope.report_ref),
    )
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope, second_envelope), (tension,)
    )
    posture = project(state, USE)
    assert relation_fidelity(posture, state) == 1.0


def test_relation_fidelity_is_zero_on_a_wrong_state(envelope, second_envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = genesis_state("subject-1", "2026-07-29", (second_envelope,))
    posture = project(first, USE)
    assert relation_fidelity(posture, second) == 0.0


def test_relation_fidelity_is_zero_when_relations_were_tampered(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    posture = project(state, USE)
    tampered = WitnessState(
        subject_id=state.subject_id,
        review_moment=state.review_moment,
        envelopes=state.envelopes,
        relations=(make_relation(envelope),),
        unclassified=state.unclassified,
        returns=state.returns,
        prior_ref=state.prior_ref,
        state_digest=state.state_digest,
    )
    assert relation_fidelity(posture, tampered) == 0.0


def test_return_recoverability_is_one_on_a_preserving_chain(
    envelope, second_envelope
) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = update_state(first, "2026-07-15", envelopes=(second_envelope,))
    third = update_state(second, "2026-07-29", relations=(make_relation(envelope),))
    assert return_recoverability((first, second, third)) == 1.0


def test_return_recoverability_scores_a_broken_link(envelope, second_envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = update_state(first, "2026-07-15", envelopes=(second_envelope,))
    stranger = genesis_state("subject-1", "2026-07-29", (second_envelope,))
    assert return_recoverability((first, second, stranger)) == 0.5


def test_return_recoverability_on_a_single_state(envelope) -> None:
    sound = genesis_state("subject-1", "2026-07-29", (envelope,))
    assert return_recoverability((sound,)) == 1.0
    tampered = WitnessState(
        subject_id=sound.subject_id,
        review_moment=sound.review_moment,
        envelopes=sound.envelopes,
        relations=sound.relations,
        unclassified=sound.unclassified,
        returns=sound.returns,
        prior_ref=sound.prior_ref,
        state_digest="0" * 64,
    )
    assert return_recoverability((tampered,)) == 0.0


def test_return_recoverability_refuses_an_empty_chain() -> None:
    with pytest.raises(ValueError, match="empty chain"):
        return_recoverability(())


def test_premature_crowning_rate_on_mixed_cases(envelope) -> None:
    open_state = genesis_state("subject-1", "2026-07-29", (envelope,))
    empty_state = genesis_state("subject-1", "2026-07-29")
    protected = genesis_state(
        "subject-1",
        "2026-07-29",
        (envelope,),
        (make_relation(envelope, RelationType.PROTECTED_ABSENCE),),
    )
    cases = [
        (open_state, 1),  # reviewer agrees with +1: not crowning
        (empty_state, -1),  # register says -1, reviewer says -1: not crowning
        (protected, 0),  # register says 0, reviewer says 0: not crowning
        (open_state, 0),  # register said +1 where the reviewer says 0: crowning
        (open_state, -1),  # register said +1 where the reviewer says -1: crowning
    ]
    assert premature_crowning_rate(cases) == pytest.approx(2 / 5)


def test_premature_crowning_rate_refuses_an_empty_case_set() -> None:
    with pytest.raises(ValueError, match="at least one case"):
        premature_crowning_rate(())


def test_premature_crowning_rate_rejects_an_out_of_range_posture(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    with pytest.raises(ValueError, match="correct_posture"):
        premature_crowning_rate([(state, 2)])


def test_caution_is_not_crowning(envelope) -> None:
    """A register value BELOW the reviewer's posture never counts."""

    protected = genesis_state(
        "subject-1",
        "2026-07-29",
        (envelope,),
        (make_relation(envelope, RelationType.PROTECTED_ABSENCE),),
    )
    assert premature_crowning_rate([(protected, 1)]) == 0.0


def test_metrics_docstrings_bound_their_claims() -> None:
    module_doc = __import__("witness_register.metrics", fromlist=["x"]).__doc__
    assert "none of them measures" in module_doc.lower()
    for function in (relation_fidelity, return_recoverability, premature_crowning_rate):
        assert function.__doc__


def test_projection_probe_use_names_itself() -> None:
    from witness_register import MEASUREMENT_PROBE_USE

    assert "not a real use" in MEASUREMENT_PROBE_USE
    # It is a valid declared use for a Projection, by construction.
    Projection(0, MEASUREMENT_PROBE_USE, "a" * 64, ("reason",))
