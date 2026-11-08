"""Consumer gates for a separated, self-sufficient Witness Register clone.

Envelopes arrive by value. The isolated interpreter exercises the package with
no sibling packages or site-packages available; document links and disposable
artifact rules are checked independently.
"""

from __future__ import annotations

import json
import re
from fnmatch import fnmatch
from pathlib import Path
import subprocess
import sys

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


def test_register_works_with_no_sibling_packages(tmp_path: Path) -> None:
    """Import and use the real package with only its source and the stdlib."""

    program = """
import importlib
import json
import sys

sys.path.insert(0, sys.argv[1])
siblings = json.loads(sys.argv[2])
for sibling in siblings:
    try:
        importlib.import_module(sibling)
    except ModuleNotFoundError as error:
        assert error.name == sibling, (sibling, error)
    else:
        raise AssertionError(f"sibling unexpectedly importable: {sibling}")

from witness_register import (
    canonical_json, genesis_state, intake_envelope, project, verify_chain,
)

records = []
for line_id, digest in (("copper_line", "b" * 64), ("iron_line", "c" * 64)):
    payload = {
        "schema_version": "line.report-envelope/1.0",
        "line_id": line_id,
        "subject_id": "isolated-consumer",
        "review_date": "2026-11-08",
        "registry_version": "0.1.0",
        "registry_digest": "a" * 64,
        "native_status": {"vector": [{"status": "opaque", "quantity": None}]},
        "report_ref": digest,
        "source_snapshot_refs": [],
        "scope_and_nonclaims": ["Constructed input; no native report verified."],
    }
    record, issues = intake_envelope(payload)
    assert record is not None, issues
    assert canonical_json(record.native_status) == canonical_json(payload["native_status"])
    records.append(record)
state = genesis_state("isolated-consumer", "2026-11-08", tuple(records))
assert verify_chain((state,)) == ()
posture = project(state, "inspect this constructed envelope")
assert posture.state_ref == state.state_digest
assert posture.value == 1
assert not set(siblings).intersection(sys.modules)
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            program,
            str(PROJECT_ROOT / "src"),
            json.dumps(SIBLING_WORKS),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
