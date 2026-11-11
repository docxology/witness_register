"""Unclassified holdings: observations kept outside every status alphabet.

Some inputs fit no current category. The register holds them raw — verbatim
observation, provenance, candidate readings, and the stated reason they are
unclassified — and NEVER auto-creates a category for them. Promotion into
the relation vocabulary happens only through
:func:`witness_register.state.promote_unclassified`, which requires a
non-empty human decision reference and links the new relation back to the
original held record. The held record is never rewritten; history is
preserved, not replaced.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnclassifiedHeld:
    """One observation held outside the status and relation alphabets.

    ``raw_observation`` is verbatim: the register does not normalize,
    summarize, or reinterpret it. ``candidate_relations`` is a tuple of free
    text readings someone might later decide on, not a default decision.
    ``reason_unclassified`` states why no current category fits, so a later
    reviewer can tell a genuinely new kind of input from a lazily unfiled
    one.
    Validated state boundaries admit actual string fields and an immutable
    tuple of strings for candidates. Raw serialization retains malformed
    domains for inspection; it never splits a reading into characters.
    """

    held_id: str
    raw_observation: str
    provenance: str
    candidate_relations: tuple[str, ...]
    reason_unclassified: str
    review_moment: str

    def __post_init__(self) -> None:
        if not self.held_id.strip():
            raise ValueError("held_id must be non-blank")
        if not self.raw_observation.strip():
            raise ValueError(
                "raw_observation must be non-blank: an empty holding holds nothing"
            )
        if not self.reason_unclassified.strip():
            raise ValueError(
                "reason_unclassified must be non-blank: holding without a "
                "stated reason is silent rejection"
            )
