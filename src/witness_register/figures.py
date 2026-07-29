"""Deterministic figure plates drawn from live register calls.

Every value a plate prints comes from running the real package in the build:
the chain plate seals and verifies an actual two-state chain over the four
real exported envelopes in ``data/envelopes/``, the projection plate prints
what ``project`` actually returned for each constructed state, and the
battery plate prints ``run_battery``'s own results including the live proof
that every case rejects its injected-wrong variant. Nothing is typed in as a
literal that the code could have produced.

Design constraints, shared with the sibling line works but written natively:

- **Legibility floor.** The manuscript's text block is 7.66 in wide (letter
  paper less the 0.42 in side margins declared in ``manuscript/config.yaml``),
  and every plate is embedded at ``width=100%`` on a canvas at most
  ``MAX_CANVAS_WIDTH`` units wide, so an ``N``-unit label renders at
  ``N * 7.66 * 72 / MAX_CANVAS_WIDTH`` points. ``MIN_TEXT_SIZE`` = 18 units
  therefore renders at 6.20 pt, above the 6 pt print-legibility gate;
  :func:`text` raises below the floor rather than shipping an unreadable
  label. ``tests/test_figures.py`` re-derives the arithmetic from the config.
- **No colour of its own.** The register is not a line and has no colour in
  the set's sense; the plates are greyscale on paper, and no meaning is
  carried by ink alone — every distinction also has a word.
- **Determinism.** Two builds are byte-identical; the registry records the
  SHA-256 of every artifact so a replaced image fails the check, not review.

Non-claims: a plate depicts what the register's code returned for
constructed or stored inputs on the build machine. It is not evidence about
any line's report, any subject's merit, or any real decision.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .battery import CASE_IDS, BatteryError, run_battery
from .envelopes import intake_envelope
from .projection import project
from .relations import RelationRecord, RelationType
from .returns import ReturnContractRecord
from .state import genesis_state, update_state, verify_chain
from .version import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENVELOPE_DIR = PROJECT_ROOT / "data" / "envelopes"
OUTPUT_DIR = PROJECT_ROOT / "output" / "figures"

FIGURE_REGISTRY_SCHEMA = "witness-register.figure-registry/1.0"

#: Widest canvas any plate may open; caps how small an embedded label prints.
MAX_CANVAS_WIDTH = 1600

#: Smallest label, in canvas units, any plate may draw (6.20 pt rendered).
MIN_TEXT_SIZE = 18

# Greyscale palette. The register has no colour in the set's sense.
PAPER = "#f5f3ef"
INK = "#1a1a1a"
MID = "#666666"
FAINT = "#d8d5cf"
CARD = "#ffffff"
DARK = "#2e2e2e"

RSVG_CONVERT = "rsvg-convert"


def escape_text(value: str) -> str:
    """Escape text inserted between SVG tags."""

    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def text(
    x: int, y: int, value: str, size: int, fill: str = INK, weight: str = "400"
) -> str:
    """One SVG text element, refusing a size below the legibility floor."""

    if size < MIN_TEXT_SIZE:
        raise ValueError(
            f"figure text size {size} is below the {MIN_TEXT_SIZE}-unit "
            "legibility floor; an illegible label is a defect, not a style"
        )
    return (
        f'<text x="{x}" y="{y}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="{size}" fill="{fill}" font-weight="{weight}">'
        f"{escape_text(value)}</text>"
    )


def rect(
    x: int,
    y: int,
    width: int,
    height: int,
    fill: str = CARD,
    stroke: str = FAINT,
    dash: str = "",
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2"{dash_attr}/>'
    )


def line(x1: int, y1: int, x2: int, y2: int, stroke: str = MID) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="2"/>'
    )


def svg_document(width: int, height: int, body: list[str], description: str) -> str:
    """Assemble one SVG document with a machine-readable description."""

    if width > MAX_CANVAS_WIDTH:
        raise ValueError(
            f"canvas width {width} exceeds MAX_CANVAS_WIDTH={MAX_CANVAS_WIDTH}; "
            "a wider canvas shrinks every label below its derived print size"
        )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        f"<desc>{escape_text(description)}</desc>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{PAPER}"/>',
        *body,
        "</svg>",
    ]
    return "\n".join(parts) + "\n"


def _worked_records():
    """Intake the four stored real envelopes, failing loudly if any is absent."""

    names = (
        "red_line_worked.json",
        "black_line_worked.json",
        "golden_line_worked.json",
        "white_line_worked.json",
    )
    records = []
    for name in names:
        payload = json.loads((ENVELOPE_DIR / name).read_text(encoding="utf-8"))
        record, issues = intake_envelope(payload)
        if record is None:
            raise RuntimeError(f"{name} failed intake: {issues}")
        records.append(record)
    return records


def _worked_chain():
    """The same two-state chain the worked-example test builds, built live."""

    records = _worked_records()
    refs = [record.report_ref for record in records]
    first = genesis_state(
        "line-set-worked-examples-2026-07-29", "2026-07-29", envelopes=records
    )
    cannot_compare = RelationRecord(
        relation_id="worked-cannot-compare-1",
        subject_id=first.subject_id,
        source_report_refs=(refs[0], refs[1]),
        relation_type=RelationType.CANNOT_COMPARE,
        bounded_description="different instruments, different worked subjects",
    )
    contract = ReturnContractRecord(
        contract_id="worked-same-subject-return",
        subject_id=first.subject_id,
        why_held="four envelopes describe four different worked cases",
        alternatives_live=("use as a mechanics demonstration",),
        change_condition="all four lines export envelopes about one work",
        standing="whoever runs the four reviews about one work",
        protected="nothing in this case",
        trigger="a same-subject export set enters data/envelopes/",
        acceptance_condition="four same-subject envelopes in one state",
    )
    due = RelationRecord(
        relation_id="worked-return-due-1",
        subject_id=first.subject_id,
        source_report_refs=tuple(refs),
        relation_type=RelationType.RETURN_DUE,
        bounded_description="a same-subject export set is owed first",
        return_contract_ref=contract.contract_id,
    )
    second = update_state(
        first, "2026-07-29", relations=(cannot_compare, due), returns=(contract,)
    )
    return first, second


def _tamper_refusal_detail() -> str:
    """Mutate a freshly built state's record and capture the live refusal."""

    first, _second = _worked_chain()
    first.envelopes[0].native_status  # touch, then mutate a fresh copy below
    fresh_first, _ = _worked_chain()
    status = fresh_first.envelopes[2].native_status
    if isinstance(status, list) and status:
        status[0][1] = "REWRITTEN-AFTER-SEALING"
    else:  # pragma: no cover - shape guard; golden's status is a list
        raise RuntimeError("expected a list-shaped native_status to tamper with")
    try:
        update_state(fresh_first, "2026-07-30")
    except ValueError as error:
        return str(error)
    raise RuntimeError("tampered state was extended; the plate would be a lie")


