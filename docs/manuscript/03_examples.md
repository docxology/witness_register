# Worked Examples {#sec:examples}

Historical worked examples exercise the register over stored exports: the
co-registration of different worked subjects, and the original
same-subject return contract. The original exports were generated on
2026-07-29; later admissions and dates are recorded separately in
`data/envelopes/README.md`. The examples are executed at test time —
`tests/test_worked_example.py` and `tests/test_same_subject.py` — not
described from memory.

## Different subjects: the co-registration

The stored worked envelopes describe *different* worked subjects — each line's
own shipped example — so the honest structure over them is an
incomparability relation and an open return contract naming what a
same-subject co-registration would require.

`tests/test_worked_example.py` intakes the stored collection unmodified, builds the
two-state chain, and measures: chain verification clean ([@prop:append-only]),
return recoverability $1.0$, relation fidelity $1.0$, and the posture for
treating the co-registration as a live subject record held at $0$ with both
records named in the reasons.

The held posture is the demonstration: real data, honest relations, and a
register that declines to crown them. The holding is not permission — it is
the same non-auto-category rule [@prop:no-auto-categories] states: an
observation that fits no current category is held raw, and holding caps the
projection at $0$.

The chain figure ([@fig:wr-chain]) retains the original four-export
construction, derived independently from its stored historical subset;
the battery figure ([@fig:wr-battery]) shows the 3×3 falsifiable checks.

## Same subject: the return contract

The return was then met the way the contract said it must be: four further
envelopes, each line's real evaluator run over ONE declared work —
witness_register 0.1.0 itself, with registrar-authored inputs whose
provenance is recorded beside the records.

The instruments answered in their own vocabularies: a declaration-coverage
`ALIGNED`, an honest `outside_scope` for the one action asked about, two
directional `TOWARD` readings with seven `NOT_OBSERVED`, and an absence
ledger naming the unobserved tip-anchor dependency and one `UNRESOLVED`
question.

Completing the contract lifts exactly the `return_due` hold and nothing
else — the incomparability relation still holds the first chain at $0$ —
and the same-subject state's own posture is also held at $0$, because the
honest reading of the ledger's open question enters as an unresolved
dependency. Three favorable readings and one open question is a held posture,
not a crown; `tests/test_same_subject.py` measures every sentence of this
paragraph.

The return contract demonstrates the register's core discipline: a
non-compensatory invariant ([@prop:non-compensatory]) means that one open
question prevents the posture from reaching $+1$, regardless of how many
favorable readings sit beside it. This is not a defect — it is the design.

## The 3×3 battery as evidence

The review's 3×3 canonical witness cases ship in
`src/witness_register/battery.py`, with acceptance tests in
`tests/test_battery.py`. The grid groups cases by STATE, RELATION and RETURN:

- STATE: `S1` holds missing input without automatic classification; `S2`
  preserves co-present support and resistance; `S3` retains protection.
- RELATION: `R4` blocks a route while preserving the aspiration; `R5` keeps
  a dependency unresolved despite agreement; `R6` keeps distinct named holds.
- RETURN: `T7` reopens stale naming without condemnation; `T8` closes only
  verified parts before full return; `T9` links promotion to its holding and
  human classification while preserving history.

The falsification pass changes one observation per case and confirms that
each case rejects its injected wrong variant. The plate is rendered from
`run_battery()`; the manuscript binding checks its case identifiers
([@fig:wr-battery]). Empty-register posture and tampered-seal controls live
elsewhere in the suite. A malformed seal produces structural refusal without
a posture; it is not a substantive $-1$ against the subject.

## What the examples do not establish

The historical collections do not establish freshness of their native
reports or a shared subject across later admissions. The same-subject
return contract uses the registrar as its own subject
— a deliberate self-application — and does not demonstrate the contract with
an external subject or a subject who declines to return. The battery
exercises nine constructed states; it does not enumerate the full state
space. These limits are developed in [@sec:limits].

## Released-snapshot transport cohort

The release cohort in `data/envelopes/releases/v0.2.0/` preserves the
worked envelopes from immutable sibling snapshots. Its manifest identifies
the actual tags or bounded-wait fallback commits and exported byte hashes.
`scripts/build_release_cohort.py` produces the state chain and projection;
`tests/test_release_cohort.py` replays them and plants custody defects.
The registrar records `CANNOT_COMPARE` and an open correspondence return:
the native worked subjects remain distinct. A successful intake verifies
the envelope shape, not its native report, consent, truth or applicability.
