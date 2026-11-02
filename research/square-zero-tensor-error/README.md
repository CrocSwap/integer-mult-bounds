# Exact tensor error for square-zero borders

This contribution is produced by Nick Petalas. Apache-2.0.

Claim type: scoped proof with exact finite corroboration. No new kappa.

For a unitary target `D` and relative error `N^2=0`, put
`C(e)=D(I+eN)` and `a=|e| ||N||`. The exact Euclidean error of every
ordinary tensor power, in both forward and inverse-transpose orientations,
is the norm of an explicit matrix of size `k+1`:

```text
F_k(a) = || B_k(a) ||
B[i,j] = a^(j-i) sqrt(binomial(j,i) binomial(k-i,j-i)), i<j
B[i,j] = 0, i>=j

lim_(a->0+) F_k(a)/a = sqrt(floor((k+1)^2/4)).
```

The reduction holds for every finite original dimension and every rank of
`N`. A rational weighted-coordinate version avoids all square roots in the
verifier. For `0<delta<=1`, the necessary condition
`|e| ||N|| sqrt(floor((k+1)^2/4)) <= delta` and sufficient choice
`|e| ||N|| <= delta/(2k)` give dyadic parameter budgets at most two bits
apart. The tensor count therefore requires an additional `log2(k)+O(1)`
parameter bits, rather than a fixed parameter choice. The exact finite
spectral formula, global bounds and all-k proof are in [PROOF.md](PROOF.md).

## Connection to the open problem

Dillon Amburgey's [PR4623](https://github.com/CrocSwap/integer-mult-bounds/pull/4623)
asks for a global complex approximation and recursive precision contract.
This result isolates its completed-endpoint question under a relative
square-zero hypothesis. The card scope is explicitly changed in
[TASK.json](TASK.json). The predecessor's circuit, budgets and finite
approximation lemma are cited premises, not audit deliverables.

Ordinary tensor powers do not establish chronological supplier substitution.
Applying this theorem to a recursive caller requires its actual owner map
and a proof of the relative square-zero hypothesis. Singular wrappers,
intermediate magnitudes, paid-call errors, restoration, physical storage and
movement remain unpriced here. General polynomial borders are outside the
theorem. The selected frontier is unchanged; no complete multiplication
theorem or independent human or proof-kernel acceptance is claimed.

The classical ingredients are singular-value decomposition, Boolean-lattice
symmetry and the positive-matrix eigenvector theorem. The contribution is
their exact square-zero tensor-error consequence and the sharp precision
screen, with no claim of literature priority for those ingredients.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/square-zero-tensor-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/square-zero-tensor-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/square-zero-tensor-error
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/square-zero-tensor-error --check-source-history
```

A reviewer may substitute another CPython 3.12 executable. Expected markers
are `PASS_SQUARE_ZERO_TENSOR_ERROR`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Default replay writes no files. The optional
`--receipt NEW_EXTERNAL_PATH` exclusively creates a generated receipt bound
to the package file hashes and recomputed finite result. No receipt is
handwritten or committed.

The finite verifier compares 21,840 literal tensor entries with a separately
written subset formula, 6,144 compressed action/Gram entries and 21,840
inverse-transpose entries. It also enumerates 2,080 first-order level terms,
192 exact precision choices and a 256-entry mixed rank-two tensor similarity.
Eleven controls cover a changed compression coefficient, missing identity
subtraction, invalid domains and false exact linearization. The all-k and
all-dimension claims rest on the written proof, not these finite counts.

Both commands have 60-second caps. Actual timings, environment and integrity
checks are recorded in [VALIDATION.md](VALIDATION.md). No selected supplier,
predecessor scientific replay, Lean or Docker suite is required or claimed.

## Bounded implementation

The verifier uses no recursion, dynamic evaluation, background work or third
party dependencies. Literal tensors have at most 64 rows in the registered
checks. Helpers enforce a 256-row capacity; the coefficient/precision loop
has 64 tensor counts. Functions stay below 60 physical lines. Preconditions
and scientific checks use explicit exceptions and remain active under `-O`.
Receipt output is restricted to an external path and refuses overwrites.

Power of Ten rule 3 has a managed-runtime deviation in `verify.py`.
CPython integers, fractions and lists allocate dynamically during these
finite exact checks, so allocation cannot be confined to initialization.
The scope is this offline verifier only. Fixed tensor/count domains and
matrix capacities bound live objects and integer expression sizes; normal
and optimized replay verify the controls. There is no persistent service or
unbounded input stream. A native fixed-storage implementation would be the
follow-up only if this checker were put on a constrained execution path.

Python has no compiler warning flags. Warning-strict execution and in-memory
syntax compilation are the applicable diagnostics here. This package changes
no shared CI or repository analysis configuration.

## Sources and overlap

[SOURCES.json](SOURCES.json) pins the original card, selected record and
PR4623 context at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
Those files are provenance; no predecessor implementation is imported.
Credit Dillon Amburgey, Cinna Davis, Jacob Alan Sussman, zxv and the retained
native, compiler, caller and precision lineage.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360690)
records the scope. Live PRs, recent handoffs, active Discussions, merged topic
searches and tracked main README terms were checked. The remote overlap
cache reported complete pagination; its sparse local corpus covered 102 of
8,917 note records. Missing local notes are not evidence of novelty.
Unpublished work and arbitrary historical diffs remain coverage limits.

PR4828 and PR4829 give sharp component shear/port conditioning constants.
They do not compute the error of tensoring a completed shear and subtracting
identity. PR5021 prices errors inserted at ordered paid-call boundaries,
whereas this theorem concerns completed matrix endpoints.

## Open next questions

1. Can an actual legally flattened caller meet the relative square-zero
   hypothesis? First provide its source-bound owner map and prove the
   relative error squares to zero. Chronological compatibility and restored
   independent productive outputs are the blockers to applying this result.
2. Can this endpoint choice fit one complete intermediate-error and wrapper
   budget? First bind actual subword norms and additive paid-call errors,
   then apply one global finite-circuit budget. The physical caller, scalar
   wrappers and numerical oracle contract are absent here.