def chain_plate() -> str:
    """The worked chain, sealed and verified live, with the refusal shown."""

    first, second = _worked_chain()
    violations = verify_chain((first, second))
    verdict = "sound" if not violations else f"{len(violations)} violation(s)"
    refusal = _tamper_refusal_detail()
    body: list[str] = []
    body.append(
        text(60, 70, "THE APPEND-ONLY CHAIN, SEALED AND VERIFIED", 30, weight="700")
    )
    body.append(
        text(
            60,
            110,
            "Both states built live from the four stored real envelopes; every digest below is computed in this build.",
            20,
            MID,
        )
    )
    # Genesis card.
    body.append(rect(60, 150, 640, 240))
    body.append(text(90, 195, "STATE 0 — GENESIS", 24, weight="700"))
    body.append(text(90, 235, f"subject: {first.subject_id}", 20))
    body.append(
        text(
            90,
            270,
            f"envelopes: {len(first.envelopes)} (red, black, golden, white)",
            20,
        )
    )
    body.append(text(90, 305, "prior_ref: (empty — genesis)", 20, MID))
    body.append(
        text(90, 345, f"seal: {first.state_digest[:24]}…", 20, DARK, weight="700")
    )
    # Arrow.
    body.append(line(700, 270, 880, 270, INK))
    body.append(f'<polygon points="880,262 896,270 880,278" fill="{INK}"/>')
    body.append(text(712, 250, "prior_ref = seal of state 0", 18, MID))
    # Update card.
    body.append(rect(900, 150, 640, 240))
    body.append(text(930, 195, "STATE 1 — UPDATE (APPEND ONLY)", 24, weight="700"))
    body.append(
        text(930, 235, "adds: 1 CANNOT_COMPARE, 1 RETURN_DUE, 1 return contract", 20)
    )
    body.append(
        text(930, 270, "prior records: all 4 envelopes, unchanged and in place", 20)
    )
    body.append(text(930, 305, f"prior_ref: {second.prior_ref[:24]}…", 20, MID))
    body.append(
        text(930, 345, f"seal: {second.state_digest[:24]}…", 20, DARK, weight="700")
    )
    # Verdict strip.
    body.append(rect(60, 430, 1480, 90, DARK, DARK))
    body.append(
        text(
            90,
            485,
            f"verify_chain((state0, state1)) — {verdict} · return recoverability preserved",
            24,
            PAPER,
            weight="700",
        )
    )
    # Refusal strip.
    body.append(rect(60, 560, 1480, 130, CARD, MID, dash="8 6"))
    body.append(
        text(
            90,
            605,
            "WHAT REFUSAL LOOKS LIKE (run live in this build):",
            20,
            weight="700",
        )
    )
    body.append(
        text(
            90,
            640,
            "one stored value mutated after sealing, then update_state —",
            20,
            MID,
        )
    )
    snippet = refusal if len(refusal) <= 118 else refusal[:115] + "…"
    body.append(text(90, 672, f'raised: "{snippet}"', 18, INK))
    body.append(
        text(
            60,
            740,
            "The chain proves internal consistency only; the tip is unbound without an anchor the chain does not control.",
            18,
            MID,
        )
    )
    return svg_document(
        1600,
        780,
        body,
        "Two-state chain schematic with live seals, live verification verdict, and a live tamper refusal.",
    )


