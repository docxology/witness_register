# Development and synchronization

Read [the validation contract](../AGENTS.md), [claim boundaries](claim_boundaries.md)
and [publication procedure](publication.md) before changing behavior.
Use the locked uv environment and preserve the Python floor in `pyproject.toml`.
Figures require a working `rsvg-convert` executable.

Install the project's complete locked development environment with
`uv sync --all-extras --all-groups` before running the gates. Use that
environment's Python and tools, not another project's interpreter: an unrelated
installed `scripts` package can shadow this repository's script namespace.
When checking a source checkout through a separate isolated environment, put
the checkout root and `src` on both the parent import path and child
`PYTHONPATH`; do not replace package namespaces with stand-ins.

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
Relation and return string fields require actual strings; reference surfaces
and live alternatives require immutable tuples of strings. False, zero,
containers, and other nonstring identities, remainders, or authority references
are structural defects (`RELATION_DOMAIN` or `RETURN_DOMAIN`). Shared domain
admission precedes identity counting, reference lookup, truthiness, and hashing;
it does not centralize or interpret any native evaluator.
Native envelope subject spelling need not equal the registrar's subject spelling.
Malformed JSON-compatible reference surfaces are preserved by raw serialization
instead of being iterated as if they were valid tuples. Valid canonical shapes
and schema identities are unchanged; this is stricter admission, not a new format.
`verify_chain` requires a genesis and checks actual append context. Local state
validation cannot prove that external history or an anchor is complete/current.

Run every command in [AGENTS.md](../AGENTS.md). After touching figures, build
twice and compare every artifact byte for byte. Regenerate the formalism ledger
with `uv run python scripts/gen_formalism_ledger.py`; its tracked output must
match. Render through the separate engine described in
[STANDALONE.md](../STANDALONE.md) and inspect the rendered artifacts.

Release packets record measured commands, sibling commit/tag provenance and
artifact digests. Preserve prior packets and fixture custody. Refresh siblings
from immutable release exports into a new versioned cohort, invoking each exporter
separately and storing only its published envelope by value. Never overwrite a
retained historical envelope or manifest. Exported-byte custody and report-pointer
syntax do not establish native correspondence, freshness, or shared subject identity.

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
