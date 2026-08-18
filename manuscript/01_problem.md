# The Problem {#sec:problem}

![The Witness Register cover plate: four vertical ledger columns with distinct greyscale hatch textures run in parallel without converging; a horizontal register band carries the title across all four; four seal circles mark the instruments below, and the witness mark sits above and alone. The cover uses only the register's greyscale palette — no colour that would affiliate it with any one instrument.](../output/figures/wr_cover.png){#fig:wr-cover width=100%}

Four independent instruments — the line works — each answer their own
substantive question about a subject in their own vocabulary, and each ends
in a status. A reader holding all four reports faces a temptation with a
long institutional history: collapse them into one number. Average the
verdicts, rank the instruments, let the loudest status become the state.

The 2026-07-29 design review of the collected line set ("The Space Between
the Lines", an external reviewer, with an analytic reader — unpublished
correspondence, answered in this repository's `docs/correspondence.md`)
names what that collapse destroys. A selected status is a SAFE PROJECTION of
a richer state, and the projection must not become the whole state: strong
support and strong resistance co-present are not the same as no evidence,
though both can project to the same cautious middle. A protected absence is
not missing evidence to be mined. A block that no other strength may buy
back disappears the moment scores are allowed to compensate one another.

The review's proposal is a missing layer, not a fifth verdict: a SHARED
WITNESS REGISTER that co-registers each line's report envelope, stores
cross-line relations as separate records, keeps history append-only, and
must never rank, average, merge, score, or override the lines. Its mottos:
*precedence without information destruction*; *no crown without return*.

This work is that register, built as a sixth work standing beside the set.
It is deliberately not a line. It has no colour, no substantive question of
its own, and no verdict. Each line already exports one common report
envelope under the published schema string `line.report-envelope/1.0` — a
digest pointer to its complete native report, its identity, subject, review
date, registry provenance, native status in its own vocabulary, and its
non-claims. The register accepts those envelopes by value — the schema
string is aligned across repositories by published convention, never by
import — and holds them beside one another without reading past their
covers.

\`\`\`{=latex}
\clearpage
\`\`\`

The paper proceeds as follows. [Section @sec:design](#sec:design) describes the register's architecture — the envelope contract, relations, chain, and projection. [Section @sec:method](#sec:method) documents how the register is built and operated. [Section @sec:formalism](#sec:formalism) states the instrument formally, from the definition of an envelope record (@def:envelope-record) through the projection invariants (@prop:non-compensatory). [Section @sec:scholarship](#sec:scholarship) situates the work in its intellectual lineage. [Section @sec:examples](#sec:examples) presents two worked examples — the co-registration of four instruments and the same-subject return contract — together with the 3×3 battery. [Section @sec:limits](#sec:limits) states the epistemic boundaries and non-claims, and [Section @sec:conclusion](#sec:conclusion) closes.

