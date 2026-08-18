# Documentation guidance

Documentation is part of the Witness Register contract. Keep API behavior and
numeric manuscript claims bound to executable tests; state whether a claim is
computational, structural, methodological, or outside the instrument's scope.

The register is a sixth work beside the line set: it co-registers report
envelopes without aggregation, ranking, or override. It has no colour, no
substantive question of its own, and no verdict — only the typed relations it
records.

## What belongs here

- Behavior claims that can be verified by running the package
- Architecture decisions and their constraints
- Correspondence and reviewer feedback with responses
- Publication metadata and release records

## What does not belong here

- Prose that belongs in the manuscript (goes under `../manuscript/`)
- Code-level documentation (stays in docstrings under `../src/`)
- Test expectations (stays in test files under `../tests/`)
