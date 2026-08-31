"""Public surface discipline and version bindings across every copy."""

from __future__ import annotations

import re
from pathlib import Path

import witness_register

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_all_is_sorted_and_complete() -> None:
    assert witness_register.__all__ == sorted(witness_register.__all__)
    for name in witness_register.__all__:
        assert getattr(witness_register, name) is not None


def test_all_has_no_duplicates() -> None:
    assert len(witness_register.__all__) == len(set(witness_register.__all__))


def test_version_matches_pyproject() -> None:
    text = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, re.MULTILINE)
    assert match is not None
    assert match.group(1) == witness_register.__version__


def test_version_matches_manuscript_config() -> None:
    text = (PROJECT_ROOT / "docs" / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    match = re.search(r'version: "([^"]+)"', text)
    assert match is not None
    assert match.group(1) == witness_register.__version__


def test_version_has_a_changelog_window() -> None:
    text = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {witness_register.__version__}" in text


def test_the_package_docstring_states_the_non_claims() -> None:
    doc = witness_register.__doc__
    assert doc is not None
    for phrase in (
        "NEVER imports any line package",
        "NEVER parses, compares, ranks, averages, merges",
        "NEVER auto-creates a category",
        "NEVER infers consent or permission",
        "NEVER mutates or rewrites history",
        "bounded posture",
        "unbound without EXTERNAL anchoring",
    ):
        assert phrase in doc, phrase


def test_the_envelope_schema_is_the_published_literal() -> None:
    assert witness_register.ENVELOPE_SCHEMA == "line.report-envelope/1.0"
