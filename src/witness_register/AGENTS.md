# `witness_register` package

A sixth work beside the line set: append-only co-registration of report envelopes,
typed cross-line relations, and a bounded posture that never erases the state.

## Modules

- `__init__.py` — public API surface and non-claims
- `state.py` — genesis, update_state, verify_chain, append-only contract
- `projection.py` — project() with fixed precedence and reasons
- `battery.py` — run_battery and per-case defeat
- `envelopes.py` — intake_envelope validation
- `relations.py` — RelationRecord, RelationType, ReturnContractRecord
- `returns.py` — return contract lifecycle
- `held.py` — held observation and unclassified records
- `invariants.py` — structural checks and planted-bad cases
- `metrics.py` — recoverability, fidelity, and composite metrics
- `serialization.py` — canonical JSON and registry digest
- `figures.py` — deterministic figure plates and cover art
- `version.py` — single source of truth for the package version

## Invariants

1. No line imports. Envelopes arrive by value, not by import.
2. No interpretation of `native_status`. Projection is driven by relation records only.
3. Append-only history. `update_state` fails closed on tampering.
4. No auto-categories. Promotion requires a non-empty `human_decision_ref`.
5. The posture is bounded: only `-1 | 0 | +1`, only with a declared next use.

Validation: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
