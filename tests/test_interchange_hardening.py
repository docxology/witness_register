"""Strict interchange and chain controls; no semantic native-status assertions."""

import json
from dataclasses import replace

import pytest

from conftest import accept, make_payload, make_relation, make_contract
from witness_register import (
    Projection,
    RelationType,
    anchor_statement,
    canonical_envelope,
    canonical_json,
    genesis_state,
    intake_envelope,
    project,
    raw_state,
    state_content_digest,
    update_state,
    verify_chain,
    check_projection,
    check_projection_binding,
    project_chain,
    canonical_projection,
    check_state,
    record_return,
    remainder_contract,
    state_binding_fidelity,
    chain_coverage,
    InvalidStateError,
)
from witness_register.json_data import (
    MAX_JSON_DEPTH,
    MAX_JSON_NODES,
    MAX_JSON_CHARACTERS,
)


@pytest.mark.parametrize(
    "value",
    [
        None,
        False,
        0,
        -4,
        1.25,
        " ",
        "λ",
        [],
        {},
        {"nested": [None, True, 3, {"s": "x"}]},
    ],
)
def test_accepted_status_round_trips_without_semantic_change(value):
    record = accept(make_payload(native_status=value))
    assert (
        json.loads(canonical_json(canonical_envelope(record)))["native_status"] == value
    )


def test_bounded_intake_refuses_deep_large_and_cyclic_data_with_named_issues():
    nested = []
    for _ in range(MAX_JSON_DEPTH + 2):
        nested = [nested]
    cycle = []
    cycle.append(cycle)
    for value in (
        nested,
        [None] * (MAX_JSON_NODES + 1),
        cycle,
        "x" * (MAX_JSON_CHARACTERS + 1),
        1 << 5000,
    ):
        record, issues = intake_envelope(make_payload(native_status=value))
        assert record is None
        assert issues and all(i.field == "native_status" for i in issues)
    for field in ("scope_and_nonclaims", "source_snapshot_refs"):
        record, issues = intake_envelope(
            make_payload(**{field: ["x"] * (MAX_JSON_NODES + 1)})
        )
        assert record is None
        assert any(i.field == field for i in issues)


@pytest.mark.parametrize(
    "field", ["line_id", "subject_id", "registry_version", "schema_version"]
)
def test_non_status_unicode_is_also_validated(field):
    record, issues = intake_envelope(make_payload(**{field: "\udfff"}))
    assert record is None
    assert any(i.field == field for i in issues)


def test_empty_payload_and_mixed_refusal_order_are_exhaustive():
    from witness_register import REQUIRED_FIELDS

    assert [i.field for i in intake_envelope({})[1]] == list(REQUIRED_FIELDS)
    payload = make_payload(line_id="", review_date="2026-02-30", native_status=(1, 2))
    del payload["report_ref"]
    assert [i.field for i in intake_envelope(payload)[1]] == [
        "line_id",
        "review_date",
        "native_status",
        "report_ref",
    ]


def test_direct_record_tampering_remains_detectable(envelope):
    first = genesis_state("subject-1", "2026-10-21", (envelope,))
    envelope.native_status["detail"].append("direct-record mutation")
    with pytest.raises(InvalidStateError, match="seal"):
        project(first, "u")
    assert verify_chain((first,))


@pytest.mark.parametrize("field", ["prior_state_ref", "parent_return_ref"])
def test_return_digest_entry_points_refuse_newlines(field):
    with pytest.raises(ValueError, match=field):
        make_contract(**{field: "a" * 64 + "\n"})


def test_relation_and_projection_digest_entry_points_refuse_newlines(envelope):
    with pytest.raises(ValueError, match="source_report_refs"):
        make_relation(envelope, source_report_refs=("a" * 64 + "\n",))
    with pytest.raises(ValueError, match="state_ref"):
        Projection(0, "u", "a" * 64 + "\n", ("held",))
    for field in ("support_refs", "resistance_refs"):
        invalid = raw_state(
            "s",
            "2026-10-21",
            (envelope,),
            (make_relation(envelope, **{field: ("a" * 64 + "\n",)}),),
        )
        with pytest.raises(InvalidStateError):
            project(invalid, "u")


def test_real_leap_day_backdating_and_declared_subject_correspondence(envelope):
    differently_named = replace(
        envelope, subject_id="another spelling", report_ref="c" * 64
    )
    first = genesis_state(
        "register-subject", "2028-02-29", (envelope, differently_named)
    )
    second = update_state(first, "2026-10-21")
    assert verify_chain((first, second)) == ()
    anchor = anchor_statement((first, second), "2028-03-01")
    assert anchor["tip_review_moment"] == "2026-10-21"
    assert anchor["anchored_on"] == "2028-03-01"


