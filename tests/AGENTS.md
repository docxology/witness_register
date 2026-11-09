# Test folder contract

`tests/` exercises the public API, state chain, projection, battery, figure
determinism, intake validation, installed consumers, and publication integrity.

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
- `test_formalism.py` — public intake and projection boundary behavior
- `test_register_figures.py` — figure geometry, deterministic builds, artifact custody
- `test_worked_example.py` — the historical stored export collection, end to end
- `test_same_subject.py` — same-subject co-registration contract
- `test_publication_metadata.py` — publication metadata across config and package
- `test_standalone.py` — isolated wheel/sdist-installed public APIs consume the
  actual ten-envelope cohort, verify chain seals and held projection, and retain
  opaque status, report references, nonclaims, and empty private-source references
  without checkout scripts, source paths, or sibling packages
- `test_wave3_hardening.py` — wave-3 hardening contracts

## Invariants

- No mocks. Use real records, temporary output roots, constructed states, and
  actual installed distributions; no lexical scanner substitutes for behavior.
- Keep project coverage at or above the `90` floor in `pyproject.toml`.
- Import figure builders from `witness_register.figures`, not from `scripts/`.

## Validation

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
```
