"""Append-only authority and return replay acceptance, without evidence truth claims."""

from dataclasses import replace

import pytest

from conftest import make_contract, make_holding, make_relation
from witness_register import (
    DecisionEvent,
    DecisionKind,
    TargetKind,
    RelationType,
    InvalidStateError,
    genesis_state,
    project,
    record_return,
    remainder_contract,
    update_state,
    verify_chain,
    check_chain,
    relation_digest,
    return_contract_digest,
    canonical_json,
    canonical_decision,
)

USE = "review the recorded route"


def decision(state, target, kind=DecisionKind.RESOLVE, use=USE, name="D1"):
    is_contract = hasattr(target, "contract_id")
    return DecisionEvent(
        name,
        kind,
        TargetKind.CONTRACT if is_contract else TargetKind.RELATION,
        return_contract_digest(target) if is_contract else relation_digest(target),
        f"decision:{name}",
        f"evidence:{name}",
        use,
        state.state_digest,
    )


@pytest.mark.parametrize(
    "kind",
    [
        RelationType.NON_COMPENSATORY_BLOCK,
        RelationType.DIRECTIONAL_TENSION,
        RelationType.UNRESOLVED_DEPENDENCY,
        RelationType.CANNOT_COMPARE,
        RelationType.UNCLASSIFIED_OBSERVATION,
    ],
)
@pytest.mark.parametrize("support_count", [0, 50])
def test_existing_constraint_requires_explicit_resolution_chain(
    envelope, kind, support_count
):
    relation = make_relation(envelope, kind)
    supporters = tuple(
        replace(envelope, report_ref=f"{n + 1:064x}") for n in range(support_count)
    )
    support = tuple(
        make_relation(e, relation_id=f"support-{n}") for n, e in enumerate(supporters)
    )
    first = genesis_state(
        "subject-1", "2026-10-19", (envelope,) + supporters, (relation,) + support
    )
    acknowledged = update_state(
        first,
        "2026-10-20",
        decisions=(decision(first, relation, DecisionKind.ACKNOWLEDGE),),
    )
    expected = -1 if kind is RelationType.NON_COMPENSATORY_BLOCK else 0
    assert project(first, USE).value == project(acknowledged, USE).value == expected
    resolved = update_state(
        acknowledged,
        "2026-10-21",
        decisions=(decision(acknowledged, relation, name="D2"),),
    )
    assert project(resolved, USE).value == 1
    assert project(resolved, "another use").value == expected
    assert resolved.relations == acknowledged.relations == first.relations
    assert resolved.decisions[: len(acknowledged.decisions)] == acknowledged.decisions
    assert check_chain((first, acknowledged, resolved)) == ()
    assert project(resolved, USE) == project(resolved, USE)


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("support_count", [0, 50])
def test_contradictory_resolutions_hold_without_order_arbitration(
    envelope, reverse, support_count
):
    block = make_relation(envelope, RelationType.NON_COMPENSATORY_BLOCK)
    first = genesis_state("subject-1", "2026-10-20", (envelope,), (block,))
    events = (
        decision(first, block),
        decision(first, block, DecisionKind.REOPEN, name="D2"),
    )
    support = tuple(
        make_relation(envelope, relation_id=f"support-{n}")
        for n in range(support_count)
    )
    second = update_state(
        first,
        "2026-10-21",
        relations=support,
        decisions=events[::-1] if reverse else events,
    )
    assert project(second, USE).value == -1
    assert any("decision_conflict" in r for r in project(second, USE).reasons)
    assert any("non-compensatory block" in r for r in project(second, USE).reasons)
    assert verify_chain((first, second)) == ()