def test_fabricated_posture_can_bind_while_failing_replay(envelope):
    state = genesis_state(
        "subject-1",
        "2026-10-21",
        (envelope,),
        (make_relation(envelope, RelationType.NON_COMPENSATORY_BLOCK),),
    )
    invented = Projection(1, "u", state.state_digest, ("invented",))
    assert check_projection_binding(invented, state) == ()
    assert state_binding_fidelity(invented, state) == 1.0
    assert check_projection(invented, state)


def test_chain_segment_denominator_and_absent_external_anchor_are_visible(envelope):
    first = genesis_state("subject-1", "2026-10-19", (envelope,))
    second = update_state(first, "2026-10-20")
    third = update_state(second, "2026-10-21")
    report = chain_coverage((second, third))
    assert (report.preserved_links, report.total_links) == (1, 1)
    assert report.preservation_fraction == 1.0
    assert not report.genesis_covered and not report.full_chain_valid
    assert report.external_anchor_ref == ""
    whole = chain_coverage(
        (first, second, third), external_anchor_ref="operator-claim:log"
    )
    assert whole.genesis_covered and whole.full_chain_valid
    assert whole.total_links == 2
    assert whole.external_anchor_ref == "operator-claim:log"


def test_chain_subject_change_is_refused_even_with_complete_new_schema_seal(envelope):
    first = genesis_state("s", "2026-10-20", (envelope,))
    second = update_state(first, "2026-10-21")
    moved = replace(
        second,
        subject_id="t",
        state_digest=state_content_digest(
            "t",
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
    assert (
        check_projection_binding(
            Projection(0, "u", moved.state_digest, ("probe",)), moved
        )
        == ()
    )
    assert any("subject identity" in issue for issue in verify_chain((first, moved)))


def test_chain_projection_and_serialized_replay_inputs(envelope):
    first = genesis_state("s", "2026-10-20", (envelope,))
    second = update_state(first, "2026-10-21")
    result = project_chain((first, second), "u", "receipt-only")
    assert result == project(second, "u", "receipt-only")
    payload = json.loads(canonical_json(canonical_projection(result)))
    assert payload["human_decision_ref"] == "receipt-only"
    assert payload["reasons"] == list(result.reasons)
    with pytest.raises(InvalidStateError, match="genesis"):
        project_chain((second,), "u")
    with pytest.raises(InvalidStateError):
        project_chain((first, genesis_state("s", "2026-10-21")), "u")
    with pytest.raises(ValueError, match="empty chain"):
        project_chain((), "u")


def test_direct_non_json_payload_is_a_typed_structural_failure(envelope):
    first = genesis_state("s", "2026-10-21", (envelope,))
    invalid = replace(first, envelopes=(replace(envelope, native_status=(1, 2)),))
    with pytest.raises(InvalidStateError) as exc:
        project(invalid, "u")
    assert {i.code for i in exc.value.issues} >= {"ENVELOPE", "SEAL"}


def test_return_order_open_remainder_and_partial_ancestry_are_checked(envelope):
    contract = make_contract()
    partial = record_return(contract, "X returned", "Y due")
    child = remainder_contract(partial, "child")
    cases = (
        (partial, contract),
        (replace(contract, open_remainder="no return yet"),),
        (contract, child, partial),
        (contract, partial, replace(child, acceptance_condition="easier")),
    )
    for records in cases:
        invalid = raw_state("s", "2026-10-21", (envelope,), returns=records)
        assert check_state(invalid)
        with pytest.raises(InvalidStateError):
            project(invalid, "u")


@pytest.mark.parametrize("support_count", [0, 50])
def test_structural_failures_cannot_be_compensated_by_envelopes_or_agreements(
    envelope, support_count
):
    from witness_register import sha256_hex

    supporters = tuple(
        replace(envelope, report_ref=sha256_hex(f"supporter-{n}"))
        for n in range(support_count)
    )
    agreements = tuple(
        make_relation(e, relation_id=f"agreement-{n}") for n, e in enumerate(supporters)
    )
    contract = make_contract()
    done = record_return(contract, "received", "")
    bad_pairs = (
        (contract, replace(done, standing="another person")),
        (done,),
        (contract, done, done),
    )
    for records in bad_pairs:
        invalid = raw_state(
            "s", "2026-10-21", (envelope,) + supporters, agreements, returns=records
        )
        with pytest.raises(InvalidStateError):
            project(invalid, "u")


def test_json_bounds_cover_aggregate_container_nodes():
    from witness_register.json_data import json_domain_issues

    value = [[None] * 100 for _ in range(101)]
    assert any("node limit" in issue for issue in json_domain_issues(value))


def test_one_state_segment_report_does_not_invent_a_link(envelope):
    state = genesis_state("s", "2026-10-21", (envelope,))
    report = chain_coverage((state,))
    assert report.total_links == 0 and report.preservation_fraction == 1.0
    assert (
        chain_coverage((replace(state, state_digest="a" * 64),)).preservation_fraction
        == 0.0
    )
