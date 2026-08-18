# The Design {#sec:design}

## Non-sovereignty, stated first

The register's defining properties are refusals, enforced in code and
restated as non-claims in every module: it never imports a line package; it
never parses, compares, ranks, averages, or merges any line's
`native_status`; it never auto-creates a category; it never infers consent
or permission; it never mutates or rewrites history; and it emits no score
other than one bounded posture, and that only on request. Each line remains
the sole authority over its own vocabulary. The register witnesses; it does
not judge.

## The envelope contract

Intake is a shape check over the published `line.report-envelope/1.0`
payload: schema string exact, line identity non-blank, review date a real
ISO calendar date, registry digest and report pointer 64 lowercase hex,
snapshot references non-blank strings, and a non-empty set of non-claims —
an envelope without its instrument's boundary can quietly outgrow what the
instrument was allowed to say. `native_status` may be any JSON-compatible
value and is stored verbatim. Nothing is rejected silently: refusal returns
typed issues naming every defect. Accepting an envelope asserts nothing
about the truth of its report.

## Relations describe; they never replace

Cross-line structure lives in separate relation records over the envelopes'
report pointers: non-compensatory block, unresolved dependency, protected
absence, directional tension, unclassified observation, return due,
cannot-compare, and agreement. A relation keeps its surfaces apart — support
references and resistance references are distinct fields — so a conflict
survives as two sides rather than a summary. An empty `human_decision_ref`
means NOT_RECORDED, a first-class honest value, never a default verdict.

Inputs that fit no category are held raw, outside every alphabet, with a
stated reason. Promotion into the relation vocabulary requires a non-empty
human decision reference and yields a new relation that links back to the
original holding, which stays in history verbatim.

## Append-only, sealed, and returned to

States are sealed by a digest over their complete canonical content —
including record order — and chained by `prior_ref`. An update must carry
every prior record unchanged; the prior seal is re-derived from live content
first, so in-place tampering fails closed
(formalized in [the formal core](#sec:formalism); construction documented in [the method section](#sec:method)). Return contracts record what must
come back, from whom, under what trigger, and with what observable
acceptance condition; a completed return is a new record beside the open one
and closes only the verified part, the remainder keeping its trigger. The
review's 3×3 canonical witness cases ship as an executable battery whose
checks are themselves proven able to reject
(described in [the examples section](#sec:examples)).

![The worked two-state chain, built live from the four stored real envelopes at figure-build time: the genesis seal, the update's prior_ref pointing at it, verify_chain's verdict on the pair, and — run in the same build — the exact refusal update_state raises when one stored value is mutated after sealing. Chain integrity is internal consistency only; the tip is unbound without an anchor the chain does not control.](../output/figures/wr_chain.png){#fig:wr-chain width=100%}

## The posture that cannot travel alone

On request, for one declared next use, the register projects `-1 | 0 | +1`.
The invariants are non-compensatory and enforced in code, driven only by
relation records: an unresolved block forces `-1`; a protected absence
forbids `+1` unconditionally; an unmet return forbids `+1` until the return
condition is met or a referenced human decision rescopes; an empty register
is `-1`, because nothing to witness is not permission. The symbols are
interface values, not the ontology: every projection carries the digest of
the state that earned it and the reasons it holds, and a held `0` is a
structured enumeration, never a vague middle
(formalized in [the formal core](#sec:formalism)). Three first-pass measures —
relation fidelity, return recoverability, premature crowning rate — evaluate
the register's own bookkeeping, never the truth of any report.
