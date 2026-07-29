"""Return contracts: what must come back, from whom, and what stays open.

A return contract records why material is held, what is still alive as an
alternative, what evidence or consequence could change the state, who has
standing to provide it, what must remain protected while waiting, the
trigger for looking again, and an observable acceptance condition. It is a
record of obligation, not a countdown to approval: fulfilling a contract
earns a re-review, and the honest outcome of a return may be that the
material stays held.

A completed return NEVER closes more than the verified part. That rule is
modelled as fields, not prose: :func:`record_return` fills
``verification_result`` with what was actually verified and
``open_remainder`` with what was not, keeping the trigger unchanged so the
remainder stays due. The open record is never rewritten — the completed
record is a new record beside it, sharing the contract id so the pair reads
as one obligation and its answer.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ReturnContractRecord:
    """One obligation of return, held beside the envelopes it concerns.

    ``verification_result`` is the empty string until a return actually
    happens; emptiness is the honest open state, not a defect.
    ``prior_state_ref`` names the witness-state digest under which the
    contract was set, so a later return points back at the exact state it
    answers rather than rewriting it. ``open_remainder`` on a completed
    record names what the verified return did NOT close; the unchanged
    ``trigger`` keeps that remainder due.
    """

    contract_id: str
    subject_id: str
    why_held: str
    alternatives_live: tuple[str, ...]
    change_condition: str
    standing: str
    protected: str
    trigger: str
    acceptance_condition: str
    verification_result: str = ""
    open_remainder: str = ""
    prior_state_ref: str = ""

    def __post_init__(self) -> None:
        if not self.contract_id.strip():
            raise ValueError("contract_id must be non-blank")
        if not self.why_held.strip():
            raise ValueError(
                "why_held must be non-blank: a hold without a stated reason "
                "cannot be returned to"
            )
        if not self.trigger.strip():
            raise ValueError("trigger must be non-blank")
        if not self.acceptance_condition.strip():
            raise ValueError("acceptance_condition must be non-blank and observable")
        if self.verification_result and not self.verification_result.strip():
            raise ValueError(
                "verification_result must be empty (open) or carry content: "
                "a whitespace-only value would read as a verified return "
                "that verified nothing"
            )
        if self.open_remainder and not self.open_remainder.strip():
            raise ValueError(
                "open_remainder must be empty (nothing remains) or name the "
                "remainder: a whitespace-only value is neither"
            )

    @property
    def is_met(self) -> bool:
        """Whether this record carries a verified return with nothing left open.

        A partial return — verified result with a non-empty remainder — is
        NOT met: only the verified part closed, and the unchanged trigger
        keeps the remainder due.
        """

        return bool(self.verification_result) and not self.open_remainder


def record_return(
    contract: ReturnContractRecord,
    verification_result: str,
    open_remainder: str,
) -> ReturnContractRecord:
    """Record an actual return as a NEW record beside the open contract.

    ``verification_result`` must be non-blank — this function records a
    return that happened, never manufactures one. ``open_remainder`` names
    what the verified part did not close; pass the empty string only when
    nothing remains. The returned record keeps the original ``trigger``,
    ``why_held``, and every other field verbatim, so the remainder keeps its
    trigger and the prior rationale survives. The open record itself is not
    modified; append the returned record to a new state beside it.
    """

    if not verification_result.strip():
        raise ValueError(
            "verification_result must be non-blank: record_return records a "
            "return that happened, it does not manufacture one"
        )
    if contract.verification_result:
        raise ValueError(
            "the given record already carries a verified return; record a "
            "further return against the remainder as its own contract"
        )
    return replace(
        contract,
        verification_result=verification_result,
        open_remainder=open_remainder,
    )
