# Changelog

## 0.1.0 — 2026-07-29

First window. The Shared Witness Register, built as a sixth work beside the
line set in answer to the 2026-07-29 design review "The Space Between the
Lines" (Marek Bargiel, with Simba) — see
[docs/correspondence.md](docs/correspondence.md).

- `envelopes.py` — typed intake of `line.report-envelope/1.0` payloads by
  value; verbatim storage; typed refusal (`WRONG_SCHEMA`, `MISSING_FIELD`,
  `MALFORMED_FIELD`, `EMPTY_NONCLAIMS`), nothing silent.
- `relations.py` — the eight-member relation vocabulary; relations describe,
  never override; `human_decision_ref` empty = NOT_RECORDED, first-class.
- `returns.py` — return contracts; `record_return` closes only the verified
  part, keeps the trigger, refuses blank verifications.
- `held.py` — `UnclassifiedHeld` outside every alphabet.
- `state.py` — sealed states, append-only chain, fail-closed `update_state`,
  `verify_chain`, `seal_tip` (tip unbound without external anchoring —
  stated, not solved), `promote_unclassified` requiring a human decision.
- `projection.py` — bounded `-1/0/+1` posture, non-compensatory invariants
  in code, driven only by relation records; `witness_hold_reasons`.
- `metrics.py` — relation fidelity, return recoverability, premature
  crowning rate; register-bookkeeping measures only.
- `invariants.py` — structural checks plus a 12-defect proof-of-detection
  battery.
- `battery.py` — the review's 3×3 canonical witness cases as a shipped
  battery; every case rejects an injected-wrong variant.
- `serialization.py` — canonical JSON + SHA-256; six
  `witness-register.<thing>/1.0` schema strings.

Measured this window (commands run 2026-07-29, recorded in AGENTS.md gates):
test and coverage numbers are reported by the suite itself — run
`uv run pytest tests/ --cov=src --cov-branch -q` for the current figures;
the release gate is branch coverage `fail_under = 90`.

### 2026-07-29 hardening — the adversarial pass the first window did not get

A hostile verification pass (34 fresh probes against the public API, run
before any fix) found four defects and one design point; each fix landed with
the probe that produced it rewritten as a regression test in
`tests/test_wave3_hardening.py`:

- **A whitespace-only `verification_result` counted as a verified return.**
  `record_return` refused it, but direct construction did not, `is_met` came
  back `True`, and a `RETURN_DUE` hold lifted all the way to `+1` — measured,
  a crown without a return. `ReturnContractRecord.__post_init__` now refuses
  whitespace-only `verification_result` and `open_remainder`: empty means
  open (or nothing remains), content means content, whitespace means nothing
  and raises.
- **`NaN` and `Infinity` laundered through `native_status`.** Python's
  `json.dumps` accepts them by default, so intake accepted the payload and
  the sealed state's canonical JSON carried a bare `NaN` literal no strict
  parser reads back. Intake now validates with `allow_nan=False`, and
  `canonical_json` itself raises rather than emitting non-JSON — a digest
  over text that is not JSON would seal a non-interchangeable value.
- **`project` stamped `state_ref` onto rewritten history.** `update_state`
  and `seal_tip` re-derive the seal; `project` did not, so a record mutated
  in place after sealing still earned a projection carrying a `state_ref`
  that no longer named the live content. `project` now re-derives the seal
  and refuses a mismatch, fail-closed like its siblings.
- **Formatting gate had never run.** `ruff format --check` was declared in
  AGENTS.md but failing across 14 files; the tree is now formatted and both
  ruff gates pass.
- **Stated non-check, now stated in code.** An envelope's `subject_id` is
  not required to equal the state's — lines spell the same work's subject
  differently, so string equality is not the correspondence that matters.
  `genesis_state`'s docstring records this as a registration decision, and a
  binding test holds the docstring and the behaviour together.

Everything the pass could not bend is also on record: a
`NON_COMPENSATORY_BLOCK` buried under fifty `AGREES` relations still forces
`-1`; `PROTECTED_ABSENCE` caps at `0` past every decision reference; a
mutated middle state fails `verify_chain`, `update_state`, and `seal_tip`;
promotion refuses blank and whitespace decision references; and intake
rejected all twelve malformed-payload classes with typed issues naming every
defect, not only the first. Measured after the pass: 157 passed (148 before),
98.65% branch coverage (the misses are pre-existing lines in `battery.py` and
`invariants.py`), `ruff check` and `ruff format --check` both clean. First
render through the external engine completed the same day: 0 undefined
references, validation passing (five bare-URL warnings fixed in
`manuscript/99_references.md`).

### 2026-07-29 second window — real envelopes, and the core stated formally

