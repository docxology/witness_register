# Witness Register manuscript

This folder holds the numbered manuscript sections, the render configuration,
the bibliography, and the LaTeX preamble consumed by the external template.
The cover and figure plates are generated into `output/figures/`.

## Composition order

The body composes in lexical filename order. Lettered inserts (e.g. `02a`, `02b`)
follow their parent whole-number file.

## Files

- [`config.yaml`](config.yaml) — paper metadata, authors, publication, and page geometry
- [`00_abstract.md`](00_abstract.md) — abstract
- [`01_problem.md`](01_problem.md) — the problem: independent instruments, no shared register
- [`02_design.md`](02_design.md) — the design: chain, projection, and battery
- [`02a_formalism.md`](02a_formalism.md) — formal definitions and propositions
- [`02b_scholarship.md`](02b_scholarship.md) — scholarship and intellectual lineage
- [`02c_method.md`](02c_method.md) — how the register is built and operated
- [`02d_formalism.md`](02d_formalism.md) — further propositions: chain, return, and deterministic projection
- [`03_examples.md`](03_examples.md) — worked examples and the 3×3 battery
- [`03_limits.md`](03_limits.md) — limits and epistemic boundaries
- [`04_conclusion.md`](04_conclusion.md) — conclusion
- [`99_references.md`](99_references.md) — heading for the bibliography section
- [`preamble.md`](preamble.md) — LaTeX declarations
- [`references.bib`](references.bib) — BibTeX bibliography

## Rendering

Build the project figures, then follow the [pinned render and validation guide](../quickstart.md#render-the-manuscript).
The figure builder derives the historical chain and battery plates from the
package and committed fixture data. The current cohort and its evidence
boundaries are described in the manuscript and the [release documentation](../publication.md).

See [AGENTS.md](AGENTS.md) for manuscript editing rules.