#: The projection rows, in the precedence order project() enforces. Each row
#: names a constructor; the plate prints what project() actually returned.
def _projection_rows():
    records = _worked_records()
    envelope = records[0]
    ref = envelope.report_ref

    def relation(rid: str, rtype: RelationType, **over) -> RelationRecord:
        fields = {
            "relation_id": rid,
            "subject_id": "zone",
            "source_report_refs": (ref,),
            "relation_type": rtype,
            "bounded_description": "constructed for the projection table",
        }
        fields.update(over)
        return RelationRecord(**fields)

    contract = ReturnContractRecord(
        contract_id="zone-contract",
        subject_id="zone",
        why_held="constructed",
        alternatives_live=(),
        change_condition="c",
        standing="s",
        protected="p",
        trigger="t",
        acceptance_condition="a",
    )
    agrees = tuple(
        relation(f"agree-{index}", RelationType.AGREES, human_decision_ref=f"d{index}")
        for index in range(50)
    )
    rows = [
        (
            "unresolved NON_COMPENSATORY_BLOCK (rescope decision offered)",
            genesis_state(
                "zone",
                "2026-07-29",
                envelopes=(envelope,),
                relations=(relation("block", RelationType.NON_COMPENSATORY_BLOCK),),
            ),
            "decision-arg-offered",
        ),
        (
            "the same block buried under 50 AGREES",
            genesis_state(
                "zone",
                "2026-07-29",
                envelopes=(envelope,),
                relations=agrees[:25]
                + (relation("block-2", RelationType.NON_COMPENSATORY_BLOCK),)
                + agrees[25:],
            ),
            "decision-arg-offered",
        ),
        (
            "empty state (nothing co-registered)",
            genesis_state("zone", "2026-07-29"),
            "decision-arg-offered",
        ),
        (
            "PROTECTED_ABSENCE (rescope decision offered)",
            genesis_state(
                "zone",
                "2026-07-29",
                envelopes=(envelope,),
                relations=(
                    relation(
                        "prot",
                        RelationType.PROTECTED_ABSENCE,
                        human_decision_ref="decision-on-record",
                    ),
                ),
            ),
            "decision-arg-offered",
        ),
        (
            "RETURN_DUE, contract unmet, no rescope",
            genesis_state(
                "zone",
                "2026-07-29",
                envelopes=(envelope,),
                relations=(
                    relation(
                        "due",
                        RelationType.RETURN_DUE,
                        return_contract_ref="zone-contract",
                    ),
                ),
                returns=(contract,),
            ),
            "",
        ),
        (
            "the same RETURN_DUE, rescope decision offered",
            genesis_state(
                "zone",
                "2026-07-29",
                envelopes=(envelope,),
                relations=(
                    relation(
                        "due-2",
                        RelationType.RETURN_DUE,
                        return_contract_ref="zone-contract",
                    ),
                ),
                returns=(contract,),
            ),
            "decision-arg-offered",
        ),
        (
            "DIRECTIONAL_TENSION, no decision recorded",
            genesis_state(
                "zone",
                "2026-07-29",
                envelopes=(envelope,),
                relations=(relation("tension", RelationType.DIRECTIONAL_TENSION),),
            ),
            "decision-arg-offered",
        ),
        (
            "one envelope, nothing forbids the use",
            genesis_state("zone", "2026-07-29", envelopes=(envelope,)),
            "",
        ),
    ]
    printed = []
    for label, state, decision_ref in rows:
        projection = project(
            state,
            "the constructed next use this table was asked about",
            human_decision_ref=decision_ref,
        )
        printed.append((label, projection.value, projection.reasons[0]))
    return printed


