"""Consumer gates for a separated, self-sufficient Witness Register clone.

Envelopes arrive by value. The isolated interpreter exercises an installed
distribution without sibling packages or checkout imports; document links
and disposable artifact rules are checked independently.
"""

from __future__ import annotations

import json
import re
from fnmatch import fnmatch
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: Generated, vendored, or cache directories that are not part of the source
#: of truth. A clone may or may not have them; neither case is interesting.
SKIP_DIRECTORIES = frozenset(
    {
        ".git",
        ".venv",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "__pycache__",
        "output",
        "htmlcov",
        "build",
        "dist",
        "node_modules",
    }
)

#: The instruments and reader, referenced by name and GitHub URL, never by
#: relative path and never by import.
SIBLING_WORKS = (
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
    "line_set",
)

#: ``[text](target)`` with an optional ``"title"``. Bare autolinks in angle
#: brackets are URLs by construction and carry no relative path to resolve.
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def source_files(root: Path, suffix: str) -> list[Path]:
    """Every file under *root* with *suffix*, excluding generated trees."""

    found: list[Path] = []
    for path in sorted(root.rglob(f"*{suffix}")):
        if any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            found.append(path)
    return found


def relative_link_targets(path: Path) -> list[str]:
    """Return the link targets in *path* that are relative filesystem paths."""

    targets: list[str] = []
    for target in MARKDOWN_LINK_RE.findall(path.read_text(encoding="utf-8")):
        if target.startswith("#") or SCHEME_RE.match(target):
            continue
        bare = target.split("#", 1)[0]
        if bare:
            targets.append(bare)
    return targets


def escaping_links(root: Path) -> list[str]:
    """Relative markdown links that resolve outside *root*."""

    escapes: list[str] = []
    for path in source_files(root, ".md"):
        for target in relative_link_targets(path):
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                escapes.append(f"{path.relative_to(root)} -> {target}")
    return escapes


def unresolvable_links(root: Path) -> list[str]:
    """Relative markdown links inside *root* that point at nothing."""

    dangling: list[str] = []
    for path in source_files(root, ".md"):
        for target in relative_link_targets(path):
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                continue
            if not resolved.exists():
                dangling.append(f"{path.relative_to(root)} -> {target}")
    return dangling


def test_no_markdown_link_resolves_outside_the_repository() -> None:
    """Sibling works are addressed by name and URL, never by relative path."""

    assert escaping_links(PROJECT_ROOT) == []


def test_every_relative_markdown_link_points_at_a_file_that_exists() -> None:
    """A link inside the root that resolves to nothing is dead in a clone too."""

    assert unresolvable_links(PROJECT_ROOT) == []


