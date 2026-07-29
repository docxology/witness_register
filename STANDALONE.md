# witness_register as a separated copy

This repository is the whole of the Shared Witness Register. It carries its
own Python package, tests, documentation, and manuscript sources. It is a
sixth work standing BESIDE the line set, and — by design more than any
sibling — it is complete on its own: its entire architecture is that the
lines' reports arrive by value, never by import.

## What a separated copy is

The five sibling works —
[red_line](https://github.com/docxology/red_line),
[black_line](https://github.com/docxology/black_line),
[golden_line](https://github.com/docxology/golden_line),
[white_line](https://github.com/docxology/white_line), and the set reader
[line_set](https://github.com/docxology/line_set) — live in their own
repositories. A separated copy of this one is a clone held on its own, with
no sibling checkout beside it and no monorepo around it. This document
states what that copy can do and what it cannot.

## What it can do alone

From a clone of this repository and nothing else:

- Install: `pyproject.toml` declares `dependencies = []`. The package is
  pure standard library on Python 3.10 or later; the `dev` group is
  `pytest`, `pytest-cov`, and `ruff`. `uv.lock` is tracked, so `uv sync`
  reproduces the pinned development environment.
- Run the full test suite and meet the branch-coverage gate
  (`fail_under = 90`), including the 3×3 witness battery, the 12-defect
  invariant battery, and every positive control.
- Intake any envelope that follows the published
  `line.report-envelope/1.0` shape — from a line repository, from a file,
  or hand-built — because the contract is a data shape, not a dependency.

No module in `src/witness_register/` imports a sibling work, and no path in
this repository resolves above its own root; `tests/test_standalone.py`
enforces both with positive controls.

## What it cannot do alone

**Render the publication bundle.** `output/pdf/witness_register_combined.pdf`
and the web bundle are written by the `docxology/template` render engine,
which is a separate repository and is not vendored here. This is a declared
external dependency, not a hidden one: nothing in `src/` produces or reads
those files, and no test fails when they are absent.

**Verify a chain tip against the world.** The code states this limitation
itself: an append-only chain's tip is unbound without EXTERNAL anchoring.
`seal_tip` hands you the digest; anchoring it is your infrastructure's job,
not this package's claim.

**Fetch a line's native report.** An envelope's `report_ref` is a digest
pointer. Dereferencing it requires the exporting line's repository or
archive; the register stores the pointer and the non-claims that rode with
it, nothing more.
