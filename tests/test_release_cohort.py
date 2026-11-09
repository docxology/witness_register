"""Released-snapshot custody and authored registration, without native interpretation."""

from hashlib import sha256
import json
from pathlib import Path
import shutil

import pytest

from scripts.build_release_cohort import build_cohort
from witness_register import canonical_json

DIRECTORY = Path(__file__).resolve().parents[1] / "data/envelopes/releases/v0.2.0"
# Membership belongs to each edition, not to its tested manifest or the current
# family roster. Historical editions must not acquire later admissions.
EDITION_LINES = {
    "v0.2.0": {
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
        "silver_line",
        "violet_line",
        "blue_line",
        "green_line",
    },
    "v0.3.0": {
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
        "silver_line",
        "violet_line",
        "blue_line",
        "green_line",
    },
    "v0.3.0-source-refresh": {
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
        "silver_line",
        "violet_line",
        "blue_line",
        "green_line",
    },
    "v0.3.0-final-source-refresh": {
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
        "silver_line",
        "violet_line",
        "blue_line",
        "green_line",
    },
    "v0.3.1-runtime-source-refresh": {
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
        "silver_line",
        "violet_line",
        "blue_line",
        "green_line",
    },
    "v0.4.0-element-admission": {
        "red_line",
        "black_line",
        "golden_line",
        "white_line",
        "silver_line",
        "violet_line",
        "blue_line",
        "green_line",
        "copper_line",
        "iron_line",
    },
}
EDITIONS = tuple(EDITION_LINES)
CURRENT_EDITION = "v0.4.0-element-admission"


def test_release_cohort_replays_every_declared_export():
    manifest = json.loads((DIRECTORY / "manifest.json").read_text())
    lines = EDITION_LINES[DIRECTORY.name]
    assert {
        entry["repository"].split("/")[1] for entry in manifest["siblings"]
    } == lines
    assert len(manifest["siblings"]) == len(lines)
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
    assert len(states[-1]["payload"]["envelopes"]) == len(lines)
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
    lines = EDITION_LINES[edition]
    assert len(manifest["siblings"]) == len(lines)
    assert {e["repository"].split("/")[1] for e in manifest["siblings"]} == lines
    generated = build_cohort(directory)
    assert generated == json.loads((directory / "co_registration.json").read_text())
    first, second = generated["states"]
    envelopes = second["payload"]["envelopes"]
    assert len({e["subject_id"] for e in envelopes}) == len(lines)
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


def test_current_edition_keeps_native_status_opaque_and_private_sources_outside():
    directory = DIRECTORY.parent / CURRENT_EDITION
    manifest = json.loads((directory / "manifest.json").read_text())
    generated = build_cohort(directory)
    stored = {
        envelope["line_id"]: envelope
        for envelope in generated["states"][-1]["payload"]["envelopes"]
    }
    assert set(stored) == EDITION_LINES[CURRENT_EDITION]
    for entry in manifest["siblings"]:
        payload = json.loads((directory / entry["file"]).read_text())
        envelope = stored[payload["line_id"]]
        assert canonical_json(envelope["native_status"]) == canonical_json(
            payload["native_status"]
        )
        assert envelope["report_ref"] == payload["report_ref"]
        assert envelope["scope_and_nonclaims"] == payload["scope_and_nonclaims"]
        if payload["line_id"] in {"violet_line", "copper_line", "iron_line"}:
            assert payload["source_snapshot_refs"] == []
            assert entry["snapshot_kind"] == "disclosure-reviewed-synthetic-envelope"
            assert not {
                "commit",
                "tree",
                "tag_object",
                "export_recipe",
                "source_path",
            }.intersection(entry)


@pytest.mark.parametrize("document", ("manifest", "export"))
@pytest.mark.parametrize(
    "defect", ("duplicate", "NaN", "Infinity", "-Infinity", "array")
)
def test_cohort_file_intake_requires_strict_json(tmp_path, document, defect):
    directory = tmp_path / "cohort"
    shutil.copytree(DIRECTORY.parent / CURRENT_EDITION, directory)
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entry = manifest["siblings"][0]
    target = manifest_path if document == "manifest" else directory / entry["file"]
    original = target.read_text()
    if defect == "duplicate":
        key = "cohort_id" if document == "manifest" else "line_id"
        malformed = f'{{"{key}":"ambiguous",' + original.lstrip()[1:]
    elif defect == "array":
        malformed = "[]"
    else:
        malformed = f'{{"nonfinite":{defect},' + original.lstrip()[1:]
    target.write_text(malformed)
    if document == "export":
        entry["sha256"] = sha256(target.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(
        ValueError,
        match="duplicate JSON field|nonfinite JSON constant|expected a JSON object",
    ):
        build_cohort(directory)


def test_ten_native_status_vectors_cannot_clear_authored_holds(tmp_path):
    directory = tmp_path / "cohort"
    shutil.copytree(DIRECTORY.parent / CURRENT_EDITION, directory)
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    status = {"uninterpreted": [True, 1, 1.0, None, {"claim": "all clear"}]}
    for entry in manifest["siblings"]:
        path = directory / entry["file"]
        payload = json.loads(path.read_text())
        payload["native_status"] = status
        path.write_text(json.dumps(payload))
        entry["sha256"] = sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    generated = build_cohort(directory)
    envelopes = generated["states"][-1]["payload"]["envelopes"]
    expected_lines = EDITION_LINES[CURRENT_EDITION]
    assert {envelope["line_id"] for envelope in envelopes} == expected_lines
    assert all(
        canonical_json(envelope["native_status"]) == canonical_json(status)
        for envelope in envelopes
    )
    assert generated["projection"]["value"] == 0
    reasons = generated["projection"]["reasons"]
    assert any("return_due" in reason for reason in reasons)
    assert any("CANNOT_COMPARE" in reason for reason in reasons)
