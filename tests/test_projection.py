"""Every projection invariant, with positive AND negative cases."""

from __future__ import annotations

import pytest
from conftest import make_contract, make_holding, make_relation

from witness_register import (
    Projection,
    RelationType,
    genesis_state,
    project,
    promote_unclassified,
    record_return,
    update_state,
    witness_hold_reasons,
)

USE = "test: declared next use"


def test_no_posture_without_a_declared_use(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    with pytest.raises(ValueError, match="declared"):
        project(state, "   ")


def test_projection_record_validates_its_own_bounds(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    with pytest.raises(ValueError, match="-1, 0, or \\+1"):
        Projection(2, USE, state.state_digest, ("reason",))
    with pytest.raises(ValueError, match="declared"):
        Projection(0, " ", state.state_digest, ("reason",))
    with pytest.raises(ValueError, match="state_ref"):
        Projection(0, USE, "", ("reason",))
    with pytest.raises(ValueError, match="reason"):
        Projection(0, USE, state.state_digest, ())


def test_an_empty_state_is_minus_one_not_permission() -> None:
    state = genesis_state("subject-1", "2026-07-29")
    posture = project(state, USE)
    assert posture.value == -1
    assert any("not permission" in reason for reason in posture.reasons)


def test_an_unresolved_block_forces_minus_one(envelope) -> None:
    block = make_relation(
        envelope, RelationType.NON_COMPENSATORY_BLOCK, relation_id="blk"
    )
    state = genesis_state("subject-1", "2026-07-29", (envelope,), (block,))
    posture = project(state, USE)
    assert posture.value == -1
    assert any("blk" in reason for reason in posture.reasons)


def test_a_human_resolved_block_no_longer_forces_minus_one(envelope) -> None:
    resolved = make_relation(
        envelope,
        RelationType.NON_COMPENSATORY_BLOCK,
        relation_id="blk",
        human_decision_ref="decision:resolved-2026-07-29",
    )
    state = genesis_state("subject-1", "2026-07-29", (envelope,), (resolved,))
    assert project(state, USE).value == 1


def test_a_projection_time_ref_never_resolves_a_block(envelope) -> None:
    block = make_relation(
        envelope, RelationType.NON_COMPENSATORY_BLOCK, relation_id="blk"
    )
    state = genesis_state("subject-1", "2026-07-29", (envelope,), (block,))
    assert project(state, USE, human_decision_ref="decision:attempt").value == -1


def test_protection_caps_at_zero_and_is_never_lifted(envelope) -> None:
    protection = make_relation(
        envelope,
        RelationType.PROTECTED_ABSENCE,
        relation_id="pro",
        protected_boundary_refs=("boundary:consent",),
    )
    state = genesis_state("subject-1", "2026-07-29", (envelope,), (protection,))
    plain = project(state, USE)
    assert plain.value == 0
    assert any("not missing evidence" in reason for reason in plain.reasons)
    # Negative case: not even an explicit decision ref lifts protection.
    assert project(state, USE, human_decision_ref="decision:try").value == 0


def test_a_due_return_caps_at_zero_until_verified(envelope) -> None:
    contract = make_contract("con-due")
    due = make_relation(
        envelope,
        RelationType.RETURN_DUE,
        relation_id="due",
        return_contract_ref="con-due",
    )
    first = genesis_state(
        "subject-1", "2026-07-01", (envelope,), (due,), (), (contract,)
    )
    assert project(first, USE).value == 0

    done = record_return(contract, "the return arrived dated and verified", "")
    second = update_state(first, "2026-07-29", returns=(done,))
    assert project(second, USE).value == 1


def test_a_partial_return_keeps_the_cap(envelope) -> None:
    contract = make_contract("con-part")
    due = make_relation(
        envelope,
        RelationType.RETURN_DUE,
        relation_id="due",
        return_contract_ref="con-part",
    )
    first = genesis_state(
        "subject-1", "2026-07-01", (envelope,), (due,), (), (contract,)
    )
    partial = record_return(contract, "part X verified", "part Y still open")
    second = update_state(first, "2026-07-29", returns=(partial,))
    assert project(second, USE).value == 0


def test_a_projection_time_ref_rescopes_only_the_return_cap(envelope) -> None:
    contract = make_contract("con-due")
    due = make_relation(
        envelope,
        RelationType.RETURN_DUE,
        relation_id="due",
        return_contract_ref="con-due",
    )
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope,), (due,), (), (contract,)
    )
    rescoped = project(state, USE, human_decision_ref="decision:rescope-1")
    assert rescoped.value == 1
    assert any("decision:rescope-1" in reason for reason in rescoped.reasons)


