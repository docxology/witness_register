# Development and synchronization

Read [the validation contract](../AGENTS.md), [claim boundaries](claim_boundaries.md)
and [publication procedure](publication.md) before changing behavior.
Use the locked uv environment and preserve the Python floor in `pyproject.toml`.
Figures require a working `rsvg-convert` executable.

Use the [locked setup and native gates](quickstart.md#native-verification)
from the source checkout to keep its scripts and package imports together.

For a behavior defect, first run a regression that fails on the existing
implementation. Keep the positive and planted-defect controls. Change the API,
tests, architecture, manuscript, claim ledger and figure captions together.
Derived numbers belong in executable bindings, not an independent manual count.
New serialized shapes require a versioned schema and migration rules; see
[the review ledger](review-20261020.md).

`genesis_state` and `update_state` validate structure. `raw_state` only seals
inspectable imports and defect fixtures. `project` repeats validation and raises
`InvalidStateError` with typed issues, retaining the raw records for inspection.
Relation, return, envelope, and holding string fields require actual strings;
reference surfaces, live alternatives, and candidate readings require immutable
tuples of strings. Envelope `native_status` remains opaque JSON and is checked
by the existing intake path, never by a status vocabulary. False, zero,
containers, and other nonstring identities, provenance, remainders, or authority
references are structural defects (`RELATION_DOMAIN`, `RETURN_DOMAIN`,
`ENVELOPE_DOMAIN`, or `HOLDING_DOMAIN`). Shared domain admission precedes local
identity counting, reference lookup, truthiness, and seal validation; it does
not centralize or interpret any native evaluator.
Native envelope subject spelling need not equal the registrar's subject spelling.
Malformed JSON-compatible sequence surfaces are preserved by raw serialization
instead of being iterated as if they were valid tuples. Transport intake still
accepts lists or tuples and produces tuple fields; direct raw records must have
their declared tuple domains before validated admission. Raw sealing is not
admission. Valid canonical bytes and schema identities are unchanged; this is
stricter admission, not a new format. Envelope intake remains open-shaped:
unknown payload keys are not stored record fields, and stored `record_schema`
wrappers still replay through intake.
`verify_chain` requires a genesis and checks actual append context. Local state
validation cannot prove that external history or an anchor is complete/current.

Run every command in [AGENTS.md](../AGENTS.md). After touching figures, build
twice and compare every artifact byte for byte. Regenerate the formalism ledger
with `uv run python scripts/gen_formalism_ledger.py`; its tracked output must
match. Render through the separate engine described in
[the pinned render guide](quickstart.md#render-the-manuscript) and inspect the rendered artifacts.

Release packets record measured commands, sibling commit/tag provenance and
artifact digests. Preserve prior packets and fixture custody. Refresh siblings
from immutable release exports into a new versioned cohort, invoking each exporter
separately and storing only its published envelope by value. Never overwrite a
retained historical envelope or manifest. Exported-byte custody and report-pointer
syntax do not establish native correspondence, freshness, or shared subject identity.

Inspect every validation result and the rendered-provenance receipt after
following the render guide. Record failed runs alongside the successful
receipt. The engine's own infrastructure tests are a separate check.
