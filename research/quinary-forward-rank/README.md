# Faster complete characteristic-five disjointness replay

An optional forward-echelon evaluator reduces the median time of the complete
composed PR5221 scientific replay by **33.75%** on the recorded host. Both
scientific command bodies execute in full, with identical combined stdout,
every reached rank call and the original typed receipt retained. This is a
scoped implementation-equivalence proof and a measured runtime improvement.
The characteristic-five repair theorem remains Brian / JoyboyBrian's result.
No new mathematical repair rank, supplier or kappa is claimed.

This contribution was produced by Nick Petalas. Apache-2.0.

## Change and execution boundary

The primary verifier in [PR5221](https://github.com/CrocSwap/integer-mult-bounds/pull/5221)
computes reduced row echelon form and returns only its rank. The new evaluator
normalizes each pivot and eliminates rows below it, updating only the remaining
row suffix. Eliminating above each pivot is unnecessary for the returned rank.

`adapter.py` authenticates all six declared source inputs before compiling any
source. In adapted mode it renames exactly one source definition from `rank`
to `frozen_rank` and supplies `forward_rank` under the original name. The
entire remainder of the primary source, including its `__main__` block, is
unchanged. The independent command is compiled and executed without edits.
Compilation uses authenticated source text directly, without importing source
bytecode. The frozen predecessor files are never modified.

The complete composed consumer runs the primary body and independent body
sequentially in one fresh Python process. The same wrapper, authentication,
compilation, imports, fixture construction, output capture and checking are
inside both timed modes. Original mode executes the original rank definition.
Adapted mode uses the new evaluator. This measures the complete scientific
consumer, including the independent check. It does not measure the shared
package runner, CI planning, or the sum of two separately started interpreters.

The two unchanged output lines are:

```text
PASS_QUINARY_RESONANT_DISJOINTNESS_REPAIR
PASS_INDEPENDENT_QUINARY_TENSOR_AND_KERNEL
```

The combined output SHA256 is
`e2c64edfb1e54f877f32e061452239b97cd8493be02017bdafc156e901f2d0a8`.
The original typed `RESULT.json` remains checked by both source bodies.
All five Jordan rules, both literal source fixtures, endpoint witnesses,
domain controls, direct-binomial powers, similarity and kernel census remain.
Their mathematical claims retain predecessor credit and are not new results
of this package.

## Equivalence proof

The new function accepts rectangular integer matrices with at most 256 rows
and columns and entries of at most 64 bits, over F5. Empty matrices and
zero-column matrices have rank zero. Every reached source argument lies in
this domain. The function copies and reduces the entries before any update.

At the start of column c, let r be the number of selected pivots. The remaining
rows have zero entries in every column before c. This invariant holds initially.
If the column has no pivot among those rows, it is zero there; advancing c
preserves the invariant. Otherwise swap a nonzero pivot to row r, multiply
that row by its inverse and eliminate its column from all rows below it.
These are invertible row operations over F5. The earlier entries of all
affected rows are zero, so updating only the suffix gives exactly the same
row operation as updating the whole row. The invariant follows for the next
column and r increases by one.

The selected pivot rows are linearly independent, with distinct leading
columns. At termination every remaining row is zero, or every row has a pivot.
Thus the matrix rank is exactly r. Clearing entries above a pivot changes no
rank and is unnecessary for this conclusion. Both evaluators consequently
return the mathematical rank on the stated domain. Neither modifies its input.
Since no other source code consumes the intermediate echelon matrix, replacing
the rank return value preserves every downstream scientific check.

## Evidence

`verify.py` compares both complete output strings and observes every reached
adapted call. All **28** calls agree with the original evaluator, and each
input remains unchanged. The largest reached matrix is 254 by 254. A separate
oracle using one-entry and two-by-two minors checks every one of the **15,625**
two-by-three matrices over F5. Their rank histogram is `[1,744,14880]`.
There are another **89** boundary/rectangular cases, including negative
entries, row swaps, zero dimensions and the 256-dimensional identity.
Eleven rejection controls cover invalid fields, shapes, types and capacities,
changed source bytes and a missing rewrite anchor. Explicit guards survive
optimized Python. Each run generates a receipt from actual checks and the
SHA256 of all seven package files and six source inputs; no receipt is
handwritten or committed.

An untimed cProfile run of the original primary reports 0.209 seconds in its
28 rank calls out of 0.242 seconds total. Profiling is excluded from timings.
The largest exact row reduction is the measured limiter. Keeping forward
elimination and the unchanged construction and independent work explains why
the whole consumer is not twice as fast.

After adding a bounded source-file read, the five final pairs below alternate
original then adapted, each in a fresh process.
Times include full source authentication and both scientific bodies. The
host is CPython 3.12.15, macOS 27.0.1 arm64, 18 logical CPUs. Load averages
were `(4.34,3.94,3.06)` before measurement and
`(2.1128,3.5083,3.1260)` after the final measurement. Other processes were
present; no claim of an idle host is made. There were zero command failures
or output disagreements.

| Pair | Original seconds | Adapted seconds |
| --- | ---: | ---: |
| 1 | 0.288796625 | 0.190406375 |
| 2 | 0.283317125 | 0.187691209 |
| 3 | 0.282368625 | 0.185105083 |
| 4 | 0.282861833 | 0.184945250 |
| 5 | 0.285454292 | 0.194998125 |

Medians are **0.283317125** and **0.187691209** seconds. Ranges are
`[0.282368625,0.288796625]` and `[0.184945250,0.194998125]` seconds.
The median reduction is 33.75%; the ranges are disjoint. This is local
evidence for this complete fixed consumer, not a portable performance guarantee
or a faster multiplication algorithm. Optimization stopped at this first
verified improvement.

## Reproduction

From the repository root, with the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/quinary-forward-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/quinary-forward-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/quinary-forward-rank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/quinary-forward-rank --check-source-history
```

Expected markers are `PASS_QUINARY_FORWARD_RANK`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Any CPython 3.12 path can replace the local interpreter path. The direct
verifier also works in a Git-free export with its declared inputs.

To repeat measurements, create an external directory, choose a fresh output
filename, and use:

```sh
python3.12 -W error -B research/quinary-forward-rank/benchmark.py --rounds 5 --output /absolute/external/directory/measurements.json
```

The benchmark requires five to fifteen alternating pairs, checks exact
stdout/stderr and status, bounds every child at thirty seconds, removes its
private bytecode namespace and writes measurements exclusively outside the
checkout. Direct `adapter.py --mode original` and `--mode adapted` execute
the corresponding complete composed consumer without the conformance oracle.

## Scope and implementation constraints

This is an optional isolated adapter. Default adoption and historical pin
migration are not implemented. General coefficient fields, unbounded matrix
sizes, rounded arithmetic and intermediate echelon outputs are outside its
interface. The scientific predecessor law and complete multiplication theorem
are not independently reviewed here. Native maps, a physical caller, ownership,
restoration, routing, precision/tape, stock, compiler and outer admission remain
separate. Lean, Docker, heavy native builds and the selected scientific cold
replay were not run. No selected record or predecessor file changes.
Independent human and formal proof-kernel review are unclaimed.

All new functions are under sixty lines, with bounded matrix, fixture, file and
process domains. There is no recursion or persistent cache. CPython's managed
allocation is a Power-of-Ten rule 3 deviation; the evaluator holds at most
256 by 256 entries plus one row suffix, with bounded input integer sizes.
Sources are at most one MiB each. Rule 8/9 deviations are authenticated source
compilation and the two named evaluator callbacks used by conformance. Their
targets and source hashes are fixed; all source and output checks propagate
failures. Standard-library internals allocate and dispatch dynamically.
The inherited source's fixed loops and containers remain unchanged and are
not exposed to user-selected dimensions. Warning-strict normal and optimized
registered checks provide recurring Python diagnostics.

The first five pairs before that boundary guard also had zero errors and
identical output, with medians 0.288851667 and 0.192588875 seconds and disjoint
ranges. The final run above measures the published implementation.

## Provenance

Scientific base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8, selected PR6030. The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362961)
states this exact runtime scope. `TASK.json` retains the original runtime card
and refinement. `SOURCES.json` pins every live source at the base. Live open
and account PRs, handoffs and active Discussions, current-main README searches,
merged/general-form searches and the cached card scan supplied overlap
coverage. Sparse notes, arbitrary historical diffs and unpublished work are
not exhaustively covered. PR6135 concerns DisjointTensor DAG serialization,
a different compiler and consumer; this is not its follow-up.

## Open next questions

Can the evaluator be adopted in the default consumer while preserving
historical source pins? First specify the migration and retain both complete
scientific bodies and the typed receipt. Default integration is the remaining
blocker. No further optimization is reserved.

## Credit

Credit Brian / JoyboyBrian's PR5221 for the entire law, primary and independent
consumer, typed receipt, controls and source structure. Retain Ali Romman
PR4962, Nick Petalas PR5173, mikey1201 PR172, icekylinx PR144 and the complete
tensor/deletion lineage. Gaussian elimination is classical. The new contribution
is the source-bound implementation step, equivalence argument and measured
complete-consumer evidence.
