# Scripts

Thin build entry points. No business logic here — import from `witness_register.*`.

## Quick reference

- `build_figures.py` — regenerate all figure SVGs, PNGs, and `figure_registry.json`
  ```bash
  uv run python scripts/build_figures.py
  ```
- `gen_formalism_ledger.py` — regenerate `data/formalism_claim_ledger.json` from the manuscript and package
  ```bash
  uv run python scripts/gen_formalism_ledger.py
  ```

See [AGENTS.md](AGENTS.md) for the working contract.
## Release cohort replay

`uv run python scripts/build_release_cohort.py data/envelopes/releases/v0.2.0`
checks exported byte custody, intakes by value, and writes deterministic
`co_registration.json`. The manifest records immutable sibling sources;
historical envelope collections remain unchanged.
