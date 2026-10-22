# Development and synchronization

Read [the validation contract](../AGENTS.md), [claim boundaries](claim_boundaries.md)
and [publication procedure](publication.md) before changing behavior.
Use the locked uv environment and preserve the Python floor in `pyproject.toml`.
Figures require a working `rsvg-convert` executable.

Type check: `uv run mypy src/witness_register --check-untyped-defs`.

For a behavior defect, first run a regression that fails on the existing
implementation. Keep the positive and planted-defect controls. Change the API,
tests, architecture, manuscript, claim ledger and figure captions together.
Derived numbers belong in executable bindings, not an independent manual count.
New serialized shapes require a versioned schema and migration rules; see
[the review ledger](review-20261020.md).

`genesis_state` and `update_state` validate structure. `raw_state` only seals
inspectable imports and defect fixtures. `project` repeats validation and raises
`InvalidStateError` with typed issues, retaining the raw records for inspection.
`verify_chain` requires a genesis and checks actual append context. Local state
validation cannot prove that external history or an anchor is complete/current.

Run every command in [AGENTS.md](../AGENTS.md). After touching figures, build
twice and compare every artifact byte for byte. Regenerate the formalism ledger
with `uv run python scripts/gen_formalism_ledger.py`; its tracked output must
match. Render through the separate engine described in
[STANDALONE.md](../STANDALONE.md) and inspect the rendered artifacts.

Release packets record measured commands, sibling commit/tag provenance and
artifact digests. Preserve prior packets and fixture custody. Refresh siblings
from immutable release exports, invoking each exporter separately and storing
only its published envelope by value.

Run the existing publication stages from an isolated engine checkout, with a
real release-snapshot clone at `projects/active/witness_register`:

```bash
uv run --no-sync python scripts/pipeline/stage_03_render.py --project active/witness_register
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project active/witness_register
```

Build the project's figures first. Inspect every validation result and the
rendered-provenance receipt, not only the process exit code. The engine's
own infrastructure test suite is a distinct additional check; it does not
replace any repository or publication gate. Preserve failed attempts as
failures. No project pipeline override or engine waiver is required.
