from dataclasses import replace

import pytest

from conftest import (
    accept,
    make_payload,
    make_contract,
    make_relation,
    supporting_context,
    make_holding,
)
from witness_register import (
    InvalidStateError,
    canonical_envelope,
    canonical_json,
    chain_coverage,
    genesis_state,
    intake_envelope,
    project_chain,
    state_content_digest,
    update_state,
    verify_chain,
    raw_state,
    check_state,
    project,
    record_return,
    check_distinct_ids,
    check_digest_shapes,
    check_refs_resolve,
)


@pytest.mark.parametrize("before,after", [(True, 1), (1, 1.0), (0.0, -0.0)])
@pytest.mark.parametrize("support_count", [0, 50])
def test_prefix_preservation_compares_canonical_content(before, after, support_count):
    envelope = accept(make_payload(native_status={"opaque": before}))
    supporters = tuple(
        replace(envelope, report_ref=f"{n + 1:064x}") for n in range(support_count)
    )
    first = genesis_state("s", "2026-10-20", (envelope,) + supporters)
    second = update_state(first, "2026-10-21")
    rewritten = replace(envelope, native_status={"opaque": after})
    assert canonical_json(canonical_envelope(envelope)) != canonical_json(
        canonical_envelope(rewritten)
    )
    forged = replace(second, envelopes=(rewritten,) + supporters)
    forged = replace(
        forged,
        state_digest=state_content_digest(
            forged.subject_id,
            forged.review_moment,
            forged.envelopes,
            forged.relations,
            forged.unclassified,
            forged.returns,
            forged.prior_ref,
            forged.decisions,
            forged.history_refs,
        ),
    )
    assert verify_chain((first, forged))
    coverage = chain_coverage((first, forged))
    assert not coverage.full_chain_valid
    assert coverage.preservation_fraction == 0.0
    with pytest.raises(InvalidStateError):
        project_chain((first, forged), "inspect records")


@pytest.mark.parametrize("depth", [60, 61, 62, 63, 64, 65])
def test_accepted_native_depth_round_trips_through_envelope_and_state(depth):
    status = None
    for _ in range(depth):
        status = [status]
    envelope, issues = intake_envelope(make_payload(native_status=status))
    if depth <= 61:
        assert envelope is not None, issues
    if envelope is None:
        assert any(
            i.field == "native_status" and "depth limit" in i.message for i in issues
        )
    else:
        canonical_json(canonical_envelope(envelope))
        assert verify_chain((genesis_state("s", "2026-10-21", (envelope,)),)) == ()


def test_accepted_character_budget_includes_its_envelope_and_state_wrappers():
    envelope, issues = intake_envelope(make_payload(native_status="x" * 1000000))
    if envelope is None:
        assert any("character limit" in issue.message for issue in issues)
    else:
        canonical_json(canonical_envelope(envelope))
        genesis_state("s", "2026-10-21", (envelope,))


def test_invalid_prefix_is_reported_without_canonicalization_escape():
    envelope = accept(make_payload())
    first = genesis_state("s", "2026-10-20", (envelope,))
    second = replace(
        update_state(first, "2026-10-21"),
        envelopes=(replace(envelope, native_status=float("nan")),),
    )
    assert verify_chain((first, second))
    assert chain_coverage((first, second)).preservation_fraction == 0.0


@pytest.mark.parametrize(
    "field,before,after",
    [
        ("subject_id", True, 1),
        ("standing", True, 1),
        ("protected", True, 1),
        ("change_condition", True, 1),
        ("alternatives_live", (True,), (1,)),
        ("alternatives_live", [True], [1]),
    ],
)
def test_return_terms_cannot_use_python_numeric_equality_to_change_identity(
    envelope, field, before, after
):
    contract = make_contract(**{field: before})
    completion = replace(record_return(contract, "verified", ""), **{field: after})
    state = raw_state("s", "2026-10-21", (envelope,), returns=(contract, completion))
    assert check_state(state)
    with pytest.raises(InvalidStateError):
        project(state, "inspect records")


