# Claim boundaries

What each kind of statement from this repository is allowed to mean. The
table follows the sibling works' convention: a claim class, what it DOES
assert, and what it must never be read as asserting.

| Claim class | Asserts | Never asserts |
| --- | --- | --- |
| **Accepted envelope** (`EnvelopeRecord`) | The payload had the published `line.report-envelope/1.0` shape at intake | That the referenced report is true, complete, current, or wise; anything about `native_status` beyond "stored verbatim" |
| **Intake refusal** (`IntakeIssue`) | The payload failed a named shape rule at a named field | That the exporting line erred substantively; that its report is wrong |
| **Relation record** | Someone described these envelopes as standing in this typed relation, with this bounded description | Any correction, override, or re-scoring of a line's own status; that the relation is exhaustive |
| **`human_decision_ref` empty** | No human decision is on file (NOT_RECORDED) | A default verdict in either direction |
| **Return contract, open** | An obligation of return is recorded: why held, what could change it, who has standing, what stays protected | That the material is bad, or that fulfilment will yield approval |
| **Return contract, completed** | The verified part — and only it — came back; the remainder keeps its trigger | That the whole obligation is discharged when `open_remainder` is non-empty |
| **Unclassified holding** | A raw observation is held outside every category, with a stated reason | Any classification, however provisional; permission to act on it |
| **Sealed state / sound chain** | The stored records are internally consistent, ordered, and unmutated since sealing | Anything about the world; that the tip is current (the tip is unbound without external anchoring) |
| **Projection `+1`** | Nothing RECORDED forbids the declared next use, and at least one envelope exists | Endorsement, safety, quality, permission from any boundary owner |
| **Projection `0`** | The posture is held; `witness_hold_reasons` enumerates why, structured | A vague middle, an average, or a compromise between the lines |
| **Projection `-1`** | An unresolved non-compensatory block exists, or there is nothing to witness | Condemnation of the aim; a verdict on any line's report |
| **Metric value** | A property of the REGISTER's bookkeeping (fidelity, recoverability, crowning rate) | A property of any subject, report, or human decision |
| **Battery green** | The nine required behaviors held on the real functions this run | That the register is correct beyond the behaviors the cases encode |

Boundary sentence for the whole work: **the register witnesses; it does not
judge.** Any sentence sourced from this repository that reads as a judgment
of a subject or an override of a line has left its claim class.
