# Scripts

Thin build entry points. No business logic here — import from `witness_register.*`.

## Quick reference

- `build_figures.py` — regenerate all figure SVGs, PNGs, and `figure_registry.json`
  ```bash
  uv run python scripts/build_figures.py
  ```
  The current registry schema is `witness-register.figure-registry/2.0`.
  Every plate, including the cover, supplies authored `alt_text`; consumers
  must read that field, not the retired `alt` key or a caption fallback.
  Figure metadata versioning does not change native register, projection,
  or report-envelope schemas. Retained release evidence is historical.
- `gen_formalism_ledger.py` — regenerate `data/formalism_claim_ledger.json` from the manuscript and package
  ```bash
  uv run python scripts/gen_formalism_ledger.py
  ```

See [AGENTS.md](AGENTS.md) for the working contract.
## Release cohort replay

`uv run python scripts/build_release_cohort.py data/envelopes/releases/v0.3.1-runtime-source-refresh`
checks exported byte custody, intakes by value, and writes deterministic
`co_registration.json`. The directory argument is required: no default command
rewrites a retained cohort. The current directory contains seven recomputed
public native exports and the unchanged approved synthetic Violet envelope,
with exact byte hashes, public producer commits, and native export recipes.
Violet's private producer custody is deliberately not published.
Set `classification_decision_ref` to the current registrar's explicit
classification reference; manifests without it retain the historical
2026-10-21 authority reference for byte-identical historical replay.
This records authored incomparability and a correspondence return obligation,
not native correspondence or freshness. Historical collections remain unchanged.
