from dataclasses import replace

import pytest

from conftest import (
    accept,
    make_payload,
    make_contract,
    make_relation,
    supporting_context,
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
