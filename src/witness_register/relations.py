"""Cross-line relations: separate records that describe, never override.

A relation is the register's way of saying "these envelopes stand in this
kind of tension, dependency, agreement, or protection with one another" —
as a record of its own, beside the envelopes, never inside them. Relations
DESCRIBE; they never replace, rewrite, or re-score any line's status. A
relation that contradicts a line's native report is a recorded disagreement,
not a correction.

``human_decision_ref`` is the register's honesty about authority: an empty
string means NOT_RECORDED — no human decision is on file — and that is a
first-class honest value, never a default verdict. Machinery in this package
treats an unresolved relation as unresolved; nothing here manufactures a
decision that was not made.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .envelopes import HEX_DIGEST_RE

#: The honest value of an authority field with no decision on file.
NOT_RECORDED = ""


class RelationType(str, Enum):
    """The register's relation vocabulary.

    Each member names a way envelopes can stand to one another. None of them
    is a score, and none of them rewrites a line's own status:

    - ``NON_COMPENSATORY_BLOCK``: one line's finding blocks a route no other
      line's strength may compensate for.
    - ``UNRESOLVED_DEPENDENCY``: one report's meaning depends on something
      still open elsewhere.
    - ``PROTECTED_ABSENCE``: material is absent because a boundary protects
      it; protection is not missing evidence to be mined.
    - ``DIRECTIONAL_TENSION``: support and resistance are co-present and
      pull in different directions; both surfaces are kept.
    - ``UNCLASSIFIED_OBSERVATION``: something was observed that fits no
      current category; it is held, not forced.
    - ``RETURN_DUE``: a return contract is outstanding for this material.
    - ``CANNOT_COMPARE``: the envelopes' vocabularies do not admit the
      comparison being asked for.
    - ``AGREES``: independent reports point the same way, stated as a
      relation — never merged into one number.
    """

    NON_COMPENSATORY_BLOCK = "NON_COMPENSATORY_BLOCK"
    UNRESOLVED_DEPENDENCY = "UNRESOLVED_DEPENDENCY"
    PROTECTED_ABSENCE = "PROTECTED_ABSENCE"
    DIRECTIONAL_TENSION = "DIRECTIONAL_TENSION"
    UNCLASSIFIED_OBSERVATION = "UNCLASSIFIED_OBSERVATION"
    RETURN_DUE = "RETURN_DUE"
    CANNOT_COMPARE = "CANNOT_COMPARE"
    AGREES = "AGREES"


@dataclass(frozen=True)
class RelationRecord:
    """One described relation among co-registered envelopes.

    ``source_report_refs`` names the envelope ``report_ref`` digests this
    relation is about and must be non-empty: a relation about nothing is not
    a record. ``support_refs``, ``resistance_refs``, and
    ``protected_boundary_refs`` keep the relation's surfaces separate so a
    conflict survives as two sides, not a summary. ``return_contract_ref``
    links a ``RETURN_DUE`` relation to its contract. ``human_decision_ref``
    empty means NOT_RECORDED. ``promoted_from_ref``, when non-empty, names
    the ``held_id`` of the unclassified record this relation was promoted
    from — the promotion links forward; the held record is never rewritten.
    """

    relation_id: str
    subject_id: str
    source_report_refs: tuple[str, ...]
    relation_type: RelationType
    bounded_description: str
    support_refs: tuple[str, ...] = ()
    resistance_refs: tuple[str, ...] = ()
    protected_boundary_refs: tuple[str, ...] = ()
    return_contract_ref: str = ""
    human_decision_ref: str = NOT_RECORDED
    promoted_from_ref: str = ""

    def __post_init__(self) -> None:
        if not self.relation_id.strip():
            raise ValueError("relation_id must be non-blank")
        if not self.source_report_refs:
            raise ValueError(
                "source_report_refs must be non-empty: a relation about "
                "nothing is not a record"
            )
        for ref in self.source_report_refs:
            if not HEX_DIGEST_RE.match(ref):
                raise ValueError(
                    f"source_report_refs entry {ref!r} is not a 64-char "
                    "lowercase hex envelope report_ref"
                )
        if not self.bounded_description.strip():
            raise ValueError(
                "bounded_description must be non-blank: an undescribed "
                "relation cannot be reviewed"
            )
        if not isinstance(self.relation_type, RelationType):
            raise ValueError(
                f"relation_type must be a RelationType, got {self.relation_type!r}"
            )
        if self.human_decision_ref and not self.human_decision_ref.strip():
            raise ValueError(
                "human_decision_ref must be empty (NOT_RECORDED) or non-blank; "
                "whitespace-only is not a recorded decision"
            )
