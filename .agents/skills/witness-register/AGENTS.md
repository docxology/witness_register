# `witness-register` skill — technical reference

| File | Role |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The descriptor: YAML frontmatter (`name`, `description`) plus the body |
| [`AGENTS.md`](AGENTS.md) | This file — the folder contract |
| [`README.md`](README.md) | Orientation for a person browsing the tree |

## Audience

Agents that need to build a witness state chain, project a posture from
co-registered envelopes, run the design-review battery, or verify the append-only
contract.

## What the descriptor asserts, and where each claim is checked

| Claim in `SKILL.md` | Checked against |
| --- | --- |
| `genesis_state` and `update_state` signatures | [`src/witness_register/state.py`](../../../src/witness_register/state.py) |
| The projection invariants (-1, 0, +1) | [`src/witness_register/projection.py`](../../../src/witness_register/projection.py) |
| The 3×3 battery and per-case defeat | [`src/witness_register/battery.py`](../../../src/witness_register/battery.py) |
| Envelope intake and validation | [`src/witness_register/envelopes.py`](../../../src/witness_register/envelopes.py) |
| Relation types and return contracts | [`src/witness_register/relations.py`](../../../src/witness_register/relations.py) |
| Worked example over stored envelopes | [`tests/test_worked_example.py`](../../../tests/test_worked_example.py) |

## What a change here must preserve

- The frontmatter `name` is `witness-register`; a runtime loads the skill by
  that name, so renaming it breaks callers.
- The `description` carries the USE WHEN trigger. Keep it accurate.
- The non-claims section is the contract: no line imports, no interpretation of
  `native_status`, no auto-categories, the posture is bounded and never travels
  alone.
- The gotchas section describes probed behaviour. Re-run the probe before
  editing an entry.

## Verifying

```bash
uv run python -c "import witness_register; print(sorted(witness_register.__all__))"
uv run pytest -q
```

Project root: [AGENTS.md](../../../AGENTS.md) and [README.md](../../../README.md).