- **The worked co-registration runs on real exports.** `data/envelopes/`
  holds four `line.report-envelope/1.0` records, one per line, each
  generated by running that line's own public API in that line's own
  repository (provenance table in `data/envelopes/README.md` — repo,
  version, command, native_status shape). This is the first cross-work data
  flow in the set, by value under the published schema, never by import.
  `tests/test_worked_example.py` intakes all four unmodified, verifies the
  two native_status shapes (word vs structure) are stored verbatim, builds a
  two-state chain with honest relations — `CANNOT_COMPARE` over the one
  shared spelling, and a `RETURN_DUE` whose contract names what a
  same-subject co-registration would require — and measures: chain clean,
  return recoverability 1.0, relation fidelity 1.0, posture held at 0 with
  both records named in the reasons. The held posture is the demonstration.
- **`manuscript/02a_formalism.md`** states the envelope record, the witness
  state and chain, the append-only fail-closed propositions, the projection
  and zone, and the non-compensatory propositions as renderer-numbered
  fenced blocks, each bound to the running package by
  `tests/test_formalism.py` (field rosters via `dataclasses.fields`, clause
  behaviour via live calls, the worked-example paragraph pinned to the same
  measured outcomes its test re-derives). Two drifts planted in the real
  manuscript (a falsified state-field count, a "held at 0" flipped to "+1")
  each failed exactly the named test before byte-identical restoration.
- Re-rendered through the external engine: full validation pass, zero
  undefined references, definitions auto-numbered. Measured at close: 170
  passed (163 + 7), branch coverage 98.65%, both ruff gates clean.

### 2026-07-29 third window — figures, scholarship, the return met, and the anchor prepared

- **Three derived plates** (`figures.py`, `scripts/build_figures.py`):
  `wr_chain` (the worked chain sealed and verified live, with the actual
  tamper refusal quoted from a live `update_state` raise), `wr_zone` (the
  projection precedence table, every posture a fresh `project()` return,
  rows explicit about which offered a rescope decision and what it did and
  did not lift), and `wr_battery` (the 3×3 battery run in the build,
  including the 9/9 injected-wrong rejection proof). Greyscale on paper —
  the register has no colour in the set's sense. Legibility floor 18
  canvas units (6.20 pt at 100% embed, derived from the manuscript
  geometry and re-derived in tests), double builds byte-identical, figure
  registry with per-artifact SHA-256 and interpretive-claim /
  epistemic-boundary fields, captions bound verbatim to the manuscript
  embeds by test (drift planted and caught).
- **Scholarship** (`manuscript/02b_scholarship.md`, `references.bib`):
  linked timestamping (Haber & Stornetta 1991), hash authentication
  (Merkle, CRYPTO '89 proceedings 1990), transparency logs and the
  observer-consistency problem (RFC 6962, RFC 9162), non-compensatory
  decision rules (Fishburn 1974), provenance-as-records (W3C PROV-DM 2013),
  and boundary objects (Star & Griesemer 1989) — every bibliographic record
  verified against Crossref, the RFC Editor, or the W3C on 2026-07-29
  before use, and each citation scoped to the mechanism borrowed, never to
  any judgment.
- **The first chain's return contract was met** the way it said it must be:
  `data/envelopes/same_subject/` holds four further envelopes, each line's
  real evaluator run over ONE declared work — witness_register 0.1.0
  itself, registrar-authored inputs with provenance recorded beside the
  records and inside each `subject_id`. The instruments answered in their
  own vocabularies (`ALIGNED`; an honest `outside_scope`; two `TOWARD` with
  seven `NOT_OBSERVED`; `NAMED`/`UNRESOLVED`/`NAMED` with eight
  `NOT_RECORDED`). `tests/test_same_subject.py` measures the whole arc:
  completing the contract lifts exactly the `return_due` hold (the
  incomparability hold remains, honestly), and the same-subject state's own
  posture is held at 0 because the ledger's open question enters as an
  unresolved dependency — three favorable readings and one open question is
  a held posture, not a crown.
- **`anchor_statement`** prepares the code side of tip anchoring without
  choosing the external system: verifies the whole chain, re-derives the
  tip seal, and returns a byte-stable strict-JSON record to be stored in a
  system the chain does not control. Storing it here would anchor nothing;
  the boundary sentence travels inside the record.
- **Cross-exporter consistency bound over the stored corpus**: all eight
  stored envelopes carry the identical sorted ten-key set and sorted
  serialization; a sibling exporter drifting its roster or order fails
  `tests/test_envelopes.py` the next time its export is stored.
- Measured at close: 188 passed (186 + consistency + anchor tests), both
  ruff gates clean, figure double-build byte-identical (7 artifacts), and
  the full suite also passing under a real Python 3.10 interpreter
  (`uv run --python 3.10 --isolated pytest`, 2026-07-29).
