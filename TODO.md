# TODO

Open items, each with the reason it is open. Dates are real.

## Open (2026-08-01)

- **Scholarship: SHIPPED (2026-07-29, third window)** — six traditions
  cited with every bibliographic record verified against Crossref, the RFC
  Editor, or the W3C before use (see `docs/manuscript/02b_scholarship.md`).
  Still open: a deeper reading pass could add the audit-culture and
  documentality literatures the sibling works carry; nothing is cited from
  memory, so those wait for a real reading session.
- **Figures: BUILT (2026-07-29, third window); geometry re-derived and
  visual gaps closed (2026-08-01, assessment pass)** — see CHANGELOG. What
  remains open here is only the grayscale-print human check the siblings
  also carry: no person has yet read the plates in a grayscale print. The
  2026-08-01 pass re-derived the legibility floor to the manuscript's
  current 0.33 in side margins (7.84 in text block, 6.35 pt rendered),
  right-anchored the cover's edge labels so they no longer clip, bounded the
  projection plate's reason column within its cells, and added a test that
  no text run may overflow its canvas.
- **External anchoring of the chain tip — code side prepared
  (2026-07-29): `anchor_statement` verifies the chain and returns the
  byte-stable portable record to store elsewhere.** Which external system
  receives it (a signed note, an independent log, another repository's
  history) was decided 2026-07-29: a dedicated
  append-only anchors repository (`../anchors`, its own git history, no
  code). The first two anchors are stored there — the worked chain at
  length 3 (tip `5c8aaa1d8674…`, including the completed return) and the
  same-subject chain at length 2 (tip `a3d87025dbce…`). The limitation's
  first instance is closed for the local set; anchoring in a system outside
  this machine entirely (a remote, a signed note) remains open.

## Done (2026-08-01 assessment pass)

- **Legibility-floor claim drift repaired.** The publication pass tightened
  the manuscript geometry to `0.33` in side margins but the figure test and
  docstring still assumed `0.42` in / 7.66 in / 6.20 pt. Both re-derived to
  the config's one source. See CHANGELOG "0.1.0 — 2026-07-29 (autonomous
  assessment pass, 2026-08-01)".
- **Broken manuscript test references fixed.** Prose twice cited
  `tests/test_witness_battery.py`; the battery lives in
  `tests/test_battery.py`. A truncated sentence in `03_examples.md` was
  completed.
- **Figure-visualization gaps closed.** Projection plate reason column and
  value chips bounded within their cells; cover's right-edge labels
  right-anchored so `LIVING REGISTER` and the footer no longer clip at
  x=1500 on the 1600-wide canvas.
- **Gates added for the found bug classes.** New tests: every `tests/...`
  reference in the manuscript must resolve to a real file/function; no text
  run may overflow its canvas. Release packet updated to the measured tree.

## Done (2026-07-29)

- **Per-line worked example over real exports** — `data/envelopes/` (four
  records with provenance README) + `tests/test_worked_example.py`; see
  CHANGELOG second window. The narrower "adapter recipes" item is subsumed:
  the provenance README records the exact per-line command that produced
  each export.
- **Manuscript formalism window** — `docs/manuscript/02a_formalism.md` bound by
  `tests/test_formalism.py`, drifts planted and caught, re-rendered green.


- **Render verification.** First render through the external
  `docxology/template` engine completed 2026-07-29: a valid PDF with zero
  undefined references, full validation pass. The engine needed nothing this
  repository lacked; the only findings were five bare-URL markdown warnings
  in `docs/manuscript/99_references.md`, fixed the same day. PDF staged to
  `~/Downloads/witness_register_combined_0.1.0_2026-07-29.pdf`.
- **Adversarial hardening pass** — see CHANGELOG "2026-07-29 hardening":
  four defects found and fixed (whitespace verification counted as met;
  NaN/Infinity laundering; `project` on rewritten history; format gate never
  run), one design point recorded in code (`subject_id` correspondence is
  declared, not checked), regression tests in
  `tests/test_wave3_hardening.py`, 157 passing.

