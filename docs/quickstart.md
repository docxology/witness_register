# Use and verify the Witness Register

## Install and inspect a public envelope

Install Git and uv. The standalone package supports Python 3.11 and later.
The following source verification commands use Python 3.14 and the committed
lockfile. Run them from the checkout root.

```bash
uv sync --locked --python 3.14 --all-groups
uv run --no-sync --python 3.14 python - <<'PY'
import json
from pathlib import Path

from witness_register import genesis_state, intake_envelope, project

path = Path("data/envelopes/releases/v0.4.0-element-admission/red_line_worked.json")
record, issues = intake_envelope(json.loads(path.read_text(encoding="utf-8")))
assert record is not None, issues
state = genesis_state("documentation-example", "2026-11-09", envelopes=(record,))
posture = project(state, declared_next_use="inspect the recorded envelope")
print(posture)
PY
```

The example reads one historical public export. Its projection describes the
recorded state for the declared use. [Claim boundaries](claim_boundaries.md)
explain what that result can establish.

## Native verification

Install `rsvg-convert` from librsvg for the figure checks. From the repository
root, use the locked environment set up above.

```bash
uv run --no-sync --python 3.14 python scripts/build_figures.py
uv run --no-sync --python 3.14 pytest tests/ --cov=src --cov-branch -q
uv run --no-sync --python 3.14 ruff check src tests scripts
uv run --no-sync --python 3.14 mypy src/witness_register --check-untyped-defs
uv run --no-sync --python 3.14 ruff format --check src tests scripts
```

The native build writes SVG and PNG plates and their figure registry into
`output/figures/`. The tests check deterministic regeneration, relative
documentation links, and consumption from the installed wheel and source
distribution in isolation.

## Render the manuscript

Install Pandoc with matching pandoc-crossref, XeLaTeX, and the
[template's required TeX packages](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/usage/output-formats.md).
The template workflow below uses Pandoc 3.14 and the pandoc-crossref 0.3.26b
release built for it.

From a clean Witness Register checkout, prepare the pinned template engine
and a fresh project copy with its own Git index.

```bash
project_root="$(pwd -P)"
verification_dir="$(mktemp -d)"
renderer="$verification_dir/template"
git clone https://github.com/docxology/template.git "$renderer"
git -C "$renderer" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
mkdir -p "$renderer/projects/working"
project_copy="$renderer/projects/working/witness_register"
git clone --no-hardlinks "$project_root" "$project_copy"
git -C "$project_copy" checkout --detach "$(git -C "$project_root" rev-parse HEAD)"

cd "$project_copy"
uv sync --locked --python 3.14 --all-groups
uv run --no-sync --python 3.14 python scripts/build_figures.py
cd "$renderer"
uv sync --locked --no-dev
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/witness_register
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/witness_register
```

The renderer uses [the authored manuscript](manuscript/README.md) and the
project copy's generated figures. Open `output/pdf/witness_register_combined.pdf`
and `output/web/index.html` in `"$project_copy"`. Check the ordered sections,
citations, and figure plates against the manuscript index. Stage 04 writes
the validation report and rendered-provenance receipt under `output/reports/`.
Local rendering and validation leave the historical release packets intact.
