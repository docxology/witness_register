# `.agents/skills/` — technical reference

One directory per skill. Each skill directory ships three files:

| File | Role |
| --- | --- |
| `SKILL.md` | The descriptor a runtime loads: YAML frontmatter plus the body |
| `AGENTS.md` | The folder contract for that skill |
| `README.md` | Orientation for a person browsing the tree |

## Current skills

| Skill | Covers |
| --- | --- |
| [`witness-register/`](witness-register/AGENTS.md) | Driving the witness register end to end |

## What a change here must preserve

- A skill name is unique across the discovery roots a runtime scans; renaming
  one breaks any caller that loads it by name.
- The descriptor body states when to use the skill, the quick reference, the
  pitfalls, and the cross-references. Keep those sections present.
- Claims in a descriptor are checked against the code, not remembered. See
  [`../AGENTS.md`](../AGENTS.md) for the probe discipline.

Project root: [AGENTS.md](../../AGENTS.md) and [README.md](../../README.md).