- Package (11 modules), test suite with branch coverage gate, 3×3 witness
  battery with injected-wrong rejection, 12-defect invariant battery,
  docs (README, architecture, claim boundaries, correspondence, AGENTS,
  STANDALONE), minimal manuscript.

## Workflowz review — 2026-11-10

- [ ] **WR-20261110-01 — P2 — Preserve every accepted formalism-block kind in generated evidence provenance.**
  - **Outcome and evidence:** `citation_rows()` accepts nine prefixes (`def`, `prop`, `thm`, `lem`, `cor`, `rem`, `ax`, `clm`, and `ex`) at `src/witness_register/formalism_ledger.py:25-28`, but its derivation at `src/witness_register/formalism_ledger.py:38` calls every non-`def` block a “proposition.” Replace that lossy branch with an exhaustive prefix-to-kind mapping, so a theorem row says “theorem block,” a remark row says “remark block,” and likewise for every accepted prefix. Regenerate `data/formalism_claim_ledger.json` with `uv run python scripts/gen_formalism_ledger.py`; existing claim IDs, values, row order, and the `kind: citation` contract must remain unchanged.
  - **Behavioral acceptance probe (from repository root):** run `uv run python scripts/gen_formalism_ledger.py` and `uv run pytest tests/test_formalism_bindings.py -q`, then exercise generation against real temporary manuscript input:
    ```bash
    uv run python - <<'PY'
    from pathlib import Path
    from tempfile import TemporaryDirectory
    import witness_register.formalism_ledger as ledger

    expected = {
        "def": "definition", "prop": "proposition", "thm": "theorem",
        "lem": "lemma", "cor": "corollary", "rem": "remark",
        "ax": "axiom", "clm": "claim", "ex": "example",
    }
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "02a_formalism.md").write_text(
            "\n".join(f"::: {{#{kind}:probe-{kind}}}" for kind in expected),
            encoding="utf-8",
        )
        original = ledger.MS
        ledger.MS = root
        try:
            rows = ledger.citation_rows()
        finally:
            ledger.MS = original
    assert len(rows) == len(expected), rows
    for row in rows:
        prefix = row["value"].split(":", 1)[0]
        assert row["source"] == (
            "docs/manuscript/02a_formalism.md: "
            f"{expected[prefix]} block declared with this label"
        ), row
    print("all formalism block kinds survive ledger generation")
    PY
    ```
  - **Dependencies/constraints:** no dependency or Python-version change is needed. Use the repository’s real generator and temporary manuscript files rather than hand-editing generated JSON; retain the existing regex’s accepted vocabulary unless a separately evidenced schema change is intended.

- [ ] **WR-20261110-02 — P3 — Pin the repository development interpreter to Python 3.15.2 without narrowing package compatibility.**
  - **Outcome and evidence:** `.python-version:1` currently selects only the moving `3.15` minor series. Set it to the preferred exact development patch, `3.15.2`, so contributor and validation runs name one reproducible interpreter. This is a development-pin change only: `pyproject.toml:10` declares the package’s `>=3.11` compatibility floor, and `pyproject.toml:22-24` deliberately keeps Ruff syntax targeting aligned with that floor; both remain unchanged.
  - **Behavioral acceptance probe (from repository root):** run `uv run --python 3.15.2 python -c 'import sys; assert sys.version_info[:3] == (3, 15, 2), sys.version'` followed by `uv run --python 3.15.2 pytest tests/ --cov=src --cov-branch -q`. The first command must execute on CPython 3.15.2 and the complete real-record suite, including its branch-coverage gate, must pass there.
  - **Dependencies/constraints:** uv must be able to obtain CPython 3.15.2. Do not raise `requires-python`, change Ruff’s `py311` target, or upgrade dependencies as part of this pin. If a concrete deployment, fixture, dependency, or reproducibility constraint prevents 3.15.2, document that constraint instead of silently selecting another interpreter.
