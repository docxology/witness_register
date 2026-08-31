# Witness Register manuscript

This folder holds the numbered manuscript sections, the render configuration,
the bibliography, and the generated cover art consumed by the external template.

## Composition order

The body composes in lexical filename order. Lettered inserts (e.g. `02a`, `02b`)
follow their parent whole-number file.

## Files

- `config.yaml` — paper metadata, authors, publication, and page geometry
- `00_abstract.md` — abstract
- `01_problem.md` — the problem: four instruments, no shared register
- `02_design.md` — the design: chain, projection, and battery
- `02a_formalism.md` — formal definitions and propositions
- `02b_scholarship.md` — scholarship and intellectual lineage
- `02c_method.md` — how the register is built and operated
- `02d_formalism.md` — further propositions: chain, return, and deterministic projection
- `03_examples.md` — worked examples and the 3×3 battery
- `03_limits.md` — limits and epistemic boundaries
- `04_conclusion.md` — conclusion
- `99_references.md` — heading for the bibliography section
- `references.bib` — BibTeX bibliography

## Rendering

```bash
cd /path/to/template
uv run python scripts/pipeline/stage_03_render.py --project working/witness_register
```

See [AGENTS.md](AGENTS.md) for the working contract.
