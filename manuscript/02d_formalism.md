# Further propositions: chain, return, and deterministic projection {#sec:further-formalism}

The three propositions below extend the formal core of [@sec:formalism].
Each states a property of the running code; each is verified by the test
named in the binding table that follows.

::: {.proposition #prop:chain-verification-completeness title="Chain verification completeness"}
When a witness chain is constructed from observed events by successive
calls to `update_state` (see [@def:witness-state]), every event in the
chain is verifiable against the register's evidential record: no event
can enter a chain without a corresponding register entry, and
`verify_chain` checks every state's digest ([@prop:append-only]),
linkage (`prior_ref`), and record preservation for envelopes,
relations, unclassified holdings, and return contracts. A state that
dropped, reordered, or altered any prior record fails verification with
a message naming the violation; verification never repairs.
:::

::: {.proposition #prop:return-contract-constraint title="Return contract enforcement across chains"}
When the same subject appears in multiple chains, the return-contract
projection constrains the relationship between those chains. For a
subject $S$ appearing in chains $A$ and $B$, the projection ([@def:projection])
applies the same rules: any `RETURN_DUE` relation with no recorded
human decision forbids $+1$ until the return condition is met. A
contract recorded in one chain does not automatically bind another, but
within a single state the projection respects every open return
recorded there, and meeting a contract requires a verified return
record ([@prop:non-compensatory]) — a partial return with a non-empty
remainder does not close the obligation. Return contracts are records
of obligation, not promises of approval: the honest outcome of a return
may be that the material stays held.
:::

::: {.proposition #prop:projection-determinism title="Projection determinism"}
Given the identical witness register state $X$ (see [@def:witness-state])
and the identical declared next use $u$, `project(X, u)` produces the
identical `Projection` value — same `value`, `state_ref`, and
`reasons` — every time. The projection function is a pure computation
over the state's sealed content: it re-derives the state's digest from
live content before projecting ([@prop:append-only]), checks for
unresolved blocks, empty state, and holds in a fixed precedence
([@def:projection]), and returns a deterministic result. The digests
are deterministic in their own right; the projection carries the
digest of the exact state that earned it. Determinism is a property of
the code path; it does not make the underlying records true or the
posture warranted.
:::

## Formalism-to-test bindings

Every proposition above is verified by named tests in the package's suite;
the table below binds each result to the test that would fail if the code
stopped satisfying it. Each row is keyed on the block's *label*, not on its
number, and the label renders as the number the reader sees.

Two binding tests police the table.
`tests/test_formalism_bindings.py::test_binding_tables_bind_every_declared_block`
fails if the set of row labels stops matching the set of labels declared in
this section, and
`tests/test_formalism_bindings.py::test_every_binding_row_names_an_existing_test`
fails per row if any row's verifying-test cell names no test or names one
that does not exist. Neither checks that a named test is a *good* test, only
that every declared block is bound to one that exists. The boundary column
restates what each result does *not* claim.

| Proposition | Statement essence | Verifying test | Boundary |
| --- | --- | --- | --- |
| [@prop:chain-verification-completeness] | every event in a chain is verifiable against the register's evidential record; verification never repairs | `tests/test_formalism_bindings.py::test_chain_verification_checks_every_state` | chain internal consistency, never truth of events |
| [@prop:return-contract-constraint] | same-subject return contracts constrain the projection; partial returns do not close the obligation | `tests/test_formalism_bindings.py::test_return_contract_constrains_projection_across_chains` | records of obligation, never promises of approval |
| [@prop:projection-determinism] | identical state and use produce identical projection; deterministic code path | `tests/test_formalism_bindings.py::test_projection_is_deterministic_for_identical_inputs` | determinism of the code path, not truth of records |

The bindings are themselves code behaviour: they show which claims the suite
would catch, not that the register's posture is wise or well grounded.
