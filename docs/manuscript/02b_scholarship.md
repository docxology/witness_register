# Scholarship and Intellectual Lineage {#sec:scholarship}

The register's mechanisms are small, and none of them is new. Each design
element below names the tradition it borrows from, what exactly is taken,
and where the register deliberately stops short of the cited work's
ambition. The scholarship does not validate the register's postures — the
register makes no judgments to validate. The cited traditions are cited for
how they keep books, not for any claim about the truth of what the books
record. Every bibliographic record was verified against Crossref, the RFC
Editor, or the W3C on 2026-07-29 before being cited; nothing here is cited
from memory.

## Linked timestamping and the sealed chain

The witness state chain — each state carrying a digest over its complete
canonical content and the digest of the state it extends — is the linking
scheme of Haber and Stornetta [@haber1991], who showed that chaining
document digests makes the *order and content* of a record series
tamper-evident without trusting the record keeper's clock. Their scheme
addressed the problem of certifying when a document was created or last
modified: the linking step — each certificate including a hash of the
previous — makes retroactive insertion or reordering detectable, because
any change to an earlier link breaks every subsequent digest. The register
takes exactly that: internal tamper evidence inside the chain.

What the register does not take is the further apparatus. Haber and
Stornetta's scheme includes distributed trust mechanisms — linking with
other clients, publishing hash values in widely-witnessed media — to guard
against a dishonest time-stamping service issuing backdated certificates
that form an internally consistent but temporally false chain. The
register's tip is unbound for precisely this reason: an append-only chain
guarantees that history inside it cannot be rewritten undetected, but
nothing inside the chain can detect a discarded tip. A holder of the whole
chain may present an earlier state as current, and the chain itself cannot
know. The limitation is stated rather than solved — see the limits section
([@sec:limits]) — and `seal_tip` hands out the value such distributed
infrastructure would anchor.

The digest-over-canonical-content discipline itself belongs to the
hash-authentication tradition Merkle formalized for signatures and trees
[@merkle1990]. The register's `state_digest` is a single SHA-256 hash
over canonical JSON — a degenerate one-element tree — and the re-derivation
check before every chain extension is the Merkle-verification idiom
applied to the smallest possible unit: a state sealed against itself. The
tree is absent because the register holds a linear chain rather than a
branching structure of many leaves; the verification discipline is the
same.

## Certificate Transparency and the tip-unbound problem

The tip-unbound limitation is not a defect of the register's design; it is
the log-consistency problem that Certificate Transparency (CT) made
explicit at infrastructure scale. CT's original specification [@rfc6962]
built public append-only logs for X.509 certificates, and the current
version [@rfc9162] refines the same architecture. A CT log is a Merkle
tree hash chain that grows monotonically; monitors verify that the log is
append-only, and auditors check that particular certificates appear. The
critical insight — the one the register restates at a much smaller scale —
is that a log can be internally consistent while presenting different views
to different observers. A log operator who serves a truncated view to one
monitor and the full chain to another has produced two consistent proofs
from different states, and neither proof by itself reveals the divergence.

CT's answer is infrastructure the register does not have and does not
claim: gossip protocols between monitors, multiple independent logs, and
external auditing. These mechanisms move the consistency check *between*
observers, outside the log. The register's `seal_tip` is the value such an
infrastructure would anchor; until an anchor exists in a system the chain
does not control, chain integrity is a claim about internal consistency
only. The register states this limitation rather than implying it has been
solved, and the scholarship makes the provenance of the limitation
explicit: it is not a missing feature but a known structural boundary of
append-only logs, acknowledged at full scale by the CT working group.

## Non-compensatory decision rules

The projection's invariants — a block that no volume of agreement buys
back, a protected absence no strength outweighs, precedence in a fixed
order — are non-compensatory decision rules in the sense surveyed by
Fishburn [@fishburn1974]. Fishburn's survey of lexicographic orders
formalizes structures in which one criterion's verdict cannot be traded
against quantities of another: the first-ranked attribute decides, and
lower-ranked attributes are consulted only when higher-ranked ones fail to
discriminate. The register's projection precedence — unresolved block
before empty state before any hold, with a single block forcing `-1` under
any volume of `AGREES` relations — is a small instantiation of that
structure, deliberately chosen because compensatory aggregation is exactly
the averaging of instruments the design review forbids.

What the register does not borrow is the utility apparatus. Fishburn's
survey is grounded in decision theory and utility maximization:
lexicographic orders are studied as preference structures, and the
question is whether a lexicographic preference can be represented by a
real-valued utility function (it cannot, in the general case — a fact the
register exploits structurally). The register's posture is not a utility,
not a preference, and not optimal by any criterion. It is a bounded
interface value carrying the digest of the state that earned it, the
reasons it holds, and nothing more. The borrowing is confined to the
*shape* of non-compensatory ordering; the theoretical apparatus that
accompanies that shape in decision theory is set aside.

The same point applies in the other direction. Fishburn's survey covers
lexicographic orders over multidimensional attribute spaces; the
register's precedence is a flat list of seven checks, not a hierarchy of
attributes. The register does not implement a lexicographic decision rule
in the formal sense — it implements a precedence list whose shape
resembles one, and the resemblance is the reason for the citation. The
formal claim is stated in the formalism section
([@sec:formalism]): non-compensatory means non-compensatory, and
[@prop:non-compensatory] is enforced in code rather than asserted in
prose.

