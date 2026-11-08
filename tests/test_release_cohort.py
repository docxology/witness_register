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
EDITIONS = ("v0.2.0", "v0.3.0", "v0.3.0-source-refresh")


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


@pytest.mark.parametrize("edition", EDITIONS)
def test_release_export_custody_check_detects_changed_bytes(tmp_path, edition):
    source = DIRECTORY.parent / edition
    shutil.copytree(source, tmp_path / "cohort")
    directory = tmp_path / "cohort"
    manifest = json.loads((directory / "manifest.json").read_text())
    entry = manifest["siblings"][0]
    path = directory / entry["file"]
    original = path.read_bytes()
    assert sha256(original).hexdigest() == entry["sha256"]
    path.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="export bytes changed"):
        build_cohort(directory)


@pytest.mark.parametrize("edition", EDITIONS)
@pytest.mark.parametrize("defect", ["invalid-envelope", "foreign-line"])
def test_cohort_refuses_invalid_and_misattributed_exports(tmp_path, defect, edition):
    shutil.copytree(DIRECTORY.parent / edition, tmp_path / "cohort")
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


def test_new_cohort_uses_its_authored_classification_reference(tmp_path):
    directory = tmp_path / "cohort"
    shutil.copytree(DIRECTORY, directory)
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["cohort_id"] = "new-declared-cohort"
    manifest["reviewed_on"] = "2026-11-06"
    manifest["classification_decision_ref"] = "registrar:new-cohort-classification"
    manifest_path.write_text(json.dumps(manifest))
    generated = build_cohort(directory)
    relations = generated["states"][-1]["payload"]["relations"]
    assert all(
        relation["classification_decision_ref"]
        == manifest["classification_decision_ref"]
        for relation in relations
    )
    assert generated["projection"]["value"] == 0
    assert (
        generated["states"][-1]["payload"]["envelopes"]
        == generated["states"][0]["payload"]["envelopes"]
    )


@pytest.mark.parametrize("edition", EDITIONS[1:])
def test_native_editions_preserve_distinct_subjects_and_open_correspondence(edition):
    directory = DIRECTORY.parent / edition
    manifest = json.loads((directory / "manifest.json").read_text())
    assert len(manifest["siblings"]) == len(LINES)
    assert {e["repository"].split("/")[1] for e in manifest["siblings"]} == LINES
    generated = build_cohort(directory)
    assert generated == json.loads((directory / "co_registration.json").read_text())
    first, second = generated["states"]
    envelopes = second["payload"]["envelopes"]
    assert len({e["subject_id"] for e in envelopes}) == len(LINES)
    assert envelopes == first["payload"]["envelopes"]
    assert second["payload"]["prior_ref"] == first["state_digest"]
    relations = second["payload"]["relations"]
    assert {r["relation_type"] for r in relations} == {"CANNOT_COMPARE", "RETURN_DUE"}
    assert all(
        r["classification_decision_ref"] == manifest["classification_decision_ref"]
        for r in relations
    )
    contract = second["payload"]["returns"][0]
    assert contract["prior_state_ref"] == first["state_digest"]
    due = next(r for r in relations if r["relation_type"] == "RETURN_DUE")
    assert due["return_contract_ref"] == contract["contract_id"]
    assert generated["projection"]["value"] == 0
    assert any("return_due" in reason for reason in generated["projection"]["reasons"])
    assert any("CANNOT_COMPARE" in r for r in generated["projection"]["reasons"])


def test_source_refresh_changes_only_declared_public_bindings():
    previous = DIRECTORY.parent / "v0.3.0"
    current = DIRECTORY.parent / "v0.3.0-source-refresh"
    old = json.loads((previous / "manifest.json").read_text())
    new = json.loads((current / "manifest.json").read_text())
    assert new["cohort_id"] != old["cohort_id"]
    assert new["classification_decision_ref"] != old["classification_decision_ref"]
    changed = {"docxology/red_line", "docxology/blue_line", "docxology/silver_line"}
    for before, after in zip(old["siblings"], new["siblings"], strict=True):
        assert before["repository"] == after["repository"]
        if before["repository"] != "docxology/violet_line":
            assert before["export_recipe"] == after["export_recipe"]
        else:
            assert "export_recipe" not in after
        if before["repository"] in changed:
            assert before["commit"] != after["commit"]
            assert after["snapshot_kind"] == "immutable-commit"
            assert len(after["commit"]) == 40
        else:
            assert before == after
            assert (previous / before["file"]).read_bytes() == (
                current / after["file"]
            ).read_bytes()
        raw = (current / after["file"]).read_bytes()
        assert sha256(raw).hexdigest() == after["sha256"]
    violet = json.loads((current / "violet_line_worked.json").read_text())
    assert violet["subject_id"] == "violet-synthetic-study"
    assert violet["source_snapshot_refs"] == []