def test_a_relation_level_ref_also_rescopes_a_due_return(envelope) -> None:
    contract = make_contract("con-due")
    due = make_relation(
        envelope,
        RelationType.RETURN_DUE,
        relation_id="due",
        return_contract_ref="con-due",
        human_decision_ref="decision:recorded-on-the-relation",
    )
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope,), (due,), (), (contract,)
    )
    assert project(state, USE).value == 1


@pytest.mark.parametrize(
    "relation_type",
    [
        RelationType.UNRESOLVED_DEPENDENCY,
        RelationType.DIRECTIONAL_TENSION,
        RelationType.CANNOT_COMPARE,
        RelationType.UNCLASSIFIED_OBSERVATION,
    ],
)
def test_unresolved_relations_hold_at_zero_and_a_recorded_decision_lifts(
    envelope, relation_type
) -> None:
    unresolved = make_relation(envelope, relation_type, relation_id="rel")
    held = genesis_state("subject-1", "2026-07-29", (envelope,), (unresolved,))
    assert project(held, USE).value == 0

    decided = make_relation(
        envelope,
        relation_type,
        relation_id="rel",
        human_decision_ref="decision:reviewed",
    )
    lifted = genesis_state("subject-1", "2026-07-29", (envelope,), (decided,))
    assert project(lifted, USE).value == 1


def test_an_unpromoted_holding_caps_at_zero(envelope) -> None:
    holding = make_holding()
    state = genesis_state("subject-1", "2026-07-29", (envelope,), (), (holding,))
    posture = project(state, USE)
    assert posture.value == 0
    assert any("held outside every category" in r for r in posture.reasons)


def test_a_promoted_holding_no_longer_caps_by_itself(envelope) -> None:
    holding = make_holding()
    promoted = promote_unclassified(
        holding,
        "rel-p",
        "subject-1",
        (envelope.report_ref,),
        RelationType.AGREES,
        "the held input reads as agreement",
        human_decision_ref="decision:promote",
    )
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope,), (promoted,), (holding,)
    )
    assert project(state, USE).value == 1


def test_no_envelope_is_never_plus_one(envelope) -> None:
    # A holding alone is not witnessed material: with no relations and no
    # envelopes the posture is -1 — nothing to witness is not permission —
    # and the hold enumeration still names the missing envelope.
    holding = make_holding()
    state = genesis_state("subject-1", "2026-07-29", (), (), (holding,))
    posture = project(state, USE)
    assert posture.value == -1
    assert any("not permission" in reason for reason in posture.reasons)
    kinds = {hold.kind for hold in witness_hold_reasons(state)}
    assert "no_envelope" in kinds
    assert "unclassified_held" in kinds


def test_plus_one_always_carries_state_ref_and_reasons(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    posture = project(state, USE)
    assert posture.value == 1
    assert posture.state_ref == state.state_digest
    assert posture.reasons
    assert any("nothing recorded forbids" in reason for reason in posture.reasons)


def test_hold_reasons_are_structured_and_enumerated(envelope) -> None:
    protection = make_relation(
        envelope, RelationType.PROTECTED_ABSENCE, relation_id="pro"
    )
    tension = make_relation(
        envelope, RelationType.DIRECTIONAL_TENSION, relation_id="ten"
    )
    holding = make_holding()
    state = genesis_state(
        "subject-1", "2026-07-29", (envelope,), (protection, tension), (holding,)
    )
    holds = witness_hold_reasons(state)
    assert {hold.kind for hold in holds} == {
        "protected_absence",
        "unresolved_relation",
        "unclassified_held",
    }
    assert {hold.ref for hold in holds} == {"pro", "ten", "held-1"}
    assert all(hold.message for hold in holds)


def test_hold_reasons_are_empty_when_nothing_holds(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    assert witness_hold_reasons(state) == ()


def test_a_due_return_with_a_dangling_contract_ref_fails_closed(envelope) -> None:
    due = make_relation(
        envelope,
        RelationType.RETURN_DUE,
        relation_id="due",
        return_contract_ref="no-such-contract",
    )
    state = genesis_state("subject-1", "2026-07-29", (envelope,), (due,))
    assert project(state, USE).value == 0
