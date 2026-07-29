# Scholarship

The register's mechanisms are small and none of them is new. Each design
element below names the tradition it borrows from, what exactly is taken,
and where the register deliberately stops short of the cited work's ambition.
Every bibliographic record was verified against Crossref, the RFC Editor, or
the W3C on 2026-07-29 before being cited; nothing here is cited from memory.

**The sealed chain is linked timestamping.** The witness state chain — each
state carrying a digest over its complete canonical content and the digest of
the state it extends — is the linking scheme of Haber and Stornetta
[@haber1991], who showed that chaining document digests makes the *order and
content* of a record series tamper-evident without trusting the record
keeper's clock. The register takes exactly that: internal tamper evidence.
It does not take their further apparatus (distributed trust, published
widely-witnessed values), which is why its tip is unbound — see the limits
section. The digest-over-canonical-content discipline itself is the
hash-authentication tradition Merkle formalized for signatures and trees
[@merkle1990].

**The tip-unbound limitation is the log-consistency problem.** Certificate
Transparency [@rfc6962; @rfc9162] built public append-only logs for
certificates and confronted the same edge this register states: a log can be
internally consistent while presenting different views to different
observers, so consistency proofs must be checked *between* observers, outside
the log. CT's answer — gossip, multiple logs, external auditing — is an
infrastructure the register does not have and does not claim; `seal_tip`
hands out the value such an infrastructure would anchor, and the limitation
is stated rather than solved.

**Non-compensatory means what decision theory means by it.** The projection's
invariants — a block that no volume of agreement buys back, a protected
absence no strength outweighs, precedence in a fixed order — are
non-compensatory decision rules in the sense surveyed by Fishburn
[@fishburn1974]: lexicographic structures in which one criterion's verdict
cannot be traded against quantities of another. The register borrows the
*shape* deliberately, because compensatory aggregation is exactly the
averaging of instruments the design review forbids. It does not borrow the
utility apparatus: the posture is not a utility, not a preference, and not
optimal by any criterion — it is a bounded interface value with reasons.

**Relations describe; provenance vocabularies made that a data model.** The
rule that relation records describe stored envelopes without rewriting them
— disagreement kept as two surfaces, authority fields honest about
NOT_RECORDED — follows the posture of the W3C provenance data model
[@w3cprovdm], which types what was derived from what, and by whom, as
records *about* artifacts rather than edits *to* them. The register's
vocabulary is far smaller than PROV's and deliberately so: eight relation
types entered by people, no inference engine, no automatic derivation.

**The envelope is a boundary object in the strict sense.** Star and
Griesemer's standardized forms [@star1989] are artifacts robust enough to
travel between communities while staying locally interpretable — their
canonical examples are records that different groups fill and read without
adopting one another's theories. The `line.report-envelope/1.0` record is
built to that specification: ten fields any line can export and the register
can hold, with `native_status` staying in the exporting instrument's own
vocabulary precisely so that transport never becomes translation. Star's own
caution applies and is adopted: not everything that sits between groups is a
boundary object, and the envelope earns the name only while each line
remains authoritative over its own field.

What none of these citations does is underwrite the register's judgments,
because the register makes none: the borrowed mechanisms are bookkeeping
mechanisms, and the cited traditions are cited for how they keep books, not
for any claim about the truth of what the books record.