def test_the_link_gate_rejects_a_planted_escape_and_a_planted_dead_link(
    tmp_path: Path,
) -> None:
    """Positive control for both link checks."""

    (tmp_path.parent / "outside.md").write_text("# outside\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "here.md").write_text("# here\n", encoding="utf-8")

    clean = tmp_path / "clean.md"
    clean.write_text("See [here](docs/here.md).\n", encoding="utf-8")
    assert escaping_links(tmp_path) == []
    assert unresolvable_links(tmp_path) == []

    clean.write_text(
        "See [the map](../outside.md) and [a ghost](docs/ghost.md).\n",
        encoding="utf-8",
    )
    assert escaping_links(tmp_path) == ["clean.md -> ../outside.md"]
    assert unresolvable_links(tmp_path) == ["clean.md -> docs/ghost.md"]

    # An https acknowledgment of a sibling work is not an escape.
    clean.write_text(
        "See [line_set](https://github.com/docxology/line_set).\n",
        encoding="utf-8",
    )
    assert escaping_links(tmp_path) == []
    assert unresolvable_links(tmp_path) == []


def ignore_patterns(root: Path) -> list[str]:
    """The non-comment patterns declared in the tracked ``.gitignore``."""

    text = (root / ".gitignore").read_text(encoding="utf-8")
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def is_ignored(relative: str, patterns: list[str]) -> bool:
    """Whether *relative* is matched by any pattern, directory patterns included."""

    parts = relative.split("/")
    for raw in patterns:
        pattern = raw.rstrip("/").lstrip("/")
        if any(fnmatch(part, pattern) for part in parts):
            return True
        if fnmatch(relative, pattern):
            return True
    return False


def test_a_tracked_gitignore_covers_every_disposable_artifact() -> None:
    """A clone inherits no ignore rules; this file is the only source of them."""

    assert (PROJECT_ROOT / ".gitignore").is_file()
    patterns = ignore_patterns(PROJECT_ROOT)
    disposable = [
        "output/pdf/witness_register_combined.pdf",
        "src/witness_register/__pycache__/state.cpython-312.pyc",
        "witness_register.egg-info/PKG-INFO",
        ".venv/bin/python",
        ".coverage",
        ".coverage.project",
        "htmlcov/index.html",
        ".pytest_cache/CACHEDIR.TAG",
        ".ruff_cache/CACHEDIR.TAG",
    ]
    unignored = [item for item in disposable if not is_ignored(item, patterns)]
    assert unignored == [], unignored


def test_the_gitignore_does_not_swallow_the_source_of_truth() -> None:
    """Positive control: a matcher that matched everything would pass above."""

    patterns = ignore_patterns(PROJECT_ROOT)
    tracked = [
        "src/witness_register/state.py",
        "tests/test_standalone.py",
        "docs/manuscript/config.yaml",
        "docs/manuscript/02_design.md",
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "STANDALONE.md",
        ".gitignore",
    ]
    swallowed = [item for item in tracked if is_ignored(item, patterns)]
    assert swallowed == [], swallowed


def test_uv_lock_is_deliberately_tracked() -> None:
    """The pinned dev environment is part of the reproducibility statement."""

    assert (PROJECT_ROOT / "uv.lock").is_file()
    assert not is_ignored("uv.lock", ignore_patterns(PROJECT_ROOT))


@pytest.fixture(scope="module")
def built_distributions(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """Build both real distribution formats once, without editable installs."""
    uv = shutil.which("uv")
    assert uv is not None, "uv is required to provision installed consumers"
    destination = tmp_path_factory.mktemp("witness-distributions")
    result = subprocess.run(
        [
            uv,
            "build",
            "--sdist",
            "--wheel",
            "--out-dir",
            str(destination),
            str(PROJECT_ROOT),
        ],
        cwd=destination,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = tuple(destination.glob("*.whl"))
    sdists = tuple(destination.glob("*.tar.gz"))
    assert len(wheels) == len(sdists) == 1
    return {"wheel": wheels[0], "sdist": sdists[0]}


@pytest.mark.parametrize("distribution_kind", ("wheel", "sdist"))
def test_register_works_with_no_sibling_packages(
    tmp_path: Path, built_distributions: dict[str, Path], distribution_kind: str
) -> None:
    """Consume the actual ten-envelope cohort through installed public APIs."""
    uv = shutil.which("uv")
    assert uv is not None, "uv is required to provision installed consumers"
    environment = tmp_path / "consumer-environment"
    python = environment / "bin" / "python"
    for command in (
        [uv, "venv", "--python", sys.executable, str(environment)],
        [
            uv,
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            str(built_distributions[distribution_kind]),
        ],
    ):
        result = subprocess.run(
            command, cwd=tmp_path, capture_output=True, text=True, check=False
        )
        assert result.returncode == 0, result.stdout + result.stderr
    cohort = tmp_path / "cohort"
    shutil.copytree(
        PROJECT_ROOT / "data/envelopes/releases/v0.4.0-element-admission", cohort
    )
    program = """
import importlib
import json
import sys
from hashlib import sha256
from pathlib import Path

cohort = Path(sys.argv[1])
siblings = json.loads(sys.argv[2])
checkout = Path(sys.argv[3]).resolve()
for entry in sys.path:
    path = Path(entry).resolve()
    assert path != checkout and checkout not in path.parents, sys.path
for sibling in (*siblings, "scripts"):
    try:
        importlib.import_module(sibling)
    except ModuleNotFoundError as error:
        assert error.name == sibling, (sibling, error)
    else:
        raise AssertionError(f"checkout or sibling unexpectedly importable: {sibling}")

import witness_register
from witness_register import (
    RelationRecord, RelationType, ReturnContractRecord, canonical_json,
    canonical_projection, canonical_state_payload, genesis_state, intake_envelope,
    project, update_state, verify_chain,
)
assert Path(witness_register.__file__).resolve().is_relative_to(Path(sys.prefix))
manifest = json.loads((cohort / "manifest.json").read_text())
expected = json.loads((cohort / "co_registration.json").read_text())
records = []
payloads = {}
for entry in manifest["siblings"]:
    raw = (cohort / entry["file"]).read_bytes()
    assert sha256(raw).hexdigest() == entry["sha256"]
    payload = json.loads(raw)
    record, issues = intake_envelope(payload)
    assert record is not None and issues == (), issues
    assert record.line_id == entry["repository"].split("/")[1]
    payloads[record.line_id] = payload
    records.append(record)
assert set(payloads) == set(siblings) - {"line_set"}
assert len(records) == 10
assert len({record.subject_id for record in records}) == 10
first = genesis_state(
    manifest["cohort_id"], manifest["reviewed_on"], envelopes=tuple(records)
)
authored = expected["states"][-1]["payload"]
relations = tuple(
    RelationRecord(**{
        **{key: tuple(value) if isinstance(value, list) else value
           for key, value in item.items() if key != "record_schema"},
        "relation_type": RelationType(item["relation_type"]),
    })
    for item in authored["relations"]
)
returns = tuple(
    ReturnContractRecord(**{
        key: tuple(value) if isinstance(value, list) else value
        for key, value in item.items() if key != "record_schema"
    })
    for item in authored["returns"]
)
second = update_state(
    first, manifest["reviewed_on"], relations=relations, returns=returns
)
assert verify_chain((first, second)) == ()
assert second.prior_ref == first.state_digest
for state, pinned in zip((first, second), expected["states"], strict=True):
    assert state.state_digest == pinned["state_digest"]
    stored = canonical_state_payload(
        state.subject_id, state.review_moment, state.envelopes, state.relations,
        state.unclassified, state.returns, state.prior_ref, state.decisions,
        state.history_refs,
    )
    assert stored == pinned["payload"]
    for envelope in stored["envelopes"]:
        payload = payloads[envelope["line_id"]]
        assert canonical_json(envelope["native_status"]) == canonical_json(payload["native_status"])
        assert envelope["report_ref"] == payload["report_ref"]
        assert envelope["scope_and_nonclaims"] == payload["scope_and_nonclaims"]
        assert envelope["source_snapshot_refs"] == payload["source_snapshot_refs"]
        if envelope["line_id"] in {"violet_line", "copper_line", "iron_line"}:
            assert envelope["source_snapshot_refs"] == []
posture = project(second, manifest["declared_next_use"])
assert posture.state_ref == second.state_digest
assert posture.value == 0
assert any("return_due" in reason for reason in posture.reasons)
assert any("CANNOT_COMPARE" in reason for reason in posture.reasons)
assert canonical_projection(posture) == expected["projection"]
assert not set(siblings).intersection(sys.modules)
assert "scripts" not in sys.modules
"""
    result = subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            program,
            str(cohort),
            json.dumps(SIBLING_WORKS),
            str(PROJECT_ROOT),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
