# Independent finite-control and machine-model review

Reviewer: `/root/micro_model_review`, prepared for @CubeJerry with OpenAI
assistance. The reviewer did not modify the author's implementation. This
review is complementary to the separately assigned original-executor
operational trace review.

**Verdict: PASS for the scoped finite-control, clock and machine-model
proposition. The final proof was read and agrees with the construction.**

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Reviewed implementation: `research/scalar-table-microcontrol/lower.py`,
SHA256 `f378d44b7a208ac9b876549a28afe0b6905d74ba109194b83bd2e3becbe5b671`.
All six retained source files independently matched their declared byte
counts, SHA256 hashes and Git blob hashes; see `source-pins.json`.

## Universal model argument

The canonical machine specification permits a fixed finite alphabet, a
fixed finite number of one-dimensional tapes, and head movements of at
most one cell per step. It therefore permits stationary heads and a
serialization that acts on only one port in any transition. The generated
program uses exactly the supplied fixed P ports and the seven physical
symbols 0..6; it does not introduce a runtime scratch tape, growing decoder,
variable-sized integer, or runtime source-table search.

For a fixed admitted source table let B count branch rows, W write rows,
R right-move rows, L left-move rows, and J literal reject rows. Independent
inspection of the constructor gives the exact emitted state count

`N + 4 + 3P + 46B + 9W + 13R + 5L + J`.

The 46 states of a branch are one preliminary blank probe, seven binary
prefix-read states, fourteen post-bit forward steps, and twenty-four
value-specific rewind steps. Each source row owns one no-op dispatch
state. There are four shared terminal states, J literal rejection
terminals, and three states per final port rewind. Consequently the
emitted graph has at most `47N+3P+4`, and in particular satisfies the
author's looser `48N+3P+4` bound. These counts include unreachable graph
states; reachability pruning is not an assumption.

Every nonterminal graph state is one no-op, one physical read, one
physical write, or one unit movement. A read has seven explicit outgoing
targets. Other states have one fixed target. All targets lie in the
finite emitted state set, including original-row dispatches. Thus there
are no uncounted epsilon transitions. Program counters and decoder
prefixes are labels of finite control, rather than tape-resident
unbounded integers. Recursive Python calls used by `coded_read` have
fixed depth three during construction only.

An ordinary literal multitape transition relation is obtained by
enumerating every tuple in `{0,...,6}^P` at each nonterminal state. A read
selects a target by its one addressed symbol, a write changes only the
addressed symbol, a move changes only the addressed head, and a no-op
changes only control state. Inactive symbols and head positions are
preserved. This uses at most `S*7^P` transition entries for S states and
does not add target-machine steps, tapes, or alphabet symbols. N and P
must be fixed before the runtime inputs vary, and construction and this
potentially large literal expansion belong to the finite-template cost.
Fixed rejection labels and their metadata are also precompiled; this is
not a runtime claim to print arbitrary strings in zero time.

The selected serialization performs exactly one transition for every
raw read/write/unit-move action A in the original wrapper, and exactly one
no-op dispatch for every fetched source row U. Final successful rewinds
contribute to A and create no new source-row dispatches. A terminal state
has no outgoing transition; entering it does not incur an extra halt
step. Subject to the separate operational simulation proof, this gives
`C=A+U` for every terminating execution and the analogous aligned prefix
identity for a divergent execution. It does not imply that every closed
finite program terminates, that this serialization is optimal, or that
the project's model invoice equals this clock.

The target has the same mathematical tape contents and physical head
positions after corresponding actions. There are no additional moved-to
cells. Initial head cells must be included in the visited-region
convention; a literal full-P transition may inspect inactive head cells
even though the compact representation ignores them. It is inappropriate
to infer a different host backing-list allocation convention from the
mathematical identity. The author verifier initializes visited regions
with entry head positions, which is consistent with the required bound.

## Executed independent checks

`check_model.py` imports only the author's construction API. It does not
call `lower.check_program`, the author's simulator, or the author's
verification fixtures. It independently checks all emitted graph types,
targets, the exact dispatch partition, the seven-symbol physical
alphabet, permitted unit/stationary head movements, and expands compact
states into explicit full-P transition cases.

Commands:

```
python -B check_model.py /absolute/path/to/research/scalar-table-microcontrol
python -O -B check_model.py /absolute/path/to/research/scalar-table-microcontrol
```

Both runs pass and produce identical JSON. Coverage is 253 graphs,
11,666 state instances, and 1,226,848 literal simultaneous transition
instances, with P in 1..3. The maximal 101-branch fixture has 4,754 states,
exactly matching the independently derived expression. A 257-step closed
goto loop has zero physical actions and one dispatch per step, exercising
the nontermination qualification. Seventeen negative controls reject
broken graph targets/dispatch structure and source grammar violations,
including unclosed fallthroughs, invalid ports/directions, duplicate or
out-of-alphabet branch keys, booleans as integer literals, and malformed
terminal rows.

These finite checks are evidence for the implementation and failure
detection. The state-count and model construction above are the universal
argument. The checks do not by themselves establish semantic equivalence
to the original executor; the separately assigned operational review
must address malformed-code, blank-frontier, origin, and terminal
endpoints.

## Scope and novelty

The retained lifecycle proof already asserts a qualitative finite-control
expansion and an unspecified fixed control cost per instruction. The new
content is the explicit emitted graph, a numerical state bound, and an
exact clock for a named serialization. This does not lower the complete
Controller, stack/continuation mechanism, binary contexts, lifecycle
wrapper, or all native providers. It does not discharge the global
compiler or precision/tape assumptions and supplies no new kappa.

## Final prose and hash closure

The final `PROOF.md` was read in full. Its SHA256 is
`fa06bcf3660f871a972915a32942f20cc76187f449086d97e957a1bf83445b89`. It states the required fixed-template, local-origin, terminal-step, setup,
initial-head storage, nontermination, and tariff limitations. No blocking
model or proof defect remains. `FINAL-RECEIPT.json` pins the implementation,
proof, author verifier, source binding and result bytes reviewed. The lead
retains final packaging/README/PR wording and publication responsibility.
The separate operational review is needed for primitive equivalence; its
reported successful result is consistent with this complementary verdict.
