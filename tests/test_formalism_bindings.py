"""Bind every 02d_formalism.md block to executed register behavior.

Each test here first *derives* behavior by running the real code, then
asserts the manuscript states exactly that. The binding table in 02d is
keyed on each block's *label*, never on its number. Two gates police the
table: one requires the row set to equal the declared block set, the other
requires each row to name a test that exists.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

from witness_register import (
    EnvelopeRecord,
    RelationRecord,
    RelationType,
    ReturnContractRecord,
    WitnessState,
    genesis_state,
    intake_envelope,
    project,
    record_return,
    update_state,
    verify_chain,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMALISM_2A = PROJECT_ROOT / "manuscript" / "02a_formalism.md"
FORMALISM_2D = PROJECT_ROOT / "manuscript" / "02d_formalism.md"
CLAIM_LEDGER = PROJECT_ROOT / "data" / "claim_ledger.yaml"

_TEST_REF = re.compile(r"tests/[\w/]+\.py::\w+")
_ROW_LABEL = re.compile(r"^\|\s*\[@((?:def|prop):[\w-]+)\]\s*\|")


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _binding_table_rows() -> list[tuple[str, str]]:
    """Return ``(block label, verifying-test cell)`` for every table row in 02d."""
    rows: list[tuple[str, str]] = []
    for line in FORMALISM_2D.read_text(encoding="utf-8").splitlines():
        match = _ROW_LABEL.match(line)
        if match is None:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 4, line
        rows.append((match.group(1), cells[2]))
    return rows


def _formalism_2d_labels() -> list[str]:
    """Every proposition label declared in 02d_formalism.md, in document order."""
    labels: list[str] = []
    for line in FORMALISM_2D.read_text(encoding="utf-8").splitlines():
        match = re.search(r"#(prop:[\w-]+)", line)
        if match:
            labels.append(match.group(1))
    return labels


# --------------------------------------------------------------------------- gates


def test_binding_tables_bind_every_declared_block() -> None:
    """The row set must equal the declared block set -- no gaps, no orphans."""
    labels = _formalism_2d_labels()
    assert labels, "no proposition blocks parsed, so this gate would be vacuous"
    rows = _binding_table_rows()
    assert [label for label, _cell in rows] == labels


def test_every_binding_row_names_an_existing_test() -> None:
    """Per row: at least one verifying test is named, and every name resolves."""
    rows = _binding_table_rows()
    assert rows, "no table rows parsed, so this gate would be vacuous"

    for label, cell in rows:
        row_refs = _TEST_REF.findall(cell)
        assert row_refs, f"{label} names no verifying test"

    all_refs = set(_TEST_REF.findall(FORMALISM_2D.read_text(encoding="utf-8")))
    for ref in sorted(all_refs):
        rel_path, function_name = ref.split("::")
        test_file = PROJECT_ROOT / rel_path
        assert test_file.is_file(), ref
        assert f"def {function_name}(" in test_file.read_text(encoding="utf-8"), ref


# --------------------------------------------------------------------------- verifying tests


def _valid_envelope() -> EnvelopeRecord:
    payload = {
        "schema_version": "line.report-envelope/1.0",
        "line_id": "black_line",
        "subject_id": "s",
        "review_date": "2026-07-29",
        "registry_version": "1.0",
        "registry_digest": "a" * 64,
        "native_status": "OPAQUE",
        "report_ref": "b" * 64,
        "source_snapshot_refs": ["snap"],
        "scope_and_nonclaims": ["a boundary"],
    }
    record, issues = intake_envelope(payload)
    assert record is not None, issues
    return record


def test_chain_verification_checks_every_state() -> None:
    """verify_chain checks digests, linkage, and record preservation for every state."""
    envelope = _valid_envelope()
    g = genesis_state("s", "2026-07-29", envelopes=(envelope,))
    u = update_state(g, "2026-07-30")
    chain = (g, u)

    # A sound chain produces no violations.
    assert verify_chain(chain) == ()

    # A mutated state fails verification.
    mutated = dataclasses.replace(g, state_digest="0" * 64)
    violations = verify_chain((mutated, u))
    assert len(violations) >= 1
    assert any("content does not match its seal" in v for v in violations)

    # A state that dropped a prior record fails.
    dropped = genesis_state("s", "2026-07-30")
    chain_with_drop = (g, dropped)
    violations = verify_chain(chain_with_drop)
    assert len(violations) >= 1
    assert any("dropped" in v or "reordered" in v or "altered" in v for v in violations)

    text = _normalized(FORMALISM_2D)
    assert "verification never repairs" in text
    assert "every event in the chain is verifiable" in text


def test_return_contract_constrains_projection_across_chains() -> None:
    """Return contracts constraint the projection; partial returns do not close."""
    envelope = _valid_envelope()

    # A state with a RETURN_DUE relation and no human decision.
    ret_due = RelationRecord(
        relation_id="rd1",
        subject_id="s",
        source_report_refs=(envelope.report_ref,),
        relation_type=RelationType.RETURN_DUE,
        bounded_description="material needs return",
        return_contract_ref="rc1",
    )
    contract = ReturnContractRecord(
        contract_id="rc1",
        subject_id="s",
        why_held="needs evidence",
        alternatives_live=(),
        change_condition="evidence arrives",
        standing="any",
        protected="",
        trigger="on receipt of evidence",
        acceptance_condition="evidence is verifiable",
    )
    state = genesis_state(
        "s",
        "2026-07-29",
        envelopes=(envelope,),
        relations=(ret_due,),
        returns=(contract,),
    )
    # With an unmet return, no human decision, posture should be held at 0.
    result = project(state, "u")
    assert result.value == 0
    assert any("return_due" in r for r in result.reasons)

    # A partial return does not close the obligation.
    partial_return = record_return(
        contract,
        verification_result="partially verified",
        open_remainder="remaining part",
    )
    state_with_partial = genesis_state(
        "s",
        "2026-07-29",
        envelopes=(envelope,),
        relations=(ret_due,),
        returns=(contract, partial_return),
    )
    result_partial = project(state_with_partial, "u")
    assert result_partial.value == 0
    assert any("return_due" in r or "outstanding" in r for r in result_partial.reasons)

    text = _normalized(FORMALISM_2D)
    assert "partial return with a non-empty remainder does not close" in text


def test_projection_is_deterministic_for_identical_inputs() -> None:
    """Identical state and use produce identical Projection every time."""
    envelope = _valid_envelope()
    state = genesis_state("s", "2026-07-29", envelopes=(envelope,))

    r1 = project(state, "use_x")
    r2 = project(state, "use_x")
    r3 = project(state, "use_x")

    assert r1.value == r2.value == r3.value
    assert r1.state_ref == r2.state_ref == r3.state_ref
    assert r1.reasons == r2.reasons == r3.reasons
    assert r1.declared_next_use == r2.declared_next_use == r3.declared_next_use

    # Different use can produce different value (not determinism's concern).
    r4 = project(state, "different_use")
    # But same state, same use must always agree.
    assert project(state, "different_use") == r4

    text = _normalized(FORMALISM_2D)
    assert (
        "identical `Projection` value" in text or "identical projection" in text.lower()
    )


# --------------------------------------------------------------------------- claim ledger


def _ledger_number(claim_id: str) -> int:
    raw = CLAIM_LEDGER.read_text(encoding="utf-8")
    match = re.search(
        rf"- id: {re.escape(claim_id)}\n\s+kind: number\n\s+value: (\d+)",
        raw,
    )
    assert match is not None, claim_id
    return int(match.group(1))


def test_all_manuscript_references_to_tests_resolve() -> None:
    """Every `tests/...` reference anywhere in the manuscript names a real file.

    The binding-table gate above covers 02d_formalism.md; this one extends
    the same guarantee to prose elsewhere in the manuscript. A reference to a
    battery test that does not exist is exactly the kind of drift a reader
    would trust and a maintainer would miss — it must fail, not pass review.

    A reference may stop at the file (``tests/test_battery.py``) or name a
    function (``tests/test_battery.py::run_battery_defeat``). Both must
    resolve, so a renamed or deleted test cannot leave a stale pointer.
    """

    import re as _re

    ref = _re.compile(r"tests/[A-Za-z0-9_./]+?\.py(?:[A-Za-z0-9_:/]*)?")
    all_text = "".join(
        path.read_text(encoding="utf-8")
        for path in PROJECT_ROOT.glob("manuscript/*.md")
    )
    found = set(ref.findall(all_text))
    assert found, "no tests/ references parsed; the gate would be vacuous"

    for token in sorted(found):
        file_part = token.split("::", 1)[0]
        test_file = PROJECT_ROOT / file_part
        assert test_file.is_file(), f"{token}: no such test file"
        if "::" in token:
            function_name = token.split("::", 1)[1]
            assert function_name, f"{token}: empty function name"
            assert f"def {function_name}(" in test_file.read_text(encoding="utf-8"), (
                f"{token}: no such function in {file_part}"
            )


def test_claim_ledger_numbers_match_executed_sources() -> None:
    """The evidence ledger cannot lag behind the executable facts."""
    import inspect
    from witness_register import RelationType
    from witness_register.projection import witness_hold_reasons

    # The hold reason kinds are string literals in witness_hold_reasons;
    # extract them from the source rather than constructing a state.
    source = inspect.getsource(witness_hold_reasons)
    hold_kinds = set(re.findall(r'kind="(\w+)"', source))
    assert hold_kinds, "no hold reason kinds found — regex may need updating"

    return_contract = dataclasses.fields(ReturnContractRecord)

    expected = {
        "envelope_field_count": len(dataclasses.fields(EnvelopeRecord)),
        "witness_state_field_count": len(dataclasses.fields(WitnessState)),
        "relation_type_count": len(RelationType),
        "return_contract_field_count": len(return_contract),
        "projection_codomain_count": 3,
        "hold_reason_categories_count": len(hold_kinds),
    }
    for claim_id, value in expected.items():
        assert _ledger_number(claim_id) == value, claim_id
