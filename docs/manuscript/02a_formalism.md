# The Formal Core {#sec:formalism}

The register's behaviour is small enough to state completely. Every
definition and proposition below is written from the module it describes and
bound to the running package by a named test in `tests/test_formalism.py`;
the numbers the reader sees are assigned by the render toolchain from
document order, and none is written in this source.

::: {.definition #def:envelope-record title="Envelope record"}
An accepted envelope is the frozen record
$e = (\mathrm{schema\_version},\ \mathrm{line\_id},\ \mathrm{subject\_id},\
\mathrm{review\_date},\ \mathrm{registry\_version},\
\mathrm{registry\_digest},\ \mathrm{native\_status},\ \mathrm{report\_ref},\
\mathrm{source\_snapshot\_refs},\ \mathrm{scope\_and\_nonclaims})$ with
exactly those ten fields, in order — the published
`line.report-envelope/1.0` shape, held verbatim. $\mathrm{native\_status}$
is opaque here: the register stores it and never parses, compares, ranks,
averages, or merges it. Intake accepts strict JSON only; a payload carrying
`NaN` or `Infinity` in its status is refused with a typed issue, because a
digest over text that is not JSON would seal a non-interchangeable value.
:::

::: {.definition #def:witness-state title="Witness state and chain"}
A witness state is the frozen record
$X = (\mathrm{subject\_id},\ \mathrm{review\_moment},\ \mathrm{envelopes},\
\mathrm{relations},\ \mathrm{unclassified},\ \mathrm{returns},\
\mathrm{prior\_ref},\ \mathrm{state\_digest})$ with exactly those eight
fields, sealed by $\mathrm{state\_digest} = \mathrm{SHA\text{-}256}$ over
the canonical JSON of every other field including record order. States form
a chain: a genesis state carries an empty $\mathrm{prior\_ref}$; every
every other state carries the digest of the state it extends and must contain
every prior envelope record (see [@def:envelope-record]) unchanged and in
place before any addition.
:::

::: {.proposition #prop:append-only title="Append-only, fail-closed"}
The update function re-derives the prior witness state's (see
[@def:witness-state]) seal from its live content before extending it, so a
record mutated after sealing — even a value buried inside an opaque
`native_status` — raises rather than being carried forward; `verify_chain` applies the same checks to a stored chain after the
fact and never repairs anything; and `seal_tip` refuses to hand out an
anchor digest for content that no longer matches its seal. Projection
applies the identical re-derivation, so no posture is ever stamped onto
rewritten history.
:::

::: {.definition #def:projection title="Projection and zone"}
For a witness state $X$ (see [@def:witness-state]) and a declared next use
$u$ (blank $u$ raises: no posture without a declared use), the projection is
$P(X, u) \in \{-1, 0, +1\}$, always carrying the digest of the exact state
that earned it and at least one reason. The zone is computed from relation
records only, in fixed precedence: any non-compensatory block with no
recorded human decision forces $-1$; an empty state is $-1$, because
nothing to witness is not permission; any hold — a protected absence, an
outstanding return, an unresolved tension, dependency, incomparability, or
unreviewed observation, or an unreviewed unclassified holding — caps the
value at $0$; and $+1$ is reachable only when at least one envelope record (see
[@def:envelope-record]) exists and nothing recorded forbids the use.
Non-compensatory means the same thing here that [@prop:non-compensatory]
states: a single block forces $-1$ under any volume of agreement, and no
decision reference lifts it.
:::

::: {.proposition #prop:non-compensatory title="Non-compensatory means non-compensatory"}
No volume of recorded agreement buys back a blocked route in the projection
(see [@def:projection]), a protected boundary, or an unmet return: a single
unresolved block forces $-1$ under any number of agreement relations; a
protected absence caps the posture at $0$ past every decision reference,
including the one offered at projection time; and a return contract with no
verified return — or a verified return with a named remainder — holds the
posture until the return condition is met or a human decision explicitly
rescopes it, and a whitespace-only verification is refused at construction
rather than counted as met.
:::

![The projection zone measured: each row is one constructed state and the value project() actually returned in this build, with a human decision reference offered at projection time so the rows also show what a decision argument does not lift — it never resolves a block and never lifts a protected absence. A non-compensatory block forces -1 alone and under fifty AGREES relations alike; an empty register is -1, not permission; every hold row is 0 with its reason; +1 appears only where an envelope exists and nothing recorded forbids the use.](../../output/figures/wr_zone.png){#fig:wr-zone width=100%}


::: {.proposition #prop:no-auto-categories title="No auto-categories, no manufactured decisions"}
An observation that fits no current category is held raw, outside every
alphabet, and holding is not permission: an unreviewed holding caps the
projection (see [@def:projection]) at $0$. Promotion into the relation
vocabulary requires a non-empty human decision reference — blank and
whitespace-only references are refused — and the promoted relation links
back to the held record, which is never rewritten.
:::

## The worked co-registration

The repository carries four real envelopes under `data/envelopes/`, one per
line, each generated by running that line's own public API in its own
repository on 2026-07-29 and stored by value with a provenance record. They
describe four *different* worked subjects — each line's own shipped example
— so the honest structure over them is an incomparability relation and an
open return contract naming what a same-subject co-registration would
require. `tests/test_worked_example.py` intakes all four unmodified, builds
the two-state chain, and measures: chain verification clean
([@prop:append-only]), return
recoverability $1.0$, relation fidelity $1.0$, and the posture for treating
the co-registration as a live subject record held at $0$ with both records
named in the reasons. The held posture is the demonstration: real data,
honest relations, and a register that declines to crown them. The holding
is not permission — it is the same non-auto-category rule
[@prop:no-auto-categories] states: an observation that fits no current
category is held raw, and holding caps the projection at $0$.

The return was then met the way the contract said it must be: four further
envelopes, each line's real evaluator run over ONE declared work —
witness_register 0.1.0 itself, with registrar-authored inputs whose
provenance is recorded beside the records. The instruments answered in
their own vocabularies: a declaration-coverage `ALIGNED`, an honest
`outside_scope` for the one action asked about, two directional `TOWARD`
readings with seven `NOT_OBSERVED`, and an absence ledger naming the
unobserved tip-anchor dependency and one `UNRESOLVED` question. Completing
the contract lifts exactly the `return_due` hold and nothing else — the
incomparability relation still holds the first chain at $0$ — and the
same-subject state's own posture is also held at $0$, because the honest
reading of the ledger's open question enters as an unresolved dependency.
Three favorable readings and one open question is a held posture, not a
crown; `tests/test_same_subject.py` measures every sentence of this
paragraph.

![The design review's 3×3 canonical witness cases as the shipped battery, run at figure-build time: every check passed on the real register, and — measured in the same build — every case raised BatteryError when its observed behaviour was deliberately falsified, so a green grid is evidence the checks can fail, not only that they passed.](../../output/figures/wr_battery.png){#fig:wr-battery width=100%}
