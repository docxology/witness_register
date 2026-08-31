"""The figure contract: derived plates, legibility floor, determinism.

Real builds into real temp directories; the floor and the registry each have
a planted-defect control proving the guard can fail.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from witness_register import CASE_IDS, project
from witness_register.figures import (
    MAX_CANVAS_WIDTH,
    MIN_TEXT_SIZE,
    PLATES,
    battery_plate,
    build_figures,
    chain_plate,
    cover_plate,
    projection_plate,
    svg_document,
    text,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RSVG_AVAILABLE = shutil.which("rsvg-convert") is not None

#: Text-block width in inches: letter paper less the config's side margins.
TEXT_BLOCK_INCHES = 8.5 - 2 * 0.33


def _config_side_margins() -> tuple[float, float]:
    config = (PROJECT_ROOT / "docs" / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    match = re.search(r'geometry: "left=([\d.]+)in,right=([\d.]+)in', config)
    assert match is not None, "manuscript config declares no side margins"
    return float(match.group(1)), float(match.group(2))


def test_the_legibility_floor_is_derived_from_the_manuscript_geometry() -> None:
    """MIN_TEXT_SIZE renders above 6 pt at 100% embed on the widest canvas."""

    left, right = _config_side_margins()
    text_block = 8.5 - left - right
    assert text_block == pytest.approx(TEXT_BLOCK_INCHES)
    rendered_points = MIN_TEXT_SIZE * text_block * 72 / MAX_CANVAS_WIDTH
    assert rendered_points >= 6.0, rendered_points


def test_text_refuses_a_label_below_the_floor() -> None:
    with pytest.raises(ValueError, match="legibility floor"):
        text(0, 0, "too small to read", MIN_TEXT_SIZE - 1)


def test_svg_document_refuses_a_canvas_wider_than_the_cap() -> None:
    with pytest.raises(ValueError, match="MAX_CANVAS_WIDTH"):
        svg_document(MAX_CANVAS_WIDTH + 1, 100, [], "too wide")


def test_every_plate_svg_is_deterministic_across_two_calls() -> None:
    for build in (chain_plate, projection_plate, battery_plate):
        assert build() == build(), build.__name__


def test_no_text_overflows_the_canvas_extent() -> None:
    """No plate may draw a label that runs past its own canvas edge.

    A label that clips at the canvas boundary is an illegible label — the
    same class of defect as one below the size floor, and one a reviewer
    would only find in a print. This scans every emitted text run (both
    anchors) against the canvas ``viewBox`` it belongs to, so a cover label
    moved flush against the right edge cannot silently escape it.
    """

    import re as _re

    anchor_re = _re.compile(
        r'<text x="(\d+(?:\.\d+)?)"[^>]*text-anchor="end"[^>]*>(.*?)</text>'
    )
    left_re = _re.compile(r'<text x="(\d+(?:\.\d+)?)"[^>]*>(.*?)</text>')
    for build in (cover_plate, chain_plate, projection_plate, battery_plate):
        svg = build()
        width = int(_re.search(r'width="(\d+)"', svg).group(1))
        for m in anchor_re.finditer(svg):
            x = float(m.group(1))
            # A right-anchored run's left edge is unknown; it must sit left
            # of the canvas and its anchor must not exceed the canvas edge.
            assert x <= width, f"{build.__name__}: right-anchored text at {x} > {width}"
        for m in left_re.finditer(svg):
            escaped = m.group(2)
            # Recover a rough glyph width: the longest plausible 18-unit run
            # of text at ~0.5 em per glyph, matched against the remaining room.
            raw = (
                escaped.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            )
            if 'text-anchor="end"' in m.group(0):
                continue
            x = float(m.group(1))
            size = 18
            size_m = _re.search(r'font-size="(\d+)"', m.group(0))
            if size_m:
                size = float(size_m.group(1))
            width_estimate = len(raw) * size * 0.5
            assert x + width_estimate <= width + 1, (
                f"{build.__name__}: '{raw[:40]}…' at x={x} may overflow {width}"
            )


def test_the_chain_plate_carries_live_seals_and_the_refusal() -> None:
    svg = chain_plate()
    assert "verify_chain((state0, state1)) — sound" in svg
    assert "refusing to extend rewritten hi" in svg
    assert len(re.findall(r"seal: [0-9a-f]{24}…", svg)) == 2


def test_the_projection_plate_rows_match_fresh_calls() -> None:
    """The plate's postures are what project() returns again right now."""

    svg = projection_plate()
    assert svg.count("-1  route resisted") == 3
    assert svg.count("0  held") == 3
    assert svg.count("+1  nothing recorded forbids it") == 2
    # And the fixed points re-derive: an empty state is -1 today too.
    from witness_register import genesis_state

    assert project(genesis_state("s", "2026-07-29"), "u").value == -1


