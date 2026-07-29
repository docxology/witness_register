# TODO

Open items, each with the reason it is open. Dates are real.

## Open (2026-07-29)

- **Scholarship: SHIPPED (2026-07-29, third window)** — six traditions
  cited with every bibliographic record verified against Crossref, the RFC
  Editor, or the W3C before use (see `manuscript/02b_scholarship.md`).
  Still open: a deeper reading pass could add the audit-culture and
  documentality literatures the sibling works carry; nothing is cited from
  memory, so those wait for a real reading session.
- **Figures: BUILT (2026-07-29, third window)** — see CHANGELOG. What
  remains open here is only the greyscale-print human check the siblings
  also carry: no person has yet read the three plates in a greyscale print.
  The original sibling-grade spec this entry carried is satisfied: builder
  with registry (interpretive claim + epistemic boundary per plate),
  rendered-point legibility floor derived from the manuscript geometry and
  gated by test, double-build byte-identity, plates drawn from live calls.
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

## Done (2026-07-29)

- **Per-line worked example over real exports** — `data/envelopes/` (four
  records with provenance README) + `tests/test_worked_example.py`; see
  CHANGELOG second window. The narrower "adapter recipes" item is subsumed:
  the provenance README records the exact per-line command that produced
  each export.
- **Manuscript formalism window** — `manuscript/02a_formalism.md` bound by
  `tests/test_formalism.py`, drifts planted and caught, re-rendered green.


- **Render verification.** First render through the external
  `docxology/template` engine completed 2026-07-29: a valid PDF with zero
  undefined references, full validation pass. The engine needed nothing this
  repository lacked; the only findings were five bare-URL markdown warnings
  in `manuscript/99_references.md`, fixed the same day. PDF staged to
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
