# Architecture

One package, twelve small modules, no runtime dependencies. Every module
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
| `invariants.py` | `check_state`/`check_chain`/`check_projection` + `defect_battery` (12 planted defects, all must be detected) | passes vacuously — the battery proves rejection |
| `battery.py` | `run_battery` — the review's 3×3 canonical witness cases, with injected-wrong variants | returns green without every required behavior holding |
| `serialization.py` | canonical JSON, SHA-256, `witness-register.<thing>/1.0` schema strings | security semantics |
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
