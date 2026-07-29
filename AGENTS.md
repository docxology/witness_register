# AGENTS.md — validation contract

Rules and gates for any agent (or human) working in this repository.

## The invariants that must survive any change

1. **No line imports.** No file under `src/` or `tests/` imports `red_line`,
   `black_line`, `golden_line`, `white_line`, or `line_set`. Envelopes arrive
   by value under the published schema string `line.report-envelope/1.0`,
   declared as this repository's own literal.
2. **No interpretation of `native_status`.** The register stores it verbatim
   and never parses, compares, ranks, averages, or merges it. Projection is
   driven only by relation records.
3. **No silent rejection.** Intake returns typed `IntakeIssue`s naming every
   defect.
4. **Append-only history.** `update_state` must contain every prior record
   unchanged and fail closed on tampering; completed returns are new records
   that close only their verified part.
5. **No auto-categories, no default verdicts.** Promotion requires a
   non-empty `human_decision_ref`; an empty ref means NOT_RECORDED.
6. **The posture is bounded and never travels alone.** Only `-1 | 0 | +1`,
   only with a declared next use, always carrying `state_ref` and reasons.
7. **No mocks.** `tests/test_no_mocks.py` enforces the lexical ban; tests use
   real records and real temp files.
8. **Every count and version has one source.** `version.py` is bound by test
   to `pyproject.toml`, `manuscript/config.yaml`, and `CHANGELOG.md`.

## Gates (run all, from this repository's root)

```bash
uv run python scripts/build_figures.py            # first: deterministic plates + registry (needs rsvg-convert)
uv run pytest tests/ --cov=src --cov-branch -q   # suite + branch coverage, fail_under=90
uv run ruff check src tests scripts               # lint (E4,E7,E9,F pinned in pyproject)
uv run ruff format --check src tests scripts      # formatting
```

Run the figure build twice when touching `figures.py` and byte-compare
`output/figures/` — two runs must be identical; `tests/test_register_figures.py`
gates the same property through temp directories.

The suite includes its own proof-of-detection layers; a change that makes a
guard undiscriminating fails the guard's positive control, not just review:

- `defect_battery()` — 12 planted structural defects, each must be detected.
- `run_battery(defeat=<case>)` — every 3×3 case must reject its
  injected-wrong variant.
- `tests/test_standalone.py` — link, gitignore, cd-escape, parents[], and
  sibling-import gates, each with a planted-defect control.

## Rendering (external, optional)

The publication bundle is written by the `docxology/template` render engine,
a separate repository; see [STANDALONE.md](STANDALONE.md). Nothing in this
repository produces `output/pdf/witness_register_combined.pdf` on its own.

## Editing rules

- Frozen dataclasses, full docstrings with non-claims, small modules —
  match the prose discipline of the sibling works.
- New reader-facing numbers must be derived or test-bound, never hand-kept.
- Sibling works are referenced by name + GitHub URL only.
- Dates in changelog/TODO entries are real dates; measured numbers come from
  commands actually run.
