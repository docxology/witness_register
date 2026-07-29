"""Append-only state updates, fail-closed tampering, chains, and promotion."""

from __future__ import annotations

import pytest
from conftest import make_contract, make_holding, make_relation

from witness_register import (
    HEX_DIGEST_RE,
    RelationType,
    genesis_state,
    promote_unclassified,
    seal_tip,
    update_state,
    verify_chain,
    WitnessState,
)


def test_genesis_is_sealed_with_an_empty_prior_ref(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    assert state.prior_ref == ""
    assert HEX_DIGEST_RE.match(state.state_digest)
    assert state.envelopes == (envelope,)


def test_review_moment_must_be_an_iso_date(envelope) -> None:
    with pytest.raises(ValueError, match="ISO"):
        genesis_state("subject-1", "July 29", (envelope,))


def test_update_appends_and_links(envelope, second_envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = update_state(first, "2026-07-29", envelopes=(second_envelope,))
    assert second.prior_ref == first.state_digest
    assert second.envelopes == (envelope, second_envelope)
    assert verify_chain((first, second)) == ()


def test_update_carries_every_record_kind_forward(envelope) -> None:
    relation = make_relation(envelope)
    contract = make_contract()
    holding = make_holding()
    first = genesis_state(
        "subject-1", "2026-07-01", (envelope,), (relation,), (holding,), (contract,)
    )
    second = update_state(first, "2026-07-29")
    assert second.relations == (relation,)
    assert second.unclassified == (holding,)
    assert second.returns == (contract,)


def test_update_fails_closed_on_in_place_mutation(envelope) -> None:
    """Editing a sealed record's mutable payload is refused, not carried."""

    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    envelope.native_status["verdict"] = "QUIETLY_REWRITTEN"
    with pytest.raises(ValueError, match="rewritten history"):
        update_state(state, "2026-07-30")
    # Restore so other assertions on the fixture stay meaningful.
    envelope.native_status["verdict"] = "STRONG_YES"


def test_verify_chain_accepts_a_worked_three_state_chain(
    envelope, second_envelope
) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = update_state(first, "2026-07-15", envelopes=(second_envelope,))
    third = update_state(second, "2026-07-29", relations=(make_relation(envelope),))
    assert verify_chain((first, second, third)) == ()


def test_verify_chain_rejects_a_wrong_seal(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    tampered = WitnessState(
        subject_id=state.subject_id,
        review_moment=state.review_moment,
        envelopes=state.envelopes,
        relations=state.relations,
        unclassified=state.unclassified,
        returns=state.returns,
        prior_ref=state.prior_ref,
        state_digest="0" * 64,
    )
    violations = verify_chain((tampered,))
    assert any("seal" in item for item in violations)


def test_verify_chain_rejects_a_non_genesis_start(envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = update_state(first, "2026-07-29")
    violations = verify_chain((second,))
    assert any("genesis" in item for item in violations)


def test_verify_chain_rejects_a_broken_link(envelope, second_envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    stranger = genesis_state("subject-1", "2026-07-15", (second_envelope,))
    violations = verify_chain((first, stranger))
    assert any("prior_ref" in item for item in violations)
    assert any("dropped, reordered, or altered" in item for item in violations)


def test_verify_chain_rejects_a_dropped_prior_record(envelope, second_envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope, second_envelope))
    second = update_state(first, "2026-07-29")
    shrunk = WitnessState(
        subject_id=second.subject_id,
        review_moment=second.review_moment,
        envelopes=(envelope,),
        relations=second.relations,
        unclassified=second.unclassified,
        returns=second.returns,
        prior_ref=second.prior_ref,
        state_digest=second.state_digest,
    )
    violations = verify_chain((first, shrunk))
    assert any("envelopes were dropped" in item for item in violations)


def test_seal_tip_returns_the_digest_for_external_anchoring(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    assert seal_tip(state) == state.state_digest


def test_seal_tip_refuses_a_tampered_tip(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    envelope.native_status["verdict"] = "QUIETLY_REWRITTEN"
    try:
        with pytest.raises(ValueError, match="anchoring"):
            seal_tip(state)
    finally:
        envelope.native_status["verdict"] = "STRONG_YES"


def test_seal_tip_docstring_states_the_unbound_tip_limitation() -> None:
    assert "unbound without external anchoring" in seal_tip.__doc__.lower()


def test_promotion_requires_a_human_decision(envelope) -> None:
    holding = make_holding()
    with pytest.raises(ValueError, match="human_decision_ref"):
        promote_unclassified(
            holding,
            "rel-p",
            "subject-1",
            (envelope.report_ref,),
            RelationType.DIRECTIONAL_TENSION,
            "reads as tension",
            human_decision_ref="   ",
        )


def test_promotion_links_back_and_preserves_history(envelope) -> None:
    holding = make_holding()
    first = genesis_state("subject-1", "2026-07-01", (envelope,), (), (holding,))
    promoted = promote_unclassified(
        holding,
        "rel-p",
        "subject-1",
        (envelope.report_ref,),
        RelationType.DIRECTIONAL_TENSION,
        "reads as tension",
        human_decision_ref="decision:daniel-2026-07-29",
    )
    second = update_state(first, "2026-07-29", relations=(promoted,))
    assert promoted.promoted_from_ref == holding.held_id
    assert promoted.human_decision_ref == "decision:daniel-2026-07-29"
    assert second.unclassified == (holding,)
    assert verify_chain((first, second)) == ()