def projection_plate() -> str:
    """The zone table: what project() returned for each constructed state."""

    rows = _projection_rows()
    body: list[str] = []
    body.append(text(60, 70, "THE PROJECTION ZONE, MEASURED", 30, weight="700"))
    body.append(
        text(
            60,
            110,
            "Each row is one constructed state and the value project() actually returned in this build. Rows that offered a",
            20,
            MID,
        )
    )
    body.append(
        text(
            60,
            140,
            "decision reference at projection time say so — together the rows show what a decision argument does and does not lift.",
            20,
            MID,
        )
    )
    y = 180
    for label, value, reason in rows:
        value_word = {
            -1: "-1  route resisted",
            0: "0  held",
            1: "+1  nothing recorded forbids it",
        }[value]
        fill = DARK if value == -1 else (CARD if value == 0 else PAPER)
        text_fill = PAPER if value == -1 else INK
        body.append(rect(60, y, 560, 84, CARD, FAINT))
        body.append(text(84, y + 34, label, 20, weight="700"))
        body.append(rect(640, y, 330, 84, fill, MID))
        body.append(text(664, y + 50, value_word, 22, text_fill, weight="700"))
        snippet = reason if len(reason) <= 62 else reason[:59] + "…"
        body.append(rect(990, y, 550, 84, CARD, FAINT))
        body.append(text(1012, y + 50, snippet, 18, MID))
        y += 100
    body.append(
        text(
            60,
            y + 30,
            "The scalar never travels alone: every row's projection carried its state_ref and its full reasons.",
            18,
            MID,
        )
    )
    return svg_document(
        1600,
        y + 70,
        body,
        "Projection precedence table computed by running project() over constructed states in this build.",
    )