@pytest.mark.parametrize(
    "extra",
    [
        None,
        RelationType.NON_COMPENSATORY_BLOCK,
        RelationType.PROTECTED_ABSENCE,
        "holding",
    ],
)
@pytest.mark.parametrize("support_count", [0, 50])
def test_two_returns_only_exact_target_and_use_are_rescoped(
    envelope, extra, support_count
):
    contracts = (make_contract("C1"), make_contract("C2"))
    due = tuple(
        make_relation(
            envelope,
            RelationType.RETURN_DUE,
            relation_id=c.contract_id,
            return_contract_ref=c.contract_id,
        )
        for c in contracts
    )
    supporters = tuple(
        replace(envelope, report_ref=f"{n + 1:064x}") for n in range(support_count)
    )
    support = tuple(
        make_relation(e, relation_id=f"support-{n}") for n, e in enumerate(supporters)
    )
    relations = (
        due
        + support
        + (() if extra in (None, "holding") else (make_relation(envelope, extra),))
    )
    first = genesis_state(
        "subject-1",
        "2026-10-20",
        (envelope,) + supporters,
        relations,
        (make_holding(),) if extra == "holding" else (),
        contracts,
    )
    second = update_state(
        first,
        "2026-10-21",
        decisions=(decision(first, contracts[0], DecisionKind.RESCOPE),),
    )
    assert project(second, USE).value == (
        -1 if extra is RelationType.NON_COMPENSATORY_BLOCK else 0
    )
    assert any(
        "C2" in reason and "return_due" in reason
        for reason in project(second, USE).reasons
    )
    third = update_state(
        second,
        "2026-10-21",
        decisions=(decision(second, contracts[1], DecisionKind.RESCOPE, name="D2"),),
    )
    assert project(third, USE).value == (
        1
        if extra is None
        else -1
        if extra is RelationType.NON_COMPENSATORY_BLOCK
        else 0
    )
    assert project(third, "another use").value == (
        -1 if extra is RelationType.NON_COMPENSATORY_BLOCK else 0
    )
    assert check_chain((first, second, third)) == ()


@pytest.mark.parametrize("support_count", [0, 50])
def test_partial_then_remainder_verification_closes_only_that_obligation(
    envelope, support_count
):
    contract = make_contract()
    due = make_relation(
        envelope, RelationType.RETURN_DUE, return_contract_ref=contract.contract_id
    )
    supporters = tuple(
        replace(envelope, report_ref=f"{n + 1:064x}") for n in range(support_count)
    )
    support = tuple(
        make_relation(e, relation_id=f"support-{n}") for n, e in enumerate(supporters)
    )
    first = genesis_state(
        "subject-1",
        "2026-10-19",
        (envelope,) + supporters,
        (due,) + support,
        returns=(contract,),
    )
    partial = record_return(contract, "part X verified", "part Y observed and dated")
    second = update_state(first, "2026-10-20", returns=(partial,))
    child = remainder_contract(partial, "C-remainder", second.state_digest)
    third = update_state(second, "2026-10-21", returns=(child,))
    done = record_return(child, "part Y verified", "")
    fourth = update_state(third, "2026-10-21", returns=(done,))
    assert [project(s, USE).value for s in (first, second, third, fourth)] == [
        0,
        0,
        0,
        1,
    ]
    assert fourth.returns[: len(third.returns)] == third.returns
    assert child.trigger == partial.trigger == contract.trigger
    assert check_chain((first, second, third, fourth)) == ()
    assert project(fourth, USE) == project(fourth, USE)

    reopened = update_state(
        fourth,
        "2026-10-21",
        decisions=(decision(fourth, child, DecisionKind.REOPEN),),
    )
    assert project(reopened, USE).value == 0
    assert project(reopened, "another use").value == 1
    assert verify_chain((first, second, third, fourth, reopened)) == ()


def test_remainder_rejects_unknown_parent_changed_terms_and_ambiguous_children(
    envelope,
):
    contract = make_contract()
    partial = record_return(contract, "X verified", "Y due")
    first = genesis_state(
        "subject-1", "2026-10-20", (envelope,), returns=(contract, partial)
    )
    child = remainder_contract(partial, "child")
    for bad in (
        replace(child, parent_return_ref="a" * 64),
        replace(child, standing="another owner"),
        replace(child, why_held="different subset"),
    ):
        with pytest.raises(InvalidStateError):
            update_state(first, "2026-10-21", returns=(bad,))
    with pytest.raises(InvalidStateError, match="ambiguous"):
        update_state(
            first, "2026-10-21", returns=(child, replace(child, contract_id="child2"))
        )
    with pytest.raises(ValueError, match="partial"):
        remainder_contract(contract, "child")
    with pytest.raises(ValueError, match="new contract_id"):
        remainder_contract(partial, contract.contract_id)


