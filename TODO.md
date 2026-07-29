# TODO

Open items, each with the reason it is open. Dates are real.

## Open (2026-07-29)

- **Full manuscript with scholarship and figures.** The current manuscript
  is a minimal honest core (problem, design, limits). A real scholarly
  treatment — provenance/witness literature, append-only log literature,
  non-compensatory decision theory — needs a dedicated reading pass that
  this window did not include; citing from memory would violate the sibling
  works' scholarship discipline. No figures were built this window, so none
  are claimed.
- **Per-line adapter recipes.** Worked, copy-pasteable examples showing each
  line's exported envelope entering the register (by value, no imports).
  Open because honest recipes should be generated against each line's REAL
  current export, run and captured, not sketched from recollection of their
  APIs.
- **External anchoring of the chain tip.** `seal_tip` names the limitation:
  the tip is unbound without an anchor the chain does not control. A worked
  anchoring recipe (e.g. a signed note or an independent log) is deliberately
  out of this package's non-claims and needs a decision about which external
  system Daniel wants to bind to.
## Done (2026-07-29)

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
