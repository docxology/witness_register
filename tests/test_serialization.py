"""Serialization determinism and schema-string discipline."""

from __future__ import annotations

import json

from conftest import accept, make_contract, make_holding, make_payload, make_relation

from witness_register import (
    ENVELOPE_RECORD_SCHEMA,
    PROJECTION_SCHEMA,
    RELATION_SCHEMA,
    RETURN_CONTRACT_SCHEMA,
    STATE_SCHEMA,
    UNCLASSIFIED_SCHEMA,
    canonical_envelope,
    canonical_json,
    canonical_relation,
    canonical_return_contract,
    canonical_state_payload,
    canonical_unclassified,
    envelope_digest,
    genesis_state,
    payload_digest,
    relation_digest,
    return_contract_digest,
    sha256_hex,
    unclassified_digest,
)


def test_canonical_json_is_key_order_independent() -> None:
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert canonical_json({"a": 2, "b": 1}) == '{"a":2,"b":1}'


def test_canonical_json_preserves_non_ascii() -> None:
    assert canonical_json({"note": "zażółć"}) == '{"note":"zażółć"}'


def test_sha256_hex_shape_and_determinism() -> None:
    digest = sha256_hex("witness")
    assert len(digest) == 64
    assert digest == sha256_hex("witness")
    assert digest != sha256_hex("witness ")


def test_every_schema_string_is_namespaced_per_shape() -> None:
    schemas = {
        ENVELOPE_RECORD_SCHEMA,
        RELATION_SCHEMA,
        RETURN_CONTRACT_SCHEMA,
        UNCLASSIFIED_SCHEMA,
        STATE_SCHEMA,
        PROJECTION_SCHEMA,
    }
    assert len(schemas) == 6
    for schema in schemas:
        assert schema.startswith("witness-register.")
        assert schema.endswith("/1.0")


def test_record_digests_are_deterministic_and_distinct(envelope) -> None:
    relation = make_relation(envelope)
    contract = make_contract()
    holding = make_holding()
    digests = {
        envelope_digest(envelope),
        relation_digest(relation),
        return_contract_digest(contract),
        unclassified_digest(holding),
    }
    assert len(digests) == 4
    assert envelope_digest(envelope) == envelope_digest(accept(make_payload()))


def test_canonical_forms_carry_their_schema_string(envelope) -> None:
    assert canonical_envelope(envelope)["record_schema"] == ENVELOPE_RECORD_SCHEMA
    assert (
        canonical_relation(make_relation(envelope))["record_schema"] == RELATION_SCHEMA
    )
    assert (
        canonical_return_contract(make_contract())["record_schema"]
        == RETURN_CONTRACT_SCHEMA
    )
    assert (
        canonical_unclassified(make_holding())["record_schema"] == UNCLASSIFIED_SCHEMA
    )


def test_canonical_forms_round_trip_through_json(envelope) -> None:
    payload = canonical_state_payload(
        "subject-1",
        "2026-07-29",
        (envelope,),
        (make_relation(envelope),),
        (make_holding(),),
        (make_contract(),),
        "",
    )
    assert json.loads(canonical_json(payload)) == payload
    assert payload["record_schema"] == STATE_SCHEMA


def test_state_digest_binds_record_order(envelope, second_envelope) -> None:
    """Append-only means order is content; reordering changes the digest."""

    forward = canonical_state_payload(
        "subject-1", "2026-07-29", (envelope, second_envelope), (), (), (), ""
    )
    reversed_order = canonical_state_payload(
        "subject-1", "2026-07-29", (second_envelope, envelope), (), (), (), ""
    )
    assert payload_digest(forward) != payload_digest(reversed_order)


def test_state_seal_matches_a_recomputed_payload_digest(envelope) -> None:
    state = genesis_state("subject-1", "2026-07-29", (envelope,))
    payload = canonical_state_payload(
        "subject-1", "2026-07-29", (envelope,), (), (), (), ""
    )
    assert state.state_digest == payload_digest(payload)


def test_native_status_survives_canonicalization_verbatim() -> None:
    record = accept(make_payload(native_status=[["r1", "NAMED"], ["r2", "WITHHELD"]]))
    assert canonical_envelope(record)["native_status"] == [
        ["r1", "NAMED"],
        ["r2", "WITHHELD"],
    ]
