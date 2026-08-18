# `.agents/` — technical reference

Agent skill descriptors for this project. This directory carries no executable
code and no import surface: the package never reads it, `pytest` never collects
it, and no gate inspects it.

## Layout

| Path | Holds |
| --- | --- |
| [`skills/`](skills/) | One directory per skill descriptor |
| [`skills/witness-register/SKILL.md`](skills/witness-register/SKILL.md) | The operating walkthrough for this project |

## What a change here must preserve

- **Descriptors follow the code, not the reverse.** A statement in a descriptor
  is a claim about the current API. When `src/witness_register/` changes, the
  descriptor is updated in the same change or it is wrong.
- **The root [AGENTS.md](../AGENTS.md) is authoritative.** Where a descriptor
  and the working contract disagree, the contract wins and the descriptor is
  the defect.
- **No line imports.** The register reads envelopes by value and never imports
  `red_line`, `black_line`, `golden_line`, `white_line`, or `line_set`. A
  descriptor that implies otherwise is wrong.
- **The posture is bounded.** Projection returns only `-1 | 0 | +1`, always
  with a declared next use and reasons. Descriptors must not imply that these
  are endorsements, safety findings, or permissions.

## Verifying a descriptor

There is no automated gate over this directory, so check it by hand against the
code it describes:

```bash
uv run python -c "import witness_register; print(sorted(witness_register.__all__))"
uv run pytest -q
```

Every symbol a descriptor names must appear in the package's public surface or
in a module it names explicitly.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
