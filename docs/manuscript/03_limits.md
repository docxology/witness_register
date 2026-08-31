# Limits and Epistemic Boundaries {#sec:limits}

Stated plainly, in the set's tradition of writing the edge of the claim.

**The tip is unbound.** An append-only chain guarantees that history inside
it cannot be rewritten undetected — but nothing inside the chain can detect
a discarded tip. A holder of the whole chain may present an earlier state as
current. The register hands out the tip digest for external anchoring and
solves nothing beyond that; until an anchor exists in a system the chain
does not control, chain integrity is a claim about internal consistency
only ([@prop:append-only]). Chain verification ([@prop:chain-verification-completeness])
confirms every state links to its predecessor and every digest matches, but
it verifies the presented segment — it cannot detect whether a newer state
exists outside it.

**Intake is a shape check.** A structurally perfect envelope can point at a
fabricated report. The register's acceptance asserts published shape, never
truth; verifying a report means returning to the exporting line, which is
the point of storing pointers instead of copies ([@def:envelope-record]).

**Relations are authored.** The register enforces invariants over relation
records, but the records themselves are entered by people (or by lines'
own tooling upstream). A missing relation is invisible to projection: if no
one registers the block, the posture will not show it. This is the honest
cost of refusing to parse native vocabularies — the register cannot infer
what it was never told, and it declines to guess ([@def:projection]).

**The posture is not a decision.** `+1` means nothing recorded forbids the
declared next use; it is not endorsement, safety, quality, or permission
from any boundary owner. `-1` resists a route; it does not condemn an aim.
`0` is an enumeration of holds, not a compromise. Any use of these symbols
without their state reference and reasons has already violated the design
([@prop:non-compensatory]). The posture is deterministic for identical state
and use ([@prop:projection-determinism]), but determinism is a property of
the code path — it does not make the underlying records true or the posture
warranted.

**The measures measure the register.** Relation fidelity, return
recoverability, and premature crowning rate evaluate bookkeeping. A register
can score perfectly on all three while every underlying report is wrong;
that would be the lines' failure to catch, each in its own vocabulary, and
the register's success at not hiding it.

**The scholarship is scoped to mechanisms.** The cited traditions —
linked timestamping, transparency logs, non-compensatory decision rules,
provenance records, boundary objects — are cited for how they keep books,
with every bibliographic record verified before use. None of them underwrites
any judgment, because the register makes none, and the borrowings stop where
each tradition's larger ambitions begin (distributed trust, gossip
infrastructure, utility theory, inference engines).

## Adversarial declarations {#sec:adversarial}

Because every input is self-declared — envelopes carry pointers to reports,
relations are authored, and declared next uses choose their own scope — the
instrument can be gamed by construction, and the honest response is to
demonstrate the attacks rather than deny them. Each of the following was
exercised against the real register.

**Malicious envelope injection.** An adversary can submit a structurally
valid envelope whose `report_ref` points to a fabricated or doctored report
the register has no access to verify. The register stores the pointer and
seals it into chain state; it never opens the pointed-to report. A stored
envelope with a valid shape certifies nothing about the report's content,
and the design's response is precisely the limitation stated above
([@def:envelope-record]): intake is a shape check, and storing pointers
instead of copies keeps the verification burden on the exporting line.

**Chain tip suppression.** A holder of the whole chain can present an
earlier state as current for an unbounded period, because nothing inside the
chain detects a discarded tip. The register hands out a `seal_tip` digest
for external anchoring ([@prop:append-only]), but until an anchor exists in
a system the chain does not control, the tip is unbound and a suppressed
later state is invisible to the register's own verification. The register's
`verify_chain` ([@prop:chain-verification-completeness]) confirms internal
consistency — every state links to its predecessor, every digest matches —
but it cannot detect whether a newer state exists outside the presented
segment.

**Relation inflation.** A submitter can record an agreement, dependency, or
incomparability relation that overstates consensus — a single `AGREES`
record entered by one party with no genuine counterparty review. The
register's projection weights every relation equally; it cannot assess
whether a relation was genuinely co-authored or whether the cited reference
backing it is accurate. The non-compensatory rule ([@prop:non-compensatory])
narrows the damage: a single block still forces $-1$, and no volume of
agreement lifts it. But agreement inflation can manufacture a misleadingly
supportive posture when no block exists — a risk the register cannot close
without semantic and institutional authority it does not have.

**Projection gaming via declared next use.** A caller can choose a
narrowly scoped $u$ that avoids known holds — declaring a use that evades
the unresolved tension, the outstanding return, or the unreviewed holding
that would otherwise cap the posture. The projection evaluates exactly the
use submitted; it does not explore adjacent uses or detect that a broader
or adjacent use would be blocked ([@def:projection]). The register's honest
response is to report the posture for the declared use with its `state_ref`
and reasons intact, so a reviewer comparing the declared use to the state's
content can ask whether the scope was chosen to game the result. The
projection is deterministic for identical inputs
([@prop:projection-determinism]), but determinism says nothing about whether
the declared use honestly names what is being proposed.

These are instances of a well-documented dynamic, not defects unique to
this design. A witness register that certified truth would make these
failure modes catastrophic, because a gamed posture would launder bad
records into apparent endorsement. The register's design response is to
refuse the certifying role entirely: a posture reports what the register
contains and what the projection computed, so a gamed $+1$ overstates
nothing but the presence of declared envelopes and the absence of recorded
blocks. The attacks also stay inspectable rather than hidden — the stored
envelopes, the relation records, the chain tip digest, and the declared
next use are the very state a reviewer reads, so a reviewer who asks
"does the report ref point at a real report?", "is this the latest tip?",
"were these relations genuinely co-authored?", or "does this declared
use honestly name what is being proposed?" is asking questions the
register state itself exposes. The instrument narrows what gaming can
counterfeit; it cannot remove the need for the human judgment those
questions require, and it never converts any posture into a safety
certification, an accreditation, or a permission.