## Provenance as description, not rewriting

The rule that relation records describe stored envelopes without rewriting
them — disagreement kept as two surfaces, authority fields honest about
`NOT_RECORDED`, a holding stored raw beside its later classification
rather than replaced by it — follows the posture of the W3C provenance
data model [@w3cprovdm]. PROV-DM types what was derived from what, and by
whom, as records *about* artifacts rather than edits *to* them. An entity
record does not overwrite the entity; a derivation does not delete the
thing derived from. The register's relation records are built to the same
discipline: an `AGREES` relation does not merge the agreed-upon envelopes,
a `BLOCK` does not delete what it blocks, and a `RETURN_DUE` does not
presume what the return will contain.

The register's vocabulary is far smaller than PROV's and deliberately so.
PROV includes entities, activities, agents, derivations, generations,
usage, attribution, association, delegation, communication, and a formal
constraint language over them. The register has eight relation types
entered by people, no inference engine, and no automatic derivation. The
narrowing is not a criticism of PROV — it is a scope decision: the
register stores what people record, and the people who record it are
responsible for the categories they use. A provenance vocabulary large
enough to model scientific workflows, software builds, and data pipelines
would be overbuilt for eight relation types over four report envelopes.

The structural discipline — records about artifacts that never mutate the
artifacts — is the single point the register takes from PROV, and the
citation acknowledges the lineage without claiming equivalence.

## The envelope as a boundary object

Star and Griesemer's standardized forms [@star1989] are artifacts robust
enough to travel between communities while staying locally interpretable.
The paper's canonical examples are standardized data-entry forms that
amateur collectors and professional zoologists filled and read without
adopting one another's theories: the form carries information across a
boundary without requiring either side to convert to the other's
conceptual scheme. The `line.report-envelope/1.0` record is built to that
specification: ten fields any line can export and the register can hold,
with `native_status` staying in the exporting instrument's own vocabulary
precisely so that transport never becomes translation.

Star and Griesemer's typology distinguishes four kinds of boundary object:
repositories, ideal types, coincident boundaries, and standardized forms.
The envelope is a standardized form — a fixed shape, filled in the same
way each time, whose function is to carry information across a boundary
without negotiating it away. The register's refusal to parse, compare,
rank, average, or merge `native_status` is the operationalization of that
design choice: the field stays in the line's own vocabulary because the
register is a transport surface, not a translation layer.

Star later objected to how the concept had been taken up, in particular to
its application to any object that happens to sit between two groups,
detached from the infrastructural and standardizing work the original
study was about [@star1989]. Her caution applies here and is adopted: not
everything that sits between groups is a boundary object, and the envelope
earns the name only while each line remains authoritative over its own
field. Four Python packages and one shared register are not the Museum of
Vertebrate Zoology, and the register's relationship to the lines is not a
negotiation between amateur collectors and professional zoologists. What
is taken from the 1989 paper is a design move — a standardized form whose
local fields stay local — and the concept is not doing evidentiary work
beyond that.

## What the borrowings borrow and what they leave

The lineage-to-wire map is deliberately asymmetric:

| Scholarly tradition | Register's operational slice | Boundary preserved |
| --- | --- | --- |
| Linked timestamping [@haber1991] | chained digests for internal tamper evidence | distributed trust mechanisms; the tip is unbound |
| Hash authentication [@merkle1990] | digest-over-canonical-content seals; re-derivation check before extension | the tree structure; the register holds a linear chain |
| Certificate Transparency [@rfc6962; @rfc9162] | the log-consistency problem stated as the tip-unbound limitation | gossip, multiple logs, external auditing — infrastructure the register does not have |
| Non-compensatory decision rules [@fishburn1974] | lexicographic precedence shape: a single block forces `-1` under any volume of agreement | the utility apparatus; the posture is not a utility, not optimal, and not a preference |
| Provenance data model [@w3cprovdm] | records *about* artifacts that never mutate the artifacts | the full PROV vocabulary, inference engine, and constraint language |
| Boundary objects [@star1989] | a standardized form whose local field stays local; transport without translation | the institutional ecology; the register is not the Museum of Vertebrate Zoology |

The table is a design map, not a claim that six citations capture these
traditions. Its purpose is to make the borrowing inspectable and the
non-borrowing equally explicit: each row states what was taken and where
the taking stops.

## What the lineage does and does not license

Citing these works situates the register; it does not borrow their
authority. None of these authors claims that following a bookkeeping
discipline guarantees a correct result, and neither does this register.
The lineage explains *why* each mechanism is worth making inspectable;
the [formal core](#sec:formalism) and [further propositions](#sec:further-formalism)
state *what the evaluator can actually check*, which is only whether the
declared invariants hold — never whether the underlying reports are true,
the relations are warranted, or the posture is wise.

The register's scholarship is therefore scoped to mechanisms: linked
timestamping for the chain, transparency logs for the tip-unbound
limitation, non-compensatory decision rules for the projection invariants,
provenance records for relation discipline, boundary objects for the
envelope contract. Each borrowing is named, its boundary is stated, and
the register's refusal to reach beyond those boundaries is the point. A
register that keeps books honestly is not a register that judges wisely,
and the scholarship section's task is to make that separation legible
rather than to collapse it.
