---
name: witness-register
description: Operate the Witness Register — build state chains with genesis_state and update_state, project postures (-1|0|+1) with declared next uses, run the 3×3 design-review battery, ingest line report envelopes, and verify the append-only chain contract. The register co-registers without aggregation, ranking, or override. USE WHEN working in projects/working/witness_register, building witness chains, projecting co-registration postures, running the battery with per-case defeat, or verifying the append-only contract.
---

# Witness Register local skill

The Witness Register is a sixth work beside the line set: it co-registers line
report envelopes without aggregation, ranking, or override. Its executable core
is a state chain — `genesis_state` creates the first state from ingested
envelopes, `update_state` appends new relations and returns while refusing
tampering, and `verify_chain` checks the full chain after the fact.

The register has no colour, no substantive question of its own, and no verdict.
Projection returns only `-1 | 0 | +1`, always with a declared next use and at
least one reason.

## Quick start (from the project root)

```bash
uv run pytest -q                                                  # 206 tests
uv run python scripts/build_figures.py                            # deterministic figures (writes output/figures/)
```

Figure generation requires the system `rsvg-convert` executable from librsvg.
Render the publication bundle with the external `docxology/template` engine —
cloned or located anywhere on disk, with this checkout linked in as its
`projects/working/witness_register` — using
`uv run python scripts/pipeline/stage_03_render.py --project working/witness_register`.

## States and the chain

A witness state has eight fields: `subject_id`, `review_moment`, `envelopes`,
`relations`, `unclassified`, `returns`, `prior_ref`, and `state_digest`
(SHA-256 over the canonical JSON of the other seven fields, preserving order).

The chain is append-only:
- A genesis state carries an empty `prior_ref`.
- Every other state carries the digest of the state it extends and must contain
  every prior record unchanged and in place before any addition.
- `update_state` re-derives the prior seal from live content before extending.
  A record mutated after sealing raises rather than being carried forward.
- `verify_chain` checks every link; it never repairs anything.

## Core API — worked example

```python
from witness_register import (
    genesis_state, update_state, verify_chain,
    intake_envelope, project, run_battery
)
from pathlib import Path
import json

# Intake the four real stored envelopes
envelopes = []
for name in ("red_line_worked.json", "black_line_worked.json",
             "golden_line_worked.json", "white_line_worked.json"):
    payload = json.loads((Path("data/envelopes") / name).read_text("utf-8"))
    record, issues = intake_envelope(payload)
    assert record is not None, issues
    envelopes.append(record)

# Build the chain
first = genesis_state("worked-example", "2026-07-29", envelopes=envelopes)
# Add relations and a return contract
from witness_register import RelationRecord, RelationType, ReturnContractRecord

refs = tuple(e.report_ref for e in envelopes)
cannot_compare = RelationRecord(
    relation_id="ic-1", subject_id="worked-example",
    source_report_refs=(refs[0], refs[1]),
    relation_type=RelationType.CANNOT_COMPARE,
    bounded_description="different instruments, different worked subjects",
)
contract = ReturnContractRecord(
    contract_id="return-1", subject_id="worked-example",
    why_held="four envelopes describe four different worked cases",
    alternatives_live=("use as a mechanics demonstration",),
    change_condition="all four lines export envelopes about one work",
    standing="whoever runs the four reviews about one work",
    protected="nothing in this case",
    trigger="a same-subject export set enters data/envelopes/",
    acceptance_condition="four same-subject envelopes in one state",
)
due = RelationRecord(
    relation_id="rd-1", subject_id="worked-example",
    source_report_refs=refs,
    relation_type=RelationType.RETURN_DUE,
    bounded_description="a same-subject export set is owed first",
    return_contract_ref=contract.contract_id,
)
second = update_state(first, "2026-07-29", relations=(cannot_compare, due), returns=(contract,))

# Verify
violations = verify_chain((first, second))
assert not violations  # sound

# Project
posture = project(second, "the constructed next use")
# posture.value is -1, 0, or +1; posture.reasons names why
```

## Projection invariants

Projection is computed from relation records only, in fixed precedence:

1. Any non-compensatory block with no recorded human decision forces `-1`.
2. An empty state is `-1` — nothing to witness is not permission.
3. Any hold — a protected absence, an outstanding return, an unresolved tension,
   dependency, incomparability, or unreviewed observation — caps the value at `0`.
4. `+1` is reachable only when at least one envelope exists and nothing recorded
   forbids the use.

No volume of agreement buys back a blocked route. A single unresolved block
forces `-1` under any number of agreement relations. A protected absence caps
the posture at `0` past every decision reference.

## The battery

The design review's 3×3 canonical witness cases ship as `run_battery()`. Every
check passes on the real register, and — measured in the same build — every case
raises `BatteryError` when its observed behaviour is deliberately falsified. A
passing grid is evidence the checks can fail, not only that they passed.

```python
checks = run_battery()
# 9 checks across 3 cases; every check passed

for case_id in ["seal-tamper-detection", "projection-precedence", "intake-validation"]:
    try:
        run_battery(defeat=case_id)
    except BatteryError:
        pass  # expected — the injected-wrong variant was rejected
```

## Gotchas (probed against the real API)

- **Tamper refusal is live.** `update_state` re-derives the prior seal from
  live content. A value mutated anywhere inside a stored envelope — even buried
  inside an opaque `native_status` — causes it to raise. Test with the real
  chain, not with constructed examples.
- **Seal digests include record order.** Reordering the fields of a state
  changes its digest. The canonical JSON serializer preserves insertion order.
- **`native_status` is opaque.** The register stores it verbatim and never
  parses, compares, ranks, averages, or merges it. Projection is driven only by
  relation records.
- **Intake rejects non-JSON.** `NaN` and `Infinity` in a payload are refused
  with a typed issue, because a digest over text that is not JSON would seal a
  non-interchangeable value.
- **Blank decision refs are refused.** `RelationRecord` requires a non-empty
  `human_decision_ref` for promotion. A whitespace-only reference is rejected.
- **Figure determinism is byte-level.** Two builds produce identical SVGs, PNGs,
  and registry. `figure_registry.json` records the SHA-256 of every artifact;
  `tests/test_register_figures.py` re-derives and compares.

## Claim boundaries

The register co-registers report envelopes without aggregation, ranking, or
override. Projection values `-1 | 0 | +1` are interface values about recorded
relations, not endorsements, safety findings, or permissions. A `+1` states
only that nothing recorded forbids the declared use. The chain proves internal
consistency only; the tip is unbound without an anchor the chain does not
control. The battery passes on canonical constructed cases — it is a property of
the register's code, not of any real co-registration. See
`docs/claim_boundaries.md` before adding any prose or API surface that could
imply otherwise.

## The report envelope (cross-instrument transport)

The register ships four stored envelopes under `data/envelopes/`, one per line,
each generated by running that line's own public API on 2026-07-29 and stored
by value. They describe four *different* worked subjects — so the honest
structure is an incomparability relation and an open return contract.
`tests/test_worked_example.py` intakes all four unmodified and exercises the
full machinery.
