# Witness Register documentation

The Shared Witness Register: co-registration without aggregation.

The executable source is under [`../src/witness_register/`](../src/witness_register/);
the manuscript explains its design, formalism, and limits.

## Documents

- [architecture.md](architecture.md) — system design and module map
- [claim_boundaries.md](claim_boundaries.md) — what each claim asserts and does not assert
- [correspondence.md](correspondence.md) — design review feedback and responses
- [publication.md](publication.md) — publication metadata and release history

## Quick reference

```bash
# Run all tests
uv run pytest tests/ --cov=src --cov-fail-under=90

# Build figures
uv run python scripts/build_figures.py

# Re-render manuscript (from template repo)
cd /path/to/template
uv run python scripts/pipeline/stage_03_render.py --project working/witness_register
```

See [AGENTS.md](AGENTS.md) for the working contract.
