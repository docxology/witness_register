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

`uv run python scripts/build_release_cohort.py data/envelopes/releases/v0.4.0-element-admission`
checks exported byte custody, strict JSON, envelope shape and line attribution,
then writes deterministic `co_registration.json`. The release owner first
produces ten real native exports from actual final producer sources and
authors their manifest. The directory argument is required: no default command
rewrites a retained cohort.

Seven public native exports carry actual disclosed producer custody and
executed recipes. Copper, Iron, and Violet contribute separately
disclosure-reviewed synthetic exports with empty source references. Their
public manifest entries contain no private commit, tree, source path, or
export recipe; full native provenance and replay evidence stay private.
See the [complete authoring contract](../data/envelopes/README.md).

Set `classification_decision_ref` to the new registrar's explicit nonblank string
reference. Missing, blank, or nonstring references are refused for new cohorts;
the builder never invents a historical authority for them. The only missing-field
exception matches the SHA-256 of the entire exact retained v0.2.0 manifest bytes,
not a directory name or editable cohort label. That manifest binds its full
historical identity and producer custody; each exported byte hash is still checked.
Even a reformatted or extended copy needs an authored reference. The unchanged
historical manifest can replay after relocation without changing stored bytes.
The builder records authored incomparability and a correspondence return obligation,
not native correspondence or freshness. Status remains opaque and cannot clear
these holds. Historical collections, subjects, dates and exported bytes remain
unchanged; the ten-member edition is never inferred from the citation roster.
