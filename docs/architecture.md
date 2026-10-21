# Architecture

One package with small modules and no runtime dependencies. Every module
carries its non-claims in its docstring; the package docstring
(`src/witness_register/__init__.py`) states the register-wide ones.

## Module map

| Module | Owns | Never |
| --- | --- | --- |
| `version.py` | `__version__`, bound by test to every copy | — |
| `envelopes.py` | `intake_envelope`, `EnvelopeRecord`, `IntakeIssue`, `IssueCode` — typed intake of `line.report-envelope/1.0` by value | parses or interprets `native_status`; rejects silently |
| `relations.py` | `RelationType` (8 members), `RelationRecord`, `NOT_RECORDED` | replaces or rewrites any line's status |
| `returns.py` | `ReturnContractRecord`, `record_return` — partial returns close only the verified part, as fields | manufactures a return; closes a remainder |
| `held.py` | `UnclassifiedHeld` — raw holdings outside every alphabet | auto-creates a category |
| `state.py` | `WitnessState`, `genesis_state`, `update_state` (fail-closed append-only), `verify_chain`, `seal_tip`, `promote_unclassified` | mutates history; promotes without a human decision ref |
| `projection.py` | `Projection`, `project`, `witness_hold_reasons`, `HoldReason` — the bounded `-1/0/+1` posture | reads `native_status`; emits a value without state_ref and reasons |
| `metrics.py` | `relation_fidelity`, `return_recoverability`, `premature_crowning_rate` | measures the truth of any report |
| `invariants.py` | `check_state`/`check_chain`/`check_projection_binding`/`check_projection` + `defect_battery` (12 planted defects, all must be detected) | passes vacuously — the battery proves rejection |
| `battery.py` | `run_battery` — the review's 3×3 canonical witness cases, with injected-wrong variants | returns green without every required behavior holding |
| `serialization.py` | canonical JSON, SHA-256, versioned `witness-register.<thing>` schema strings | security semantics |
| `figures.py` | deterministic figure plates drawn from live register calls; byte-identical rebuilds | invents any value the code could have produced |

## Data flow

```
line repo (by value, published schema string)
    │  dict payload "line.report-envelope/1.0"
    ▼
intake_envelope ──typed refusal──► (None, IntakeIssues)
    │ EnvelopeRecord (verbatim)
    ▼
genesis_state / update_state ──► WitnessState (sealed, chained by prior_ref)
    │            ▲                    │
    │   RelationRecord /              ├─► verify_chain / check_chain
    │   ReturnContractRecord /        ├─► seal_tip ──► EXTERNAL anchor (yours)
    │   UnclassifiedHeld              │
    ▼                                 ▼
promote_unclassified          project(state, declared_next_use)
(human decision ref required)        │
                                     ▼
                          Projection(value, state_ref, reasons)
```

## The append-only chain and the unanchored tip

Each state's digest covers its full canonical content INCLUDING record order
and `prior_ref`, so the chain commits to its own history. `update_state`
re-derives the prior state's digest from live content before extending —
an in-place mutation of a sealed record (for example, editing an envelope's
`native_status` dict) raises instead of being carried forward.

**Stated limitation, not solved:** the tip is unbound. A holder of the whole
chain can discard recent states and present an earlier tip as current, and
nothing inside the chain can detect it. `seal_tip` re-derives and returns the
tip digest precisely so you can anchor it in something the chain does not
control — a signed message, an independent log, a sibling system's record.
Until that anchoring exists (see [TODO](../TODO.md)), chain integrity is a
claim about internal consistency only.

## Why projection reads relations, not native_status

The review proposes non-compensatory invariants over the lines' findings. The
register enforces them — but driven ONLY by typed relation records, because
the register must never parse a native vocabulary it does not own. If a
line's finding should constrain the posture, a human (or the line's own
tooling, upstream) registers that constraint as a relation. This is an
adaptation of the review's proposal, recorded in
[correspondence](correspondence.md).

## Authority, validation and replay

`decisions.py` owns typed append-only acknowledgment, resolution, rescope and
reopening claims. Classification is separate, with `classification_decision_ref`
on promotions. A nonblank historical `human_decision_ref` never discharges a
constraint. Every event binds an exact canonical relation/contract digest,
exact declared use, evidence reference and actual prior basis state.
Contradictory clear/reopen claims hold visibly without order arbitration.
Protected absence has no generic resolution.

`validation.py` owns dependency-neutral structural checks and typed issues.
Validated constructors and public projection both require it. `raw_state`
is a seal-only inspection path; it cannot receive a posture without validation.
`project_chain` also validates genesis and actual append context. A seal,
local structure, full-chain verification and external freshness are separate
claims. `history_refs` retains declared ancestry; full-chain replay binds it.

`returns.py` retains the open/completed pair model with every immutable term
bound and a required open predecessor. A partial completion can have one new
obligation linked by its exact canonical digest. `remainder_contract` preserves
standing, protection and trigger and names exactly the remaining subset.
Verified remainder closure closes that subset of the parent; changing terms
requires a new obligation and an explicit targeted rescope.

`json_data.py` validates bounded strict JSON without interpreting vocabulary;
intake deep-copies accepted status containers. Canonical serialization rejects
coercions and invalid Unicode. Migration and schema versions are specified in
[the review ledger](review-20261020.md). Backdated review dates are allowed;
append order, review date and external anchoring date remain distinct.

`check_projection_binding` and `state_binding_fidelity` are narrow seal checks.
`check_projection` replays all stored inputs. `chain_coverage` exposes preserved
links and denominator, genesis coverage, full-chain validity and an optional
operator anchor reference separately. Compatibility scalar names remain narrow
and never combine into a quality or truth score.
