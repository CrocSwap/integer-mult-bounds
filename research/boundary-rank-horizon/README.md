# Sharp boundary-rank horizon for complete finite-memory endpoints

This contribution was produced by Nick Petalas. Apache-2.0.

A complete fixed transfer representation needs positive-width tests only through

```
H = max(1, D-r-b+2),
r = rank of the positive seed rows {F T_s}, b = rank B.
```

Here every endpoint is `F T_w B`, D is the transfer dimension, and r,b are
nonzero. If either rank is zero, every positive-width endpoint is zero.
The bound is sharp for every admissible triple D,r,b over every field.
For D=8,r=2,b=3, a one-symbol cyclic example first fails at width five;
the earlier seed-rank-only horizon is seven.

Claim type: scoped written mathematical proof with exact finite corroboration.
No new kappa, selected-frontier change or complete multiplication theorem is
claimed. The new step observes that all passing reachable rows lie in the
actual right-boundary kernel of dimension D-b, rather than the whole transfer
space. [PROOF.md](PROOF.md) gives the quantified argument and sharp examples.

## Interface and predecessor

This is an independently posed refinement of the complete physical-column
interface in [zxv's PR5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441),
head `11fedb46fa199283f78282187c10aea432d8b0bb`. Its retained
[proof](../finite-memory-lifting/PROOF.md) supplies the earlier D-r+1 horizon,
fixed-table semantics, positive-width convention and complete dirty returns.
Those results are credited premises, not audit or replay targets. No predecessor
checker is imported or executed, and no existing package is changed.

The alphabet may contain every physical input/output column pair. Every word
must be tested, rather than only repeated identical columns. Every original
and returned role must remain in the residual. A reference can be subtracted
by direct sum as in the predecessor; ranks belong to that complete residual.
The matrices and boundaries must stay fixed across widths.

The exact horizon improves by b-1 widths until it reaches one. This is an
interface reduction, not a measured runtime speedup. It does not reduce table
extraction cost, transition dimension or the number of words at a given width.
No actual selected provider/consumer table is extracted here. Numerical
tolerance, physical realization, paid/native/tape/stock/precision costs,
compiler and analytic recovery remain separate. All five selected framework
assumptions remain. Independent human and formal proof-kernel review are
unclaimed. The selected cold replay, Lean, Docker and predecessor suites were
not run.

## Exact finite evidence

The standalone checker enumerates every binary one-symbol transition table
in dimensions 1,2,3 and every ordered two-symbol table in dimensions 1,2.
For each table it uses every row subspace for F and every column subspace
for B. Choosing canonical bases retains all zero/nonzero endpoint questions
and the two ranks, including arbitrary rectangular or dependent boundaries.
These are 137,896 normalized contracts, not a count of all literal boundary
matrices. The oracle visits 288,662 endpoint blocks, retaining duplicate word
paths and stopping at the first nonzero block. When no discrepancy appears,
it checks every word through D+1; histogram key zero means only this finite
observation, rather than a separate classification of zero-family root causes.
The continuum and arbitrary-field conclusions come from the written proof.

Seed ranks use row-XOR elimination. The literal endpoint oracle instead uses
column dot products and enumerates the word tree without reachability pruning.
The five census domains contain respectively 8, 400, 131,072, 16 and 6,400
contracts. All 650 triples with 1<=D<=12 and 1<=r,b<=D attain the predicted
first width. Their zero/one cyclic construction also has the all-field proof.

Nine invalid rank/dimension inputs reject. Five semantic controls cover a
one-too-small horizon, a mixed-word discrepancy missed by repeated-symbol
testing, a discrepancy in a returned-role block, the false pass after dropping
that block, and zero transfer dimension. Explicit exceptions retain all checks
under optimization. No predecessor scientific numbers are recounted.

The generated [RESULT.json](RESULT.json) binds all six scientific/package
source files by SHA256. Default execution compares the complete typed receipt
and writes nothing. `--emit /absolute/new/path.json` exclusively creates a new
generated receipt. The result file is excluded from its own source-hash list.

## Reproduce

From the repository root with CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/boundary-rank-horizon/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/boundary-rank-horizon/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/boundary-rank-horizon
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/boundary-rank-horizon --check-source-history
```

Another CPython 3.12 path may replace the displayed local interpreter.
Expected markers are `PASS_BOUNDARY_RANK_HORIZON`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The shared runner also authenticates the historical catalogue and source
provenance in [SOURCES.json](SOURCES.json). The direct scientific verifier
needs only this package, with no Git, network or predecessor runtime input.
Each registered command has a 120-second limit.

## Open next questions

Can one actual complete provider/consumer residual exhibit b>1 and a useful
horizon reduction after every return is included? Extract its fixed table,
compute the positive seed and right-boundary ranks, and compare the horizons.
Physical table extraction and complete supplier costs remain blockers. This
question is unclaimed; no further construction search follows from this result.

## Scope, credit and engineering

The `formal-interface-lemma` card changes to a written exact-interface proof,
rather than a selected-caller formalization. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030.
The current selected-baseline command passed its binding-only orientation.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375593)
records the independently posed question and live overlap limits. Source
sharing is limited to the credited physical model, not the separately claimed
uniform-approximation question. Main and live searches did not find this
rank-sensitive horizon; unpublished work and arbitrary historical diffs remain
unknown. Discovery stopped at the first proved step.

Credit zxv / PR5441 for the physical table and earlier positive seed-rank
criterion, with its retained independent/inverse-register, native, compiler
and source-adapter lineage. Weighted-automata reachability and rank-nullity are
classical. Kiefer and coauthors, Tzeng, Crosswhite and Bacon retain the
foundational credit recorded in that proof. No general literature-priority
claim is made.

Build the Lever shaped the standalone checker. Prove It Works and Test Behavior,
Not Implementation shaped the literal first-discrepancy oracle and returned-role
control. Foundational Thinking led to binary row/column subspaces as the finite
contract representation. The Investigation playbook kept predecessor results as
premises and separated the all-field proof from finite observations.

Power-of-Ten inspection found no recursion, dynamic code generation or mutable
shared state. All functions fit below sixty physical lines. The census fixes
D<=3, at most two symbols, at most sixteen subspaces and 512 individual matrices.
The two-symbol census has D<=2. Its word trees and the mixed-word control have
at most sixteen paths at one level. Sharpness fixtures fix D<=12 and one symbol.
All scientific loops are bounded by those finite domains. The CLI accepts no
external matrix and only an optional output path.

Rule 3 has a managed-runtime deviation. CPython allocates collections and
integers during replay; the fixed dimensions and binary coefficients bound live
data. The largest transition list has 512 matrices, and the receipt contains
only bounded aggregates. Extending the fixed census domains requires reviewing
those capacities. Warning-strict normal and optimized execution supplies the
available interpreter diagnostics. No external static analyzer is required.
