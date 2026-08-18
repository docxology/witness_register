# Agent-facing descriptors

This directory holds the skill descriptors an agent runtime loads when it works
on the Witness Register. Nothing here is imported by the package, executed by
the test suite, or checked by the release gate; it is orientation for a reader
that arrives without the repository's context.

Start at [`skills/witness-register/SKILL.md`](skills/witness-register/SKILL.md)
for the operating walkthrough: the state chain, projection invariants, the
battery, and the non-claims that bound every posture.

The authoritative working contract is the repository-root
[AGENTS.md](../AGENTS.md); a descriptor here that disagrees with it is wrong.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
