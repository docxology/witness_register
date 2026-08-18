# Test folder contract

`tests/` exercises the public API, state chain, projection, battery, figure
determinism, intake validation, manuscript bindings, and cross-cutting contracts.

## Test modules

- `test_api.py` — imports, version markers, public surface
- `test_state.py` — genesis, update, verify_chain, seal, tamper refusal
- `test_projection.py` — project() posture invariants and precedence
- `test_battery.py` — run_battery and per-case injected-wrong defeat
- `test_envelopes.py` — intake_envelope validation and error paths
- `test_records.py` — record-level invariants and serialization
- `test_serialization.py` — canonical JSON and registry digest
- `test_invariants.py` — structural checks and planted-bad cases
- `test_metrics.py` — recoverability, fidelity, and composite metrics
- `test_formalism.py` — formalism block parsing and label resolution
- `test_register_figures.py` — every plate is embedded with its registered caption
- `test_worked_example.py` — the four real stored envelopes, end to end
- `test_same_subject.py` — same-subject co-registration contract
- `test_publication_metadata.py` — publication metadata across config and package
- `test_standalone.py` — the package works without sibling repos
- `test_wave3_hardening.py` — wave-3 hardening contracts
- `test_no_mocks.py` — lexical ban on mocks, stand-in names, path hardcodes

## Invariants

- No mocks. Use real records, temporary output roots, and constructed states.
- Keep project coverage at or above the `90` floor in `pyproject.toml`.
- Import figure builders from `witness_register.figures`, not from `scripts/`.

## Validation

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
```
