# Method: How the register is built and operated {#sec:method}

The register is a standard-library Python package, and the design
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

1. Any non-compensatory block without an applicable explicit resolution forces `-1`.
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
`src/witness_register/battery.py`, tested by `tests/test_battery.py`.
Its STATE, RELATION and RETURN rows exercise missing/co-present/protected
records, categorical constraints, and return/promotion provenance.
Every case runs the real register functions. The falsification pass changes
one observation per case and confirms that the case rejects it, so a
green grid is evidence that its case-level checks can fail
([@fig:wr-battery]).

Three first-pass self-measures — relation fidelity, return recoverability,
and premature crowning rate — evaluate the register's own bookkeeping, never
the truth of any report. They are computed from the live chain and are
reported alongside the battery results; they carry no assertion about safety,
correctness, or completeness.

## Validation, interchange and review dates

Projection first validates local structure and the seal. Invalid bookkeeping
raises `InvalidStateError` with typed issues and emits no posture; `raw_state`
keeps refused imports available for inspection. Chain verification checks the
actual prior state of each new decision and obligation when context is present.
Native envelope subject spellings may differ: registration declares their
correspondence. The register-level subject stays stable across a chain.

Intake detaches native-status JSON from caller-owned containers. Arrays are
lists, object keys are strings, numbers are finite and strings have valid
Unicode. Tuples, non-string keys, surrogates and cycles are refused, never
coerced. Metadata reference lists also accept Python tuples as an explicitly
declared API convenience, canonicalized as JSON arrays. Bounded intake records
missing and malformed fields together in schema order; limits are defined in
`json_data.py` and exercised in `tests/test_interchange_hardening.py`.
Direct mutation of an accepted record remains a seal violation.

Review and anchor dates must be real calendar dates. Backdated reviews are
allowed: append sequence, recorded review date and operator-declared external
anchor date are separate facts, not an inferred chronology.