@pytest.mark.parametrize("subject", [True, 1, 1.0, 0.0, None])
def test_register_subject_has_a_string_domain(envelope, subject):
    with pytest.raises(InvalidStateError):
        genesis_state(subject, "2026-10-21", (envelope,))


@pytest.mark.parametrize("before,after", [(True, 1), (1, 1.0), (0.0, -0.0)])
@pytest.mark.parametrize("support_count", [0, 50])
def test_malformed_subjects_cannot_establish_preserved_identity(
    envelope, before, after, support_count
):
    envelopes, support = supporting_context(envelope, support_count)
    first = raw_state(before, "2026-10-21", envelopes, support)
    second = replace(
        first,
        subject_id=after,
        prior_ref=first.state_digest,
        history_refs=(first.state_digest,),
    )
    second = replace(
        second,
        state_digest=state_content_digest(
            second.subject_id,
            second.review_moment,
            second.envelopes,
            second.relations,
            second.unclassified,
            second.returns,
            second.prior_ref,
            second.decisions,
            second.history_refs,
        ),
    )
    assert verify_chain((first, second))
    report = chain_coverage((first, second))
    assert not report.full_chain_valid
    assert report.preservation_fraction == 0.0
    with pytest.raises(InvalidStateError):
        project_chain((first, second), "inspect records")


@pytest.mark.parametrize("record_kind", ["relation", "contract"])
def test_non_envelope_invalid_json_retains_typed_diagnostics(envelope, record_kind):
    relation = make_relation(envelope)
    contract = make_contract()
    first = genesis_state(
        "s", "2026-10-21", (envelope,), (relation,), returns=(contract,)
    )
    second = update_state(first, "2026-10-21")
    if record_kind == "relation":
        first = replace(
            first, relations=(replace(relation, bounded_description="bad\ud800"),)
        )
    else:
        first = replace(first, returns=(replace(contract, standing="bad\ud800"),))
    assert check_state(first)
    with pytest.raises(InvalidStateError) as caught:
        project(first, "inspect records")
    assert any("strict JSON" in issue.message for issue in caught.value.issues)
    assert verify_chain((first, second))
    assert not chain_coverage((first, second)).full_chain_valid


@pytest.mark.parametrize(
    "field",
    [
        "relation_id",
        "subject_id",
        "bounded_description",
        "return_contract_ref",
        "human_decision_ref",
        "promoted_from_ref",
        "classification_decision_ref",
    ],
)
@pytest.mark.parametrize("value", [False, 0, 1, None, [], {}])
def test_relation_string_domains_refuse_before_projection(envelope, field, value):
    relation = make_relation(envelope, **{field: value})
    state = raw_state("register-subject", "2026-10-21", (envelope,), (relation,))
    assert getattr(state.relations[0], field) is value
    assert state.state_digest == state_content_digest(
        state.subject_id,
        state.review_moment,
        state.envelopes,
        state.relations,
        state.unclassified,
        state.returns,
        state.prior_ref,
        state.decisions,
        state.history_refs,
    )
    for check in (check_distinct_ids, check_digest_shapes, check_refs_resolve):
        assert check(state)
    assert verify_chain((state,))
    with pytest.raises(InvalidStateError):
        project_chain((state,), "inspect records")
    with pytest.raises(InvalidStateError):
        update_state(state, "2026-10-22")
    with pytest.raises(InvalidStateError) as caught:
        project(state, "inspect records")
    assert any(
        issue.code == "RELATION_DOMAIN" and field in issue.message
        for issue in caught.value.issues
    )
    with pytest.raises(InvalidStateError):
        genesis_state("register-subject", "2026-10-21", (envelope,), (relation,))