def test_decision_basis_and_targets_must_exist_before_append(envelope):
    relation = make_relation(envelope, RelationType.DIRECTIONAL_TENSION)
    first = genesis_state("subject-1", "2026-10-20", (envelope,), (relation,))
    event = decision(first, relation)
    for bad in (
        replace(event, basis_state_ref="a" * 64),
        replace(event, target_ref="b" * 64),
    ):
        with pytest.raises(ValueError, match="basis"):
            update_state(first, "2026-10-21", decisions=(bad,))
    with pytest.raises(ValueError, match="prior_state_ref"):
        update_state(
            first, "2026-10-21", returns=(make_contract(prior_state_ref="a" * 64),)
        )
    assert canonical_json(canonical_decision(event)) == canonical_json(
        canonical_decision(event)
    )


@pytest.mark.parametrize(
    "kind", [RelationType.PROTECTED_ABSENCE, RelationType.RETURN_DUE]
)
def test_generic_resolution_cannot_clear_protected_absence_or_a_return(envelope, kind):
    contract = make_contract()
    relation = make_relation(envelope, kind, return_contract_ref=contract.contract_id)
    first = genesis_state(
        "subject-1", "2026-10-20", (envelope,), (relation,), returns=(contract,)
    )
    with pytest.raises(InvalidStateError, match="generically"):
        update_state(first, "2026-10-21", decisions=(decision(first, relation),))


@pytest.mark.parametrize(
    "field,value",
    [
        ("kind", "RESOLVE"),
        ("target_kind", "RELATION"),
        ("target_ref", "a" * 64 + "\n"),
        ("basis_state_ref", "a" * 64 + "\n"),
        ("declared_next_use", " "),
        ("human_decision_ref", ""),
        ("evidence_ref", " "),
        ("decision_id", ""),
        ("kind", DecisionKind.RESCOPE),
    ],
)
def test_decision_records_refuse_ambiguous_authority(envelope, field, value):
    relation = make_relation(envelope)
    state = genesis_state("subject-1", "2026-10-21", (envelope,), (relation,))
    with pytest.raises(ValueError):
        replace(decision(state, relation), **{field: value})


def test_contract_resolution_kind_and_duplicate_event_ids_are_refused(envelope):
    contract = make_contract()
    relation = make_relation(envelope)
    first = genesis_state(
        "s", "2026-10-20", (envelope,), (relation,), returns=(contract,)
    )
    with pytest.raises(ValueError, match="RESOLVE"):
        decision(first, contract)
    event = decision(first, relation)
    with pytest.raises(InvalidStateError, match="duplicate decision_id"):
        update_state(first, "2026-10-21", decisions=(event, event))


def test_reopening_a_verified_return_holds_and_conflicting_rescope_stays_visible(
    envelope,
):
    contract = make_contract()
    due = make_relation(
        envelope, RelationType.RETURN_DUE, return_contract_ref=contract.contract_id
    )
    first = genesis_state(
        "s",
        "2026-10-20",
        (envelope,),
        (due,),
        returns=(contract, record_return(contract, "verified", "")),
    )
    assert project(first, USE).value == 1
    reopened = update_state(
        first, "2026-10-21", decisions=(decision(first, contract, DecisionKind.REOPEN),)
    )
    assert project(reopened, USE).value == 0
    conflict = update_state(
        reopened,
        "2026-10-21",
        decisions=(decision(reopened, contract, DecisionKind.RESCOPE, name="D2"),),
    )
    assert project(conflict, USE).value == 0
    assert any("decision_conflict" in r for r in project(conflict, USE).reasons)