def test_the_battery_plate_names_every_case_and_the_defeat_proof() -> None:
    svg = battery_plate()
    for case_id in CASE_IDS:
        assert f">{case_id}<" in svg, case_id
    assert (
        f"defeat proof: {len(CASE_IDS)}/{len(CASE_IDS)} cases raised BatteryError"
        in svg
    )


def test_every_plate_registration_carries_its_boundaries() -> None:
    for plate in PLATES:
        assert plate.caption and plate.alt, plate.label
        assert plate.interpretive_claim, plate.label
        assert plate.epistemic_boundary, plate.label
        assert plate.source, plate.label


@pytest.mark.skipif(not RSVG_AVAILABLE, reason="rsvg-convert not on PATH")
def test_build_writes_every_artifact_and_an_accurate_registry(tmp_path) -> None:
    written = build_figures(tmp_path)
    names = {path.name for path in written}
    for plate in PLATES:
        assert plate.filename in names
        assert plate.filename.replace(".png", ".svg") in names
    registry = json.loads((tmp_path / "figure_registry.json").read_text("utf-8"))
    assert registry["schema_version"] == "witness-register.figure-registry/1.0"
    import hashlib

    for entry in registry["figures"]:
        png = tmp_path / entry["filename"]
        assert hashlib.sha256(png.read_bytes()).hexdigest() == entry["png_digest"]


@pytest.mark.skipif(not RSVG_AVAILABLE, reason="rsvg-convert not on PATH")
def test_two_builds_are_byte_identical(tmp_path) -> None:
    first_dir = tmp_path / "one"
    second_dir = tmp_path / "two"
    build_figures(first_dir)
    build_figures(second_dir)
    for path in sorted(first_dir.iterdir()):
        assert path.read_bytes() == (second_dir / path.name).read_bytes(), path.name


def test_the_registry_digest_check_rejects_a_replaced_image(tmp_path) -> None:
    """Planted defect: a swapped PNG must disagree with the registry."""

    if not RSVG_AVAILABLE:
        pytest.skip("rsvg-convert not on PATH")
    import hashlib

    build_figures(tmp_path)
    registry = json.loads((tmp_path / "figure_registry.json").read_text("utf-8"))
    target = tmp_path / registry["figures"][0]["filename"]
    target.write_bytes(b"not the plate that was registered")
    assert (
        hashlib.sha256(target.read_bytes()).hexdigest()
        != registry["figures"][0]["png_digest"]
    )


def test_every_plate_is_embedded_with_its_registered_caption() -> None:
    """The manuscript embeds carry the registry captions verbatim.

    A caption edited in one place and not the other is drift between what
    the registry attests and what the reader sees; this binds them.
    """

    manuscript = ""
    for name in ("01_problem.md", "02_design.md", "02a_formalism.md"):
        manuscript += (PROJECT_ROOT / "docs" / "manuscript" / name).read_text("utf-8")
    flat = " ".join(manuscript.split())
    for plate in PLATES:
        assert f"#{plate.label}" in flat, plate.label
        assert " ".join(plate.caption.split()) in flat, plate.label
        assert f"../output/figures/{plate.filename}" in flat, plate.label
