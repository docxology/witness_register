---
name: witness-register
description: Operate the Witness Register — build state chains with genesis_state and update_state, project postures (-1|0|+1) with declared next uses, append exact-target lifecycle decisions, run the design-review battery, ingest line report envelopes, and verify the append-only chain contract. The register co-registers without aggregation, ranking, or override. USE WHEN building witness chains, projecting co-registration postures, running the battery with per-case defeat, or verifying the append-only contract.
---

# Witness Register local skill

The Witness Register stands beside the instruments and their reader: it co-registers line
report envelopes without aggregation, ranking, or override. Its executable core
is a state chain — `genesis_state` creates the first state from ingested
envelopes, `update_state` appends new relations and returns while refusing
tampering, and `verify_chain` checks the full chain after the fact.

The register has no colour, no substantive question of its own, and no verdict.
Projection returns only `-1 | 0 | +1`, always with a declared next use and at
least one reason.

## Quick start (from the project root)

```bash
uv run python scripts/build_figures.py
uv run pytest tests/ --cov=src --cov-branch -q
uv run ruff check src tests scripts
uv run mypy src/witness_register --check-untyped-defs
uv run ruff format --check src tests scripts
```

Figure generation requires the system `rsvg-convert` executable from librsvg.
Render with an isolated detached checkout of `docxology/template` origin/main
on GitVault. Put a fresh real clone of the source release commit, with its own
`.git`, at `projects/active/witness_register`; build its figures first. Run
`uv run --no-sync python scripts/pipeline/stage_03_render.py --project active/witness_register`
then `uv run --no-sync python scripts/pipeline/stage_04_validate.py --project active/witness_register`.
Inspect every validation result and the actual PDF/HTML. Follow
`docs/publication.md` for provenance, metadata, independent audit and release.

## States and the chain

A witness state carries `subject_id`, `review_moment`, `envelopes`,
`relations`, `unclassified`, `returns`, `prior_ref`, `state_digest`,
`decisions` and `history_refs`. The seal covers every other field, using
canonical JSON with sorted keys and preserving record sequence order.
The register subject is a string and stays exactly unchanged across the chain;
native subject correspondence remains a registrar declaration.

The chain is append-only:
- A genesis state carries an empty `prior_ref`.
- Every other state carries the digest of the state it extends and must contain
  every prior record unchanged and in place before any addition.
- `update_state` re-derives the prior seal from live content before extending.
  A record mutated after sealing raises rather than being carried forward.
- `verify_chain` checks every link; it never repairs anything.
- `genesis_state`, `update_state` and `project` reject invalid bookkeeping with
  typed issues. `raw_state` is seal-only inspection; a seal grants no posture.
- `project_chain` checks the supplied full genesis chain before projecting.

## Core API — worked example

```python
from witness_register import (
    genesis_state, update_state, verify_chain,
    intake_envelope, project, run_battery
)
from pathlib import Path
import json

# Intake the original historical four-envelope subset
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

1. A non-compensatory block without an uncontested matching `RESOLVE` event
   forces `-1`; conflicting clear/reopen claims retain that block.
2. An empty state is `-1` — nothing to witness is not permission.
3. Any hold — a protected absence, an outstanding return, an unresolved tension,
   dependency, incomparability, or unreviewed observation — caps the value at `0`.
4. `+1` is reachable only when at least one envelope exists and nothing recorded
   forbids the use.

No volume of agreement buys back a blocked route. A single unresolved block
forces `-1` under any number of agreement relations. A protected absence caps
the posture at `0` past every decision reference.

Classification is not clearance. Promotion records `classification_decision_ref`;
historical `human_decision_ref` and a projection-time receipt supply no resolution
authority. Append a `DecisionEvent` naming the exact target digest, declared use,
evidence and actual prior basis state. Acknowledgment is neutral; protected
absence cannot be generically resolved. An exact-contract `RESCOPE` affects only
its declared use. Other unmatched obligations remain open.

Completed returns must preserve every immutable term of their open predecessor.
Partial completion closes only its verified part; `remainder_contract` links an
explicit child obligation. Reopening that remainder invalidates derived parent
closure for the matching use. Stored obligations constrain projection through
authored `RETURN_DUE` relations; the register does not invent a missing relation.

## The battery

The design review's 3×3 canonical witness cases ship as `run_battery()`. Every
check passes on the real register, and — measured in the same build — every case
raises `BatteryError` when its observed behaviour is deliberately falsified. A
passing grid is evidence the checks can fail, not only that they passed.

```python
from witness_register import CASE_IDS, BatteryError

checks = run_battery()
assert all(check.passed for check in checks)

for case_id in CASE_IDS:
    try:
        run_battery(defeat=case_id)
    except BatteryError:
        pass
    else:
        raise AssertionError(f"wrong variant was accepted: {case_id}")
```

The grid groups STATE (`S1`–`S3`), RELATION (`R4`–`R6`) and RETURN (`T7`–`T9`)
cases. Each defeat changes one observation per case; it does not plant a defect
in every predicate. Counts are derived from `checks` and `CASE_IDS`.

## Gotchas (probed against the real API)

- **Tamper refusal is live.** `update_state` re-derives the prior seal from
  live content. A value mutated anywhere inside a stored envelope — even buried
  inside an opaque `native_status` — causes it to raise. Test with the real
  chain, not with constructed examples.
- **Seal digests include record sequence order.** Reordering records changes
  the seal. Dictionary key insertion order does not: canonical JSON sorts keys.
- **`native_status` is opaque.** The register stores it verbatim and never
  parses, compares, ranks, averages, or merges it. Projection is driven only by
  relation records.
- **Intake rejects non-JSON.** `NaN` and `Infinity` in a payload are refused
  with a typed issue, because a digest over text that is not JSON would seal a
  non-interchangeable value.
- **Blank decision refs are refused.** `promote_unclassified` requires a non-empty
  human decision reference and records it as classification provenance.
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

Historical collections remain under `data/envelopes/`; the example above uses
their original subset. Current release exports live under
`data/envelopes/releases/`, with exact snapshot and byte custody in the manifest.
`scripts/build_release_cohort.py` generates its authored chain;
`tests/test_release_cohort.py` replays it. Worked native subjects remain distinct,
so the release cohort records incomparability and an open correspondence return.
