"""Released-snapshot custody and authored registration, without native interpretation."""

from hashlib import sha256
import json
from pathlib import Path
import shutil

import pytest

from scripts.build_release_cohort import build_cohort

DIRECTORY = Path(__file__).resolve().parents[1] / "data/envelopes/releases/v0.2.0"
LINES = {
    "red_line",
    "black_line",
    "golden_line",
    "white_line",
    "silver_line",
    "violet_line",
    "blue_line",
    "green_line",
}


def test_release_cohort_replays_every_declared_export():
    manifest = json.loads((DIRECTORY / "manifest.json").read_text())
    assert {
        entry["repository"].split("/")[1] for entry in manifest["siblings"]
    } == LINES
    assert len(manifest["siblings"]) == len(LINES)
    for entry in manifest["siblings"]:
        if entry.get("source_path"):
            assert entry["source_path"] == f"data/envelopes/{entry['file']}"
        else:
            assert entry["export_recipe"]
        assert len(entry["commit"]) == 40
        assert len(entry["sha256"]) == 64
        assert entry["snapshot_kind"] in (
            "annotated-release",
            "dispatcher-authorized-origin-main",
        )
        if entry["snapshot_kind"] == "annotated-release":
            assert entry["tag"].startswith("v")
            assert len(entry["tag_object"]) == 40
        else:
            assert entry["repository"] == "docxology/red_line"
            assert entry["tag"] is None
            assert entry["declared_version"] == "0.3.0"
            assert manifest["wait_termination_authority"]
    generated = build_cohort(DIRECTORY)
    assert generated == json.loads((DIRECTORY / "co_registration.json").read_text())
    assert generated["projection"]["value"] == 0
    states = generated["states"]
    assert len(states[-1]["payload"]["envelopes"]) == len(LINES)
    assert states[-1]["payload"]["envelopes"] == states[0]["payload"]["envelopes"]
    assert states[-1]["payload"]["prior_ref"] == states[0]["state_digest"]


def test_release_export_custody_check_detects_changed_bytes(tmp_path):
    shutil.copytree(DIRECTORY, tmp_path / "cohort")
    directory = tmp_path / "cohort"
    manifest = json.loads((directory / "manifest.json").read_text())
    entry = manifest["siblings"][0]
    path = directory / entry["file"]
    original = path.read_bytes()
    assert sha256(original).hexdigest() == entry["sha256"]
    path.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="export bytes changed"):
        build_cohort(directory)


@pytest.mark.parametrize("defect", ["invalid-envelope", "foreign-line"])
def test_cohort_refuses_invalid_and_misattributed_exports(tmp_path, defect):
    shutil.copytree(DIRECTORY, tmp_path / "cohort")
    directory = tmp_path / "cohort"
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entry = manifest["siblings"][0]
    path = directory / entry["file"]
    payload = json.loads(path.read_text())
    payload["line_id"] = "" if defect == "invalid-envelope" else "foreign-line"
    path.write_text(json.dumps(payload))
    entry["sha256"] = sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="refused export|does not match"):
        build_cohort(directory)
