"""Executed reproductions of the 2026-10-20 source-traced review.

These exercise bookkeeping only; arbitrary native status strings stay opaque.
"""

from dataclasses import replace

import pytest

from conftest import accept, make_contract, make_holding, make_payload, make_relation
from witness_register import (
    Projection,
    raw_state,
    RelationType,
    anchor_statement,
    check_projection,
    check_state,
    genesis_state,
    intake_envelope,
    project,
    promote_unclassified,
    record_return,
    state_content_digest,
    update_state,
    verify_chain,
    return_recoverability,
)

USE = "review the recorded route"


@pytest.mark.parametrize("kind", list(RelationType))
@pytest.mark.parametrize("support_count", [0, 50])
def test_wr01_classification_never_resolves(envelope, kind, support_count):
    holding = make_holding()
    relation = promote_unclassified(
        holding,
        "classified",
        "subject-1",
        (envelope.report_ref,),
        kind,
        "human classification only",
        "decision:classify",
    )
    contract = make_contract()
    if kind is RelationType.RETURN_DUE:
        relation = replace(relation, return_contract_ref=contract.contract_id)
    support = tuple(
        make_relation(envelope, relation_id=f"support-{n}")
        for n in range(support_count)
    )
    state = genesis_state(
        "subject-1",
        "2026-10-21",
        (envelope,),
        (relation,) + support,
        (holding,),
        (contract,),
    )
    expected = (
        -1
        if kind is RelationType.NON_COMPENSATORY_BLOCK
        else 1
        if kind is RelationType.AGREES
        else 0
    )
    assert project(state, USE).value == expected


IMMUTABLE_CHANGES = {
    "subject_id": "another subject",
    "why_held": "another rationale",
    "alternatives_live": ("an easier option",),
    "change_condition": "changed",
    "standing": "someone else",
    "protected": "no longer protected",
    "trigger": "another trigger",
    "acceptance_condition": "easier",
    "prior_state_ref": "a" * 64,
}


@pytest.mark.parametrize("field,value", IMMUTABLE_CHANGES.items())
def test_wr02_completion_cannot_rewrite_any_term(envelope, field, value):
    contract = make_contract()
    completion = replace(record_return(contract, "received", ""), **{field: value})
    state = raw_state(
        "subject-1", "2026-10-21", (envelope,), returns=(contract, completion)
    )
    assert check_state(state), field

    with pytest.raises(ValueError):
        project(state, USE)


def test_wr02_orphan_completion_is_invalid(envelope):
    state = raw_state(
        "subject-1",
        "2026-10-21",
        (envelope,),
        returns=(record_return(make_contract(), "received", ""),),
    )
    assert check_state(state)


def test_wr03_projection_refuses_an_orphan_promotion(envelope):
    holding = make_holding()
    promotion = promote_unclassified(
        holding,
        "orphan",
        "subject-1",
        ("a" * 64,),
        RelationType.AGREES,
        "orphan source",
        "decision:classify",
    )
    state = raw_state("subject-1", "2026-10-21", (envelope,), (promotion,), (holding,))
    assert check_state(state)
    with pytest.raises(ValueError, match="structur|resolve"):
        project(state, USE)


def test_wr04_acknowledging_an_existing_block_does_not_discharge_it(envelope):
    block = make_relation(
        envelope,
        RelationType.NON_COMPENSATORY_BLOCK,
        human_decision_ref="decision:acknowledge",
    )
    state = genesis_state("subject-1", "2026-10-21", (envelope,), (block,))
    assert project(state, USE).value == -1


def test_wr05_unscoped_projection_ref_cannot_discharge_two_returns(envelope):
    contracts = (make_contract("C1"), make_contract("C2"))
    due = tuple(
        make_relation(
            envelope,
            RelationType.RETURN_DUE,
            relation_id=f"due-{c.contract_id}",
            return_contract_ref=c.contract_id,
        )
        for c in contracts
    )
    state = genesis_state(
        "subject-1", "2026-10-21", (envelope,), due, returns=contracts
    )
    assert project(state, USE, human_decision_ref="decision:for-C1").value == 0


def test_wr06_intake_detaches_caller_owned_status():
    payload = make_payload()
    accepted = accept(payload)
    payload["native_status"]["detail"].append("changed before sealing")
    assert accepted.native_status["detail"] == ["opaque", 3]
    state = genesis_state("subject-1", "2026-10-21", (accepted,))
    payload["native_status"]["detail"].append("changed after sealing")
    assert project(state, USE).value == 1


@pytest.mark.parametrize("value", [(1, 2), {1: "x"}, "\ud800"])
def test_wr06_non_json_values_have_typed_refusals(value):
    record, issues = intake_envelope(make_payload(native_status=value))
    assert record is None
    assert any(issue.field == "native_status" for issue in issues)


@pytest.mark.parametrize("field", ["registry_digest", "report_ref"])
def test_wr06_digest_newline_is_not_a_digest(field):
    record, issues = intake_envelope(make_payload(**{field: "a" * 64 + "\n"}))
    assert record is None
    assert any(issue.field == field for issue in issues)


def test_wr07_subject_change_cannot_hide_behind_a_correct_seal(envelope):
    first = genesis_state("subject-1", "2026-10-20", (envelope,))
    second = update_state(first, "2026-10-21")
    moved = replace(
        second,
        subject_id="another-subject",
        state_digest=state_content_digest(
            "another-subject",
            second.review_moment,
            second.envelopes,
            second.relations,
            second.unclassified,
            second.returns,
            second.prior_ref,
        ),
    )
    assert any("subject" in issue for issue in verify_chain((first, moved)))


@pytest.mark.parametrize("day", ["2026-02-30", "2026-10-21\n", "2025-02-29"])
def test_wr07_state_and_anchor_require_real_dates(day):
    with pytest.raises(ValueError, match="date"):
        genesis_state("subject-1", day)
    first = genesis_state("subject-1", "2026-10-21")
    with pytest.raises(ValueError, match="date"):
        anchor_statement((first,), day)


def test_wr08_wording_alone_does_not_change_constraints(envelope):
    state = genesis_state(
        "subject-1",
        "2026-10-21",
        (envelope,),
        (make_relation(envelope, RelationType.DIRECTIONAL_TENSION),),
    )
    first, second = project(state, USE), project(state, "a much narrower use")
    assert (first.value, first.reasons) == (second.value, second.reasons)


def test_wr09_fabricated_favorable_posture_fails_replay(envelope):
    state = genesis_state(
        "subject-1",
        "2026-10-21",
        (envelope,),
        (make_relation(envelope, RelationType.NON_COMPENSATORY_BLOCK),),
    )
    fabricated = Projection(1, USE, state.state_digest, ("invented",))
    assert check_projection(fabricated, state)


def test_wr10_missing_and_malformed_fields_are_all_reported():
    payload = make_payload(line_id="", review_date="impossible")
    del payload["report_ref"]
    record, issues = intake_envelope(payload)
    assert record is None
    assert {issue.field for issue in issues} == {"report_ref", "line_id", "review_date"}


def test_wr09_non_genesis_segment_cannot_claim_full_chain_recoverability(envelope):
    first = genesis_state("subject-1", "2026-10-19", (envelope,))
    second = update_state(first, "2026-10-20")
    third = update_state(second, "2026-10-21")
    with pytest.raises(ValueError, match="segment"):
        return_recoverability((second, third))
