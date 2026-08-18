# Script contract

Every file in `scripts/` is a thin CLI over `src/`. Business logic belongs in
`src/witness_register/`, not here.

## Files

- `build_figures.py` — calls `witness_register.figures.build_figures()` and prints the output paths

## Canonical commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
uv run ruff check src tests scripts && uv run ruff format --check src tests scripts
uv run python scripts/build_figures.py
```