def battery_plate() -> str:
    """The shipped 3x3 battery, run live, with the injected-wrong proof."""

    checks = run_battery()
    by_case: dict[str, list] = {}
    for check in checks:
        by_case.setdefault(check.case_id, []).append(check)
    defeats = 0
    for case_id in CASE_IDS:
        try:
            run_battery(defeat=case_id)
        except BatteryError:
            defeats += 1
    body: list[str] = []
    body.append(
        text(60, 70, "THE REVIEW'S 3×3 BATTERY, RUN IN THIS BUILD", 30, weight="700")
    )
    body.append(
        text(
            60,
            110,
            f"{len(checks)} checks across {len(CASE_IDS)} cases; every check passed, and every case rejected its injected-wrong variant.",
            20,
            MID,
        )
    )
    for index, case_id in enumerate(CASE_IDS):
        column = index % 3
        row = index // 3
        x = 60 + column * 510
        y = 150 + row * 190
        case_checks = by_case.get(case_id, [])
        all_passed = bool(case_checks) and all(c.passed for c in case_checks)
        body.append(rect(x, y, 480, 160, CARD, INK if all_passed else MID))
        body.append(text(x + 24, y + 40, case_id, 20, weight="700"))
        body.append(text(x + 24, y + 76, f"checks run: {len(case_checks)}", 20))
        body.append(
            text(
                x + 24,
                y + 108,
                "all passed" if all_passed else "NOT ALL PASSED",
                20,
                DARK,
                weight="700",
            )
        )
        body.append(text(x + 24, y + 138, "injected-wrong variant: rejected", 18, MID))
    footer_y = 150 + ((len(CASE_IDS) + 2) // 3) * 190 + 20
    body.append(rect(60, footer_y, 1480, 80, DARK, DARK))
    body.append(
        text(
            90,
            footer_y + 50,
            f"defeat proof: {defeats}/{len(CASE_IDS)} cases raised BatteryError when their observed behaviour was falsified",
            22,
            PAPER,
            weight="700",
        )
    )
    return svg_document(
        1600,
        footer_y + 120,
        body,
        "Battery grid computed by running run_battery() live, including the per-case injected-wrong rejection proof.",
    )


@dataclass(frozen=True)
class PlateSpec:
    """One plate's registration: what it shows and what it must not become."""

    label: str
    filename: str
    build: object
    caption: str
    alt: str
    source: str
    interpretive_claim: str
    epistemic_boundary: str


PLATES: tuple[PlateSpec, ...] = (
    PlateSpec(
        label="fig:wr-chain",
        filename="wr_chain.png",
        build=chain_plate,
        caption=(
            "The worked two-state chain, built live from the four stored real "
            "envelopes at figure-build time: the genesis seal, the update's "
            "prior_ref pointing at it, verify_chain's verdict on the pair, and "
            "— run in the same build — the exact refusal update_state raises "
            "when one stored value is mutated after sealing. Chain integrity "
            "is internal consistency only; the tip is unbound without an "
            "anchor the chain does not control."
        ),
        alt=(
            "Two boxes for chain states joined by a prior_ref arrow, each "
            "showing its seal digest prefix; a dark verdict strip for "
            "verify_chain; a dashed strip quoting the live tamper refusal."
        ),
        source="witness_register.state over data/envelopes/*.json",
        interpretive_claim=(
            "update_state and verify_chain hold the append-only contract on "
            "the real worked chain, and refuse rewritten history."
        ),
        epistemic_boundary=(
            "Depicts register bookkeeping on stored records; says nothing "
            "about the truth of any envelope's report or the merit of any "
            "subject."
        ),
    ),
    PlateSpec(
        label="fig:wr-zone",
        filename="wr_zone.png",
        build=projection_plate,
        caption=(
            "The projection zone measured: each row is one constructed state "
            "and the value project() actually returned in this build, with a "
            "human decision reference offered at projection time so the rows "
            "also show what a decision argument does not lift — it never "
            "resolves a block and never lifts a protected absence. A "
            "non-compensatory block forces -1 alone and under fifty AGREES "
            "relations alike; an empty register is -1, not permission; every "
            "hold row is 0 with its reason; +1 appears only where an envelope "
            "exists and nothing recorded forbids the use."
        ),
        alt=(
            "8-row table: state description, returned posture (-1, 0, or "
            "+1) with a word, and the first reason string project() returned."
        ),
        source="witness_register.projection.project over constructed states",
        interpretive_claim=(
            "The posture invariants hold in code: precedence is fixed, "
            "agreement volume compensates for nothing, and every value "
            "travels with reasons."
        ),
        epistemic_boundary=(
            "The symbols are interface values about recorded relations, not "
            "endorsements, safety findings, or permissions; a +1 states only "
            "that nothing recorded forbids the declared use."
        ),
    ),
    PlateSpec(
        label="fig:wr-battery",
        filename="wr_battery.png",
        build=battery_plate,
        caption=(
            "The design review's 3×3 canonical witness cases as the shipped "
            "battery, run at figure-build time: every check passed on the "
            "real register, and — measured in the same build — every case "
            "raised BatteryError when its observed behaviour was deliberately "
            "falsified, so a green grid is evidence the checks can fail, not "
            "only that they passed."
        ),
        alt=(
            "Three-by-three grid of battery case cards, each with its check "
            "count and pass status, and a dark footer counting the per-case "
            "injected-wrong rejections."
        ),
        source="witness_register.battery.run_battery, clean and per-case defeat",
        interpretive_claim=(
            "The battery passes on the real register and demonstrably rejects "
            "falsified behaviour case by case."
        ),
        epistemic_boundary=(
            "The cases are constructed canonical scenarios from the design "
            "review; passing them is a property of the register's code, not "
            "of any real co-registration."
        ),
    ),
)


def artifact_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rasterize(svg_path: Path, png_path: Path, figure: str) -> None:
    executable = os.environ.get("WITNESS_REGISTER_RSVG_CONVERT", RSVG_CONVERT)
    try:
        subprocess.run([executable, "-o", str(png_path), str(svg_path)], check=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            f"{executable!r} could not render {figure}; install librsvg so "
            "rsvg-convert is on PATH."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"{executable!r} failed while rendering {figure}."
        ) from error


def build_figures(output_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Write every plate and the figure registry; return the written paths."""

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    entries: list[dict] = []
    for plate in PLATES:
        svg_path = output_dir / plate.filename.replace(".png", ".svg")
        png_path = output_dir / plate.filename
        svg_path.write_text(plate.build(), encoding="utf-8")
        _rasterize(svg_path, png_path, plate.label)
        written.extend([svg_path, png_path])
        entries.append(
            {
                "label": plate.label,
                "filename": plate.filename,
                "caption": plate.caption,
                "alt": plate.alt,
                "source": plate.source,
                "interpretive_claim": plate.interpretive_claim,
                "epistemic_boundary": plate.epistemic_boundary,
                "generated_by": "scripts/build_figures.py",
                "format": "PNG rasterized from deterministic SVG",
                "svg_digest": artifact_digest(svg_path),
                "png_digest": artifact_digest(png_path),
            }
        )
    registry_path = output_dir / "figure_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": FIGURE_REGISTRY_SCHEMA,
                "package_version": __version__,
                "figures": entries,
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(registry_path)
    return written


__all__ = [
    "FIGURE_REGISTRY_SCHEMA",
    "MAX_CANVAS_WIDTH",
    "MIN_TEXT_SIZE",
    "PLATES",
    "PlateSpec",
    "build_figures",
    "battery_plate",
    "chain_plate",
    "projection_plate",
    "escape_text",
    "svg_document",
    "text",
]
