# Abstract

The Witness Register is a shared co-registration layer for the four-line set,
built as a sixth work standing beside the instruments rather than among them.
Each line already exports one common report envelope under the published schema
string `line.report-envelope/1.0` — a digest pointer to its complete native
report, its identity, subject, review date, registry provenance, native status
in its own vocabulary, and its non-claims. The register accepts those envelopes
by value, holds them beside one another without reading past their covers, and
records cross-line relations as separate authored records — non-compensatory
block, unresolved dependency, protected absence, directional tension,
unclassified observation, return due, cannot-compare, and agreement.

The register's defining properties are refusals, enforced in code: it never
imports a line package; it never parses, compares, ranks, averages, or merges
any line's `native_status`; it never auto-creates a category; it never infers
consent or permission; it never mutates or rewrites history; and it emits no
score other than one bounded posture, and that only on request. States are
sealed by a digest over their complete canonical content and chained by
`prior_ref`, so in-place tampering fails closed. On request, for one declared
next use, the register projects `-1 | 0 | +1` under non-compensatory
invariants: an unresolved block forces `-1`; a protected absence forbids `+1`
unconditionally; an empty register is `-1`, because nothing to witness is not
permission. Every projection carries the digest of the state that earned it
and the reasons it holds.

What the register does not do is as important as what it does. The tip is
unbound without an external anchor the chain does not control. Intake is a
shape check, never a truth check. Relations are authored by people, and a
missing relation is invisible to projection. The posture is not a decision,
not a utility, and not permission from any boundary owner. Three first-pass
measures — relation fidelity, return recoverability, premature crowning rate —
evaluate the register's own bookkeeping, never the truth of any report. The
register witnesses; it does not judge.