@pytest.mark.parametrize(
    "field",
    [
        "source_report_refs",
        "support_refs",
        "resistance_refs",
        "protected_boundary_refs",
    ],
)
@pytest.mark.parametrize(
    "value", [False, 0, 1, None, (False,), (0,), ([],), ({},), ["a" * 64]]
)
def test_relation_reference_domains_precede_hash_and_lookup(envelope, field, value):
    relation = make_relation(envelope, **{field: value})
    state = raw_state("register-subject", "2026-10-21", (envelope,), (relation,))
    assert check_state(state)
    for check in (check_distinct_ids, check_digest_shapes, check_refs_resolve):
        assert check(state)
    with pytest.raises(InvalidStateError):
        genesis_state("register-subject", "2026-10-21", (envelope,), (relation,))
    with pytest.raises(InvalidStateError) as caught:
        project(state, "inspect records")
    assert any(issue.code == "RELATION_DOMAIN" for issue in caught.value.issues)


def test_false_classification_authority_is_a_typed_structural_refusal(envelope):
    holding = make_holding()
    relation = make_relation(
        envelope,
        promoted_from_ref=holding.held_id,
        classification_decision_ref=False,
    )
    state = raw_state(
        "register-subject", "2026-10-21", (envelope,), (relation,), (holding,)
    )
    with pytest.raises(InvalidStateError) as caught:
        project(state, "inspect records")
    assert any(
        issue.code == "RELATION_DOMAIN"
        and "classification_decision_ref" in issue.message
        for issue in caught.value.issues
    )


@pytest.mark.parametrize(
    "field",
    [
        "contract_id",
        "subject_id",
        "why_held",
        "change_condition",
        "standing",
        "protected",
        "trigger",
        "acceptance_condition",
        "verification_result",
        "open_remainder",
        "prior_state_ref",
        "parent_return_ref",
    ],
)
@pytest.mark.parametrize("value", [False, 0, 1, None, [], {}])
def test_return_domains_refuse_before_replay_and_projection(envelope, field, value):
    contract = make_contract(**{field: value})
    state = raw_state("s", "2026-11-06", (envelope,), returns=(contract,))
    assert getattr(state.returns[0], field) is value
    for check in (check_distinct_ids, check_digest_shapes, check_refs_resolve):
        assert check(state)
    assert verify_chain((state,))
    prior = genesis_state("s", "2026-11-06", (envelope,))
    for operation in (
        lambda: genesis_state("s", "2026-11-06", (envelope,), returns=(contract,)),
        lambda: update_state(state, "2026-11-06"),
        lambda: update_state(prior, "2026-11-06", returns=(contract,)),
        lambda: project(state, "inspect return"),
    ):
        with pytest.raises(InvalidStateError) as caught:
            operation()
        assert any(
            issue.code == "RETURN_DOMAIN" and field in issue.message
            for issue in caught.value.issues
        )
    with pytest.raises(InvalidStateError):
        project_chain((state,), "inspect return")


@pytest.mark.parametrize("value", [False, 0, None, (False,), ([],), ["alternative"]])
def test_return_alternatives_stay_raw_and_fail_closed(envelope, value):
    from witness_register import canonical_return_contract

    contract = make_contract(alternatives_live=value)
    serialized = canonical_return_contract(contract)["alternatives_live"]
    assert serialized == (list(value) if type(value) is tuple else value)
    state = raw_state("s", "2026-11-06", (envelope,), returns=(contract,))
    with pytest.raises(InvalidStateError) as caught:
        project(state, "inspect return")
    assert any(issue.code == "RETURN_DOMAIN" for issue in caught.value.issues)


@pytest.mark.parametrize("value", [False, 0, 1, None, [], {}])
def test_malformed_remainder_cannot_become_a_new_obligation(value):
    from witness_register import remainder_contract

    partial = make_contract(verification_result="verified subset", open_remainder=value)
    with pytest.raises(ValueError, match="partial"):
        remainder_contract(partial, "child")
