"""Append-only authority claims, never inferred permission or evidence truth."""

from dataclasses import dataclass
from enum import Enum

from .envelopes import HEX_DIGEST_RE


class DecisionKind(str, Enum):
    """Authored lifecycle acts; acknowledgment has no discharging authority."""

    ACKNOWLEDGE = "ACKNOWLEDGE"
    RESOLVE = "RESOLVE"
    RESCOPE = "RESCOPE"
    REOPEN = "REOPEN"


class TargetKind(str, Enum):
    """Exact canonical record type a decision claims to concern."""

    RELATION = "RELATION"
    CONTRACT = "CONTRACT"


@dataclass(frozen=True)
class DecisionEvent:
    """One scoped decision claim against an unchanged prior record.

    The basis names the state actually reviewed. References are not fetched;
    evidence and provenance remain authored claims for human review. Multiple
    incompatible acts for the same target/use hold rather than picking one.
    """

    decision_id: str
    kind: DecisionKind
    target_kind: TargetKind
    target_ref: str
    human_decision_ref: str
    evidence_ref: str
    declared_next_use: str
    basis_state_ref: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, DecisionKind):
            raise ValueError("kind must be a DecisionKind")
        if not isinstance(self.target_kind, TargetKind):
            raise ValueError("target_kind must be a TargetKind")
        for field in (
            "decision_id",
            "human_decision_ref",
            "evidence_ref",
            "declared_next_use",
        ):
            if (
                not isinstance(getattr(self, field), str)
                or not getattr(self, field).strip()
            ):
                raise ValueError(f"{field} must be a non-blank string")
        for field in ("target_ref", "basis_state_ref"):
            value = getattr(self, field)
            if not isinstance(value, str) or not HEX_DIGEST_RE.fullmatch(value):
                raise ValueError(f"{field} must be exactly 64 lowercase hex characters")
        if (
            self.kind is DecisionKind.RESCOPE
            and self.target_kind is not TargetKind.CONTRACT
        ):
            raise ValueError("RESCOPE must target an exact open contract")
        if (
            self.kind is DecisionKind.RESOLVE
            and self.target_kind is not TargetKind.RELATION
        ):
            raise ValueError("RESOLVE must target an exact relation")


def decision_status(
    events: tuple[DecisionEvent, ...], target_ref: str, use: str
) -> str:
    """Replay one scope without letting order arbitrate contradictory claims."""

    kinds = {
        event.kind
        for event in events
        if event.target_ref == target_ref
        and event.declared_next_use == use
        and event.kind is not DecisionKind.ACKNOWLEDGE
    }
    if DecisionKind.REOPEN in kinds and len(kinds) > 1:
        return "conflict"
    if kinds & {DecisionKind.RESOLVE, DecisionKind.RESCOPE}:
        return "cleared"
    if DecisionKind.REOPEN in kinds:
        return "reopened"
    return "open"
