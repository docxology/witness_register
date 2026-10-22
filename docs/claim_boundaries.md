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
| **Sealed raw state** | A digest binds serialized records and order | Structural validity, truth or current tip |
| **Validated state / sound chain** | Local structure is valid; full-chain verification also binds genesis, stable register subject and actual append context | Anything about the world; anchor independence or freshness |
| **Classification decision** | A human reference names the category assigned to a held observation | Discharge of the resulting constraint |
| **Resolution / rescope event** | An authored authority claim names an exact immutable target, exact next use, evidence reference and prior basis state | Verified decision truth, permission, clearance for another use or clearance of protected absence |
| **Conflicting decisions** | Contradictory claims stay visible; a block retains `-1`, other holds retain `0` | A winner selected by tuple order; softening an unresolved block |
| **Reopened remainder** | Its verified closure no longer closes an ancestor for that exact use | Erasing verification history or closing another obligation |
| **Unchanged history** | Canonical record bytes preserve JSON type and numeric distinctions | Python equality as a substitute for byte preservation |
| **InvalidStateError** | Bookkeeping has named defects; no posture was issued | A substantive block against the subject |
| **Projection `+1`** | Nothing RECORDED forbids the declared next use, and at least one envelope exists | Endorsement, safety, quality, permission from any boundary owner |
| **Projection `0`** | The posture is held; `witness_hold_reasons` enumerates why, structured | A vague middle, an average, or a compromise between the lines |
| **Projection `-1`** | An unresolved non-compensatory block exists, or there is nothing to witness | Condemnation of the aim; a verdict on any line's report |
| **Binding fidelity / binding check** | Projection digest and state seal agree | Structural validity, semantic replay or truth |
| **Projection replay check** | Stored inputs reproduce the value and reasons | Correctness of authored records or decisions |
| **Chain coverage** | Preserved links and denominator, genesis coverage, full-chain validity and operator anchor reference are separate | Combined quality score, anchor independence or freshness |
| **Metric value** | A property of the REGISTER's bookkeeping | A property of any subject, report, or human decision |
| **Battery green** | The STATE/RELATION/RETURN cases held on the real functions, with a rejecting wrong variant per case | Exhaustive state-space proof or an injected defect in every predicate |

Boundary sentence for the whole work: **the register witnesses; it does not
judge.** Any sentence sourced from this repository that reads as a judgment
of a subject or an override of a line has left its claim class.
