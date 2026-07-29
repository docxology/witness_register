# witness_register

**The Shared Witness Register: co-registration without aggregation.**

The register sits BESIDE the line set — the four line works and their set
reader — as a sixth work. It is not a line: it has no colour, no substantive
question of its own, and no verdict.

## What it is never (read this first)

**No score, no override, no rewriting of the four instruments.** The register
never ranks, averages, merges, or scores the lines it co-registers, and it
never reinterprets a line's native vocabulary. Each line remains the sole
authority over its own report. The register's whole ambition is precedence
without information destruction: it holds every instrument's word beside every
other's, keeps their conflicts co-present as first-class records, and refuses
to let any single number become the state. No crown without return.

The full non-claims are stated in the package docstring
(`src/witness_register/__init__.py`) and bounded per claim class in
[docs/claim_boundaries.md](docs/claim_boundaries.md).

## What it does

- **Accepts envelopes by value.** Each line exports one common report
  envelope under the published schema string `line.report-envelope/1.0` — a
  digest pointer to its complete native report, its identity, subject, review
  date, registry provenance, `native_status` in its OWN vocabulary, and its
  non-claims. `intake_envelope` validates the shape and stores the payload
  verbatim; nothing is rejected silently, and acceptance asserts nothing
  about the truth of the report.
- **Records relations as separate records.** Blocks, dependencies, protected
  absences, directional tensions, unclassified observations, due returns,
  incomparabilities, and agreements are typed `RelationRecord`s beside the
  envelopes. Relations describe; they never replace any line's status.
- **Keeps history append-only.** States are sealed by digest and chained by
  `prior_ref`. `update_state` refuses, fail-closed, to build on tampered
  history; `verify_chain` checks a stored chain; `seal_tip` hands you the tip
  digest for EXTERNAL anchoring — an append-only chain's tip is unbound
  without it, a limitation this repository states rather than solves.
- **Holds the unclassifiable raw.** `UnclassifiedHeld` lives outside every
  status alphabet. Promotion into a relation requires a non-empty human
  decision reference and links back to the original holding.
- **Projects a posture only on request.** `project(state, declared_next_use)`
  emits `-1 | 0 | +1` with non-compensatory invariants enforced in code and
  driven only by relation records. The symbols `-1/0/+1` are interface
  values, not the ontology: a projection always carries the state digest that
  earned it and the reasons it holds.

## Quick start

```bash
uv sync
uv run pytest tests/ --cov=src --cov-branch -q
```

```python
from witness_register import (
    genesis_state, intake_envelope, project, run_battery,
)

record, issues = intake_envelope(payload)   # payload: a line's exported dict
assert record is not None, issues           # typed refusal, never silent
state = genesis_state("subject-1", "2026-07-29", (record,))
posture = project(state, declared_next_use="cite in the review meeting")
print(posture.value, posture.reasons)       # the scalar never travels alone

run_battery()                                # the review's 3x3 witness cases
```

## The envelope contract it accepts

One dict per line report, field names by published convention:

| Field | Requirement |
| --- | --- |
| `schema_version` | exactly `"line.report-envelope/1.0"` |
| `line_id` | non-blank string, the exporting instrument's name |
| `subject_id` | string |
| `review_date` | ISO `YYYY-MM-DD` calendar date |
| `registry_version` | string, the line's own registry version |
| `registry_digest` | 64-char lowercase hex |
| `native_status` | any JSON-compatible value — stored verbatim, never interpreted |
| `report_ref` | 64-char lowercase hex pointer to the complete native report |
| `source_snapshot_refs` | list of non-blank strings |
| `scope_and_nonclaims` | non-empty list of non-blank strings |

## The projection's boundary

`-1` (route resisted), `0` (held), `+1` (nothing recorded forbids it) are
**interface values, not the ontology**. Enforced in code: an unresolved
non-compensatory block forces `-1`; a protected absence forbids `+1`
unconditionally — protection is not missing evidence to be mined; an unmet
return forbids `+1` until the return condition is met or a referenced human
decision rescopes; an empty register is `-1` — nothing to witness is not
permission. Every projection carries `state_ref` and `reasons`, and
`witness_hold_reasons` enumerates, structured, why a state holds at `0`.

## Layout

- `src/witness_register/` — the package: intake, relations, returns,
  holdings, state chain, projection, metrics, invariants, the 3×3 battery,
  serialization. Map in [docs/architecture.md](docs/architecture.md).
- `tests/` — real-record tests, no mocks; positive controls throughout.
- `manuscript/` — the short manuscript sources.
- [docs/correspondence.md](docs/correspondence.md) — why this work exists:
  the 2026-07-29 design review, proposal by proposal.
- [STANDALONE.md](STANDALONE.md) — what a separated clone can and cannot do.
- [AGENTS.md](AGENTS.md) — the validation contract and exact gate commands.

## The sibling works

Referenced by name and URL only — never by import, never by relative path:
[red_line](https://github.com/docxology/red_line),
[black_line](https://github.com/docxology/black_line),
[golden_line](https://github.com/docxology/golden_line),
[white_line](https://github.com/docxology/white_line),
[line_set](https://github.com/docxology/line_set).

## License

CC-BY-4.0 (prose); MIT (code).
