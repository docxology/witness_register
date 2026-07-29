"""Relation, return-contract, and unclassified-holding record validation."""

from __future__ import annotations

import pytest
from conftest import make_contract, make_holding, make_payload, make_relation, accept

from witness_register import (
    NOT_RECORDED,
    RelationType,
    record_return,
    sha256_hex,
)


def test_a_relation_requires_a_non_blank_id(envelope) -> None:
    with pytest.raises(ValueError, match="relation_id"):
        make_relation(envelope, relation_id="  ")


def test_a_relation_about_nothing_is_refused(envelope) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        make_relation(envelope, source_report_refs=())


def test_a_relation_source_ref_must_be_an_envelope_shaped_digest(envelope) -> None:
    with pytest.raises(ValueError, match="hex"):
        make_relation(envelope, source_report_refs=("not-hex",))


def test_a_relation_requires_a_bounded_description(envelope) -> None:
    with pytest.raises(ValueError, match="bounded_description"):
        make_relation(envelope, bounded_description="")


def test_a_relation_type_must_be_typed(envelope) -> None:
    with pytest.raises(ValueError, match="RelationType"):
        make_relation(envelope, relation_type="AGREES")


def test_human_decision_defaults_to_not_recorded(envelope) -> None:
    relation = make_relation(envelope)
    assert relation.human_decision_ref == NOT_RECORDED
    assert relation.human_decision_ref == ""
    assert relation.promoted_from_ref == ""


def test_the_relation_vocabulary_is_the_published_eight() -> None:
    assert {member.value for member in RelationType} == {
        "NON_COMPENSATORY_BLOCK",
        "UNRESOLVED_DEPENDENCY",
        "PROTECTED_ABSENCE",
        "DIRECTIONAL_TENSION",
        "UNCLASSIFIED_OBSERVATION",
        "RETURN_DUE",
        "CANNOT_COMPARE",
        "AGREES",
    }


def test_a_contract_requires_its_load_bearing_fields() -> None:
    with pytest.raises(ValueError, match="contract_id"):
        make_contract(contract_id=" ")
    with pytest.raises(ValueError, match="why_held"):
        make_contract(why_held="")
    with pytest.raises(ValueError, match="trigger"):
        make_contract(trigger=" ")
    with pytest.raises(ValueError, match="acceptance_condition"):
        make_contract(acceptance_condition="")


def test_an_open_contract_is_not_met() -> None:
    contract = make_contract()
    assert contract.verification_result == ""
    assert contract.is_met is False


def test_record_return_refuses_a_blank_verification() -> None:
    with pytest.raises(ValueError, match="non-blank"):
        record_return(make_contract(), "  ", "")


def test_record_return_refuses_to_re_verify_a_completed_record() -> None:
    done = record_return(make_contract(), "the part came back", "")
    with pytest.raises(ValueError, match="already carries"):
        record_return(done, "again", "")


def test_a_partial_return_closes_only_the_verified_part() -> None:
    contract = make_contract()
    done = record_return(contract, "part X verified", "part Y remains open")
    assert done.verification_result == "part X verified"
    assert done.open_remainder == "part Y remains open"
    assert done.trigger == contract.trigger
    assert done.why_held == contract.why_held
    assert done.is_met is False
    # The open record is untouched: a new record was returned beside it.
    assert contract.verification_result == ""


def test_a_full_return_is_met() -> None:
    done = record_return(make_contract(), "everything came back dated", "")
    assert done.is_met is True


def test_a_holding_requires_content_and_a_reason() -> None:
    with pytest.raises(ValueError, match="held_id"):
        make_holding(held_id="")
    with pytest.raises(ValueError, match="raw_observation"):
        make_holding(raw_observation="  ")
    with pytest.raises(ValueError, match="reason_unclassified"):
        make_holding(reason_unclassified="")


def test_a_holding_keeps_the_observation_verbatim() -> None:
    text = "  raw, un-normalized, with   spacing  "
    assert make_holding(raw_observation=text).raw_observation == text


def test_envelope_payload_field_names_match_the_published_convention() -> None:
    """The intake consumes exactly the published field names, by value."""

    record = accept(make_payload(report_ref=sha256_hex("convention")))
    assert record.schema_version == "line.report-envelope/1.0"
