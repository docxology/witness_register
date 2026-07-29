"""Structural invariants: clean pass, targeted defects, and proof of detection."""

from __future__ import annotations

from conftest import make_contract, make_holding, make_relation

from witness_register import (
    Projection,
    RelationRecord,
    RelationType,
    check_chain,
    check_digest_shapes,
    check_distinct_ids,
    check_projection,
    check_refs_resolve,
    check_seal,
    check_state,
    defect_battery,
    genesis_state,
    project,
    record_return,
    update_state,
)

USE = "test: declared next use"


def test_a_worked_state_passes_every_check(envelope, second_envelope) -> None:
    contract = make_contract("con-1")
    state = genesis_state(
        "subject-1",
        "2026-07-29",
        (envelope, second_envelope),
        (
            make_relation(
                envelope,
                RelationType.DIRECTIONAL_TENSION,
                relation_id="ten",
                support_refs=(envelope.report_ref,),
                resistance_refs=(second_envelope.report_ref,),
                source_report_refs=(
                    envelope.report_ref,
                    second_envelope.report_ref,
                ),
            ),
            make_relation(
                envelope,
                RelationType.RETURN_DUE,
                relation_id="due",
                return_contract_ref="con-1",
            ),
        ),
        (make_holding(),),
        (contract,),
    )
    assert check_state(state) == ()


def test_a_worked_chain_passes_check_chain(envelope, second_envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = update_state(first, "2026-07-29", envelopes=(second_envelope,))
    assert check_chain((first, second)) == ()


def test_check_chain_names_the_offending_state(envelope) -> None:
    contract = make_contract("con-1")
    done = record_return(contract, "verified", "")
    also_done = record_return(contract, "verified twice, somehow", "")
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope,), (), (), (contract, done, also_done)
    )
    violations = check_chain((state,))
    assert any(item.startswith("state 0:") for item in violations)


def test_distinct_ids_allows_the_open_plus_completed_pair(envelope) -> None:
    contract = make_contract("con-1")
    done = record_return(contract, "part X verified", "part Y open")
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope,), (), (), (contract, done)
    )
    assert check_distinct_ids(state) == ()


def test_distinct_ids_rejects_a_rewriting_completion(envelope) -> None:
    contract = make_contract("con-1")
    rewriting = make_contract(
        "con-1",
        why_held="a different rationale entirely",
        verification_result="came back",
    )
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope,), (), (), (contract, rewriting)
    )
    violations = check_distinct_ids(state)
    assert any("why_held and trigger" in item for item in violations)


def test_projection_check_accepts_its_own_state(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    posture = project(state, USE)
    assert check_projection(posture, state) == ()


def test_projection_check_rejects_a_foreign_state(envelope, second_envelope) -> None:
    first = genesis_state("subject-1", "2026-07-01", (envelope,))
    second = genesis_state("subject-1", "2026-07-29", (second_envelope,))
    posture = project(first, USE)
    violations = check_projection(posture, second)
    assert any("state_ref" in item for item in violations)


def test_projection_record_used_directly_still_needs_a_real_ref(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    fabricated = Projection(1, USE, "b" * 64, ("fabricated",))
    assert check_projection(fabricated, state) != ()


def test_digest_shape_check_covers_prior_ref(envelope) -> None:
    from witness_register import WitnessState, state_content_digest

    digest = state_content_digest(
        "subject-1", "2026-07-29", (envelope,), (), (), (), "not-hex"
    )
    state = WitnessState(
        subject_id="subject-1",
        review_moment="2026-07-29",
        envelopes=(envelope,),
        relations=(),
        unclassified=(),
        returns=(),
        prior_ref="not-hex",
        state_digest=digest,
    )
    violations = check_digest_shapes(state)
    assert any("prior_ref" in item for item in violations)


def test_refs_resolve_rejects_dangling_support_and_resistance(
    envelope, second_envelope
) -> None:
    dangling = RelationRecord(
        relation_id="rel",
        subject_id="subject-1",
        source_report_refs=(envelope.report_ref,),
        relation_type=RelationType.DIRECTIONAL_TENSION,
        bounded_description="support points somewhere absent",
        support_refs=(second_envelope.report_ref,),
    )
    state = genesis_state("subject-1", "2026-07-29", (envelope,), (dangling,))
    violations = check_refs_resolve(state)
    assert any("support_refs" in item for item in violations)


def test_seal_check_flags_in_place_mutation(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    assert check_seal(state) == ()
    envelope.native_status["verdict"] = "QUIETLY_REWRITTEN"
    try:
        assert check_seal(state) != ()
    finally:
        envelope.native_status["verdict"] = "STRONG_YES"


def test_defect_battery_detects_every_planted_defect() -> None:
    detected = defect_battery()
    assert set(detected) == {
        "duplicate_envelope_refs",
        "duplicate_relation_ids",
        "duplicate_held_ids",
        "return_pair_rewrites_rationale",
        "digest_shape",
        "unresolved_source_ref",
        "unresolved_return_contract",
        "promotion_unresolvable",
        "promotion_without_human_ref",
        "broken_seal",
        "broken_chain_link",
        "projection_ref_mismatch",
    }
    assert len(detected) == 12
