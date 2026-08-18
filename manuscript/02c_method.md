# Method: How the register is built and operated {#sec:method}

The register is small — a few hundred lines of Python — and the design
section states what it does. This section states how it is built, how it is
operated, and how it is verified. The formalism ([@sec:formalism]) restates
the same machinery as objects and rules; this section describes the
construction.

## Building the chain

The register lives as a Python package — `witness_register` — with no
import dependencies on any line package. It never imports `black_line`,
`golden_line`, `red_line`, or `white_line`. Each line already exports one
common report envelope under the published schema string
`line.report-envelope/1.0` ([@def:envelope-record]), and the register
accepts those envelopes as JSON files stored by value under `data/envelopes/`.

Intake is a shape check over the published payload: the schema string must
be `line.report-envelope/1.0` exactly, the line identity must be non-blank,
the review date must be a real ISO calendar date, the registry digest and
report pointer must be 64 lowercase hexadecimal characters, snapshot
references must be non-blank strings, and the non-claims set must be
non-empty. `native_status` may be any JSON-compatible value and is stored
verbatim — the register never parses, compares, ranks, averages, or merges
it.

Nothing is rejected silently: refusal returns typed issues naming every
defect. A payload carrying `NaN` or `Infinity` is refused because a digest
over text that is not JSON would seal a non-interchangeable value.

Two states form a chain: a genesis state carries an empty `prior_ref`; every
other state carries the digest of the state it extends. The update function
re-derives the prior state's seal from its live content before extending it,
so a record mutated after sealing — even a value buried inside an opaque
`native_status` — raises rather than being carried forward. The chain is
append-only and fail-closed ([@prop:append-only]).

## Recording relations

Cross-line structure lives in separate relation records over the envelopes'
report pointers. Each relation names its type — non-compensatory block,
unresolved dependency, protected absence, directional tension, unclassified
observation, return due, cannot-compare, or agreement — and carries distinct
support and resistance reference fields, so a conflict survives as two sides
rather than a summary.

An empty `human_decision_ref` is the honest value `NOT_RECORDED`, never a
default verdict. Inputs that fit no current category are held raw, outside
every alphabet, with a stated reason. Promotion into the relation vocabulary
requires a non-empty human decision reference and yields a new relation that
links back to the original holding, which stays in history verbatim
([@prop:no-auto-categories]).

Return contracts are a special case: they record what must come back, from
whom, under what trigger, and with what observable acceptance condition. A
completed return is a new record beside the open one and closes only the
verified part, the remainder keeping its trigger.

## Computing the projection

On request, for one declared next use, the register projects `-1 | 0 | +1`.
A blank use raises — no posture is issued without a declared use. The zone is
computed from relation records only, in fixed precedence ([@def:projection]):

1. Any non-compensatory block with no recorded human decision forces `-1`.
2. An empty state is `-1`, because nothing to witness is not permission.
3. Any hold — a protected absence, an outstanding return, an unresolved
   tension, dependency, incomparability, or unreviewed observation, or an
   unreviewed unclassified holding — caps the value at `0`.
4. `+1` is reachable only when at least one envelope exists and nothing
   recorded forbids the use.

Every projection carries the digest of the state that earned it and at least
one reason. The symbols are interface values, not the ontology: a held `0`
is a structured enumeration, never a vague middle.

## The executable battery

The review's 3×3 canonical witness cases ship as an executable battery in
`tests/test_battery.py`. Each case is a constructed state and a
predicate the projection must satisfy: three positive cases (the register
should pass), three negative cases (it should hold), and three adversarial
cases (it should reject). Every case is run against the real projection
function at test time; the battery also includes a falsification pass that
plants deliberate errors and confirms the check would have failed, so a
green grid is evidence the checks can fail, not only that they passed
([@fig:wr-battery]).

Three first-pass self-measures — relation fidelity, return recoverability,
and premature crowning rate — evaluate the register's own bookkeeping, never
the truth of any report. They are computed from the live chain and are
reported alongside the battery results; they carry no assertion about safety,
correctness, or completeness.
