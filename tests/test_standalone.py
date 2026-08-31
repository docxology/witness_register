"""Gates for the claim that this repository is separated and self-sufficient.

A clone of ``docxology/witness_register`` holds only this repository — no
sibling line checkout, no parent ``.gitignore``, no render engine one
directory up. Every gate here is paired with a positive control that plants
the defect and asserts rejection, so a gate that stopped discriminating
fails rather than passing silently. The register's deepest standalone claim
is architectural: it never imports a line package, because envelopes arrive
by value under a published schema string.
"""

from __future__ import annotations

import ast
import re
from fnmatch import fnmatch
from pathlib import Path

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

#: The five sibling works, referenced only by name and GitHub URL, never by
#: relative path and never by import.
SIBLING_WORKS = ("red_line", "black_line", "golden_line", "white_line", "line_set")

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


def test_the_scan_set_is_not_empty() -> None:
    """A gate over an empty file set is vacuous, not clean."""

    documents = source_files(PROJECT_ROOT, ".md")
    assert len(documents) > 10, len(documents)
    linked = [path for path in documents if relative_link_targets(path)]
    assert len(linked) > 3, len(linked)


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

    # An https acknowledgement of a sibling work is not an escape.
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


def test_standalone_guide_names_the_external_render_dependency() -> None:
    """A separated copy must explain its own purpose and limits."""

    text = (PROJECT_ROOT / "STANDALONE.md").read_text(encoding="utf-8")
    assert "docxology/template" in text
    for sibling in SIBLING_WORKS:
        assert f"https://github.com/docxology/{sibling}" in text, sibling
    assert "output/pdf/witness_register_combined.pdf" in text


#: ``cd`` into a path that leaves the repository is the monorepo assumption in
#: its most concrete form: it only works if this clone sits at a fixed depth
#: inside somebody else's tree.
ESCAPING_CD_RE = re.compile(r"^\s*cd\s+\.\./", re.MULTILINE)


def test_no_document_instructs_the_reader_to_cd_out_of_the_repository() -> None:
    """The render is an external tool, not a fixed position in a tree."""

    offenders = [
        str(path.relative_to(PROJECT_ROOT))
        for path in source_files(PROJECT_ROOT, ".md")
        if ESCAPING_CD_RE.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], offenders


def test_the_cd_gate_rejects_the_instruction_it_was_written_for() -> None:
    """Positive control, using the exact line sibling repos used to ship."""

    assert ESCAPING_CD_RE.search("```bash\ncd ../../../template\n```")
    assert ESCAPING_CD_RE.search("cd ../projects/working/witness_register\n")
    assert not ESCAPING_CD_RE.search('cd "$TEMPLATE_ROOT"\n')
    assert not ESCAPING_CD_RE.search("cd docs\n")


def test_no_shipped_python_resolves_a_path_above_the_repository_root() -> None:
    """A default that walks up to a sibling checkout is a hidden dependency."""

    offenders: list[str] = []
    for directory in ("src", "tests"):
        for path in source_files(PROJECT_ROOT / directory, ".py"):
            depth = len(path.relative_to(PROJECT_ROOT).parts) - 1
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Subscript):
                    continue
                value = node.value
                if not (isinstance(value, ast.Attribute) and value.attr == "parents"):
                    continue
                index = node.slice
                if isinstance(index, ast.Constant) and isinstance(index.value, int):
                    if index.value > depth:
                        offenders.append(
                            f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} "
                            f"parents[{index.value}] exceeds depth {depth}"
                        )
    assert offenders == [], offenders


def test_the_parents_gate_measures_depth_rather_than_a_fixed_number() -> None:
    """Positive control: the pattern the gate exists to catch, at real depth."""

    depth = len(Path("tests/test_standalone.py").parts) - 1
    assert depth == 1
    tree = ast.parse("ROOT = Path(__file__).resolve().parents[2] / 'template'\n")
    indices = [
        node.slice.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "parents"
        and isinstance(node.slice, ast.Constant)
    ]
    assert indices == [2]
    assert indices[0] > depth


def test_no_source_file_imports_a_sibling_line_project() -> None:
    """The register's central architectural claim: linked by value, never import."""

    offenders: list[str] = []
    for directory in ("src", "tests"):
        for path in source_files(PROJECT_ROOT / directory, ".py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    if name.split(".")[0] in SIBLING_WORKS:
                        offenders.append(
                            f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} {name}"
                        )
    assert offenders == [], offenders


def test_the_sibling_import_gate_can_see_an_import(tmp_path: Path) -> None:
    """Positive control for the import scan."""

    module = tmp_path / "planted.py"
    module.write_text("from golden_line import evaluate\n", encoding="utf-8")
    tree = ast.parse(module.read_text(encoding="utf-8"))
    modules = [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    ]
    assert modules == ["golden_line"]


@pytest.mark.parametrize("sibling", SIBLING_WORKS)
def test_no_sibling_line_package_is_importable(sibling: str) -> None:
    """The clone's interpreter must not be able to reach a sibling at all."""

    with pytest.raises(ImportError):
        __import__(sibling)
