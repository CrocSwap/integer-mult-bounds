# No six-call diagonal sharing in the positive Dic3 alphabet

This contribution was produced by Nick Petalas. Apache-2.0.

A complete exact search excludes every word of at most six paid calls for
all **890** three-register diagonal targets whose separate positive-generator
bill is at least seven. In particular, all **360** targets with separate bill
seven have exact minimum **seven**. This is a finite certificate for the
specified formal operation model, not a complete multiplication theorem.
No new kappa or selected-frontier change is claimed.

This answers the explicit six-call Open next question of Cinna Davis's
[PR #2069](https://github.com/CrocSwap/integer-mult-bounds/pull/2069),
[retained package](../bit-dicyclic-diagonal-seed620ca/README.md).
Its depth-four/five exclusions and earlier state inventory remain credited
predecessor results. The new deliverable is the complete six-call join and
the exact seven-call endpoint family. No predecessor executable, state table,
receipt or unmerged source object is consumed by the new verifier.

## Complete operation model

Let

```
G = Dic3 = <u,v | u^6=1, v^2=u^3, vuv^-1=u^-1>.
A = F2[G].
```

Use exactly three arbitrary dirty registers. A paid call is

```
D_N(g) = I + ([g]+[1]) N,
g in {u,v}, N=x y^T, x,y in F2^3, y^T x=1.
```

All 28 binary rank-one idempotents are permitted, giving 56 operations.
Every call costs one. Only positive u and v are paid labels. Their inverses
are algebraic devices in the join, never additional available calls.
No free address maps, endpoint translations, copies, erasures, clean inputs
or extra registers are allowed. The full endpoint must be
`diag([a],[b],[c])` coefficient by coefficient in `M3(A)`.
Off-diagonal couplings must vanish. A dirty spectator is represented by an
identity target; its entrance is arbitrary and must return unchanged.

The result also holds if scalar GL3(F2) changes are free between calls.
They conjugate N to another permitted rank-one idempotent and can be moved
to one end. Augmentation `[g] -> 1` sends every paid factor and the diagonal
endpoint to I, so the net scalar factor must be I. This is the predecessor's
normalization argument, not a claim that arbitrary address changes are free.

Write group elements in order `u^i v^j`, indexed `i+6j`, with `0<=i<6`
and `0<=j<2`. The shortest positive distances in that order are

```
0,1,2,2,3,4,1,2,3,3,3,2.
```

For example, `diag([u^5],[u^2],[u])` has separate bill `4+2+1=7`
and exact minimum seven. A positive spelling of u^5 is `u u v v`.

## Why the finite search proves the result

Every group-algebra entry is its exact 12-bit coefficient vector. A matrix
has nine such entries. Hashes select buckets only; state equality compares
all nine coefficient vectors, so hash collisions cannot merge unequal states.

Construct S, the complete set of products of zero through three calls.
Breadth-first expansion uses every one of the 56 factors from each newly
reached state. The numbers of new states are `1,56,2352,92318`, giving
`|S|=94727`. Keeping one shortest representative preserves every continuation:
future multiplication depends only on its full matrix, and replacing a
prefix by a shorter representative cannot exceed the depth limit.
A separate raw three-loop check covers all `56^3=175616` ordered triples
and verifies membership in S. All one- and two-call products are checked too.
These checks support the completeness argument; the new mathematical question
is the six-call endpoint layer, not the predecessor's inventory count.

Every word of length at most six splits into P Q with both factors in S.
Each paid factor is invertible, with

```
D_N(g)^-1 = I + ([g^-1]+[1]) N.
```

The implementation retains P^-1 and checks `P P^-1=I` by literal formal
matrix multiplication for every stored state. For a diagonal target T,
`P Q=T` is equivalent to `Q=P^-1 T`. Column j of P^-1 is therefore
right-multiplied by its target monomial. The join examines every P and checks
exact membership of this required Q in S. No symmetry restriction, cut
relaxation, probabilistic equality or pruning predicate removes candidates.

The independent Python permutation model derives the distances and enumerates
the complete `12^3` endpoint domain. The distance-counting polynomial is
`1+2x+4x^2+4x^3+x^4`; its cube independently agrees with the endpoint histogram.
Exactly 890 targets have bill at least seven. Every one of their 94,727
prefix lookups is negative, for **84,307,030** lookups in total.

For bill exactly seven, the independent model executes all 360 coordinate
words. They give literal diagonal formal endpoints, touch no other register,
and require no cleanup. Their seven-call upper bounds and the exhaustive
six-call exclusion establish exact minimum seven. All 2,520 single-call
omissions change the required endpoint.

## Replay and evidence

Use CPython 3.12 and a C++17 compiler. The verifier has no Python dependencies,
Git dependency or network dependency. CXX may name a different compiler
executable. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dicyclic-six-call-boundary/verify.py --controls
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dicyclic-six-call-boundary/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dicyclic-six-call-boundary
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dicyclic-six-call-boundary --check-source-history
```

Substitute another CPython 3.12 path on another machine. Compilation and
execution use a temporary directory and leave no build products in the package.
Set TMPDIR to keep temporary files under a chosen scratch directory.
Successful direct replay prints `PASS_DICYCLIC_SIX_CALL_BOUNDARY` and a generated
JSON receipt binding every package file by SHA256. `--receipt PATH` saves that
receipt outside the package. It is never hand-written or required as an input.

Eight positive joins include all direct lengths zero through six and a
noncommuting heterogeneous target. Native controls compare fast updates and
inverse updates with literal matrix multiplication on all 3,136 gate pairs,
and check every retained inverse. Disposable native mutations remove a whole
inventory depth, destroy the join key, and corrupt the required endpoint.
Each must fail at its corresponding raw-coverage or positive-join check.
The Python model uses explicit permutations, rather than the native
normal-form multiplication formula, for distances and coordinate witnesses.

The complete source history, task card and predecessor README/TASK are
bibliographic provenance in SOURCES.json. No external scientific input is
required to execute the verifier. The source-bound selected-baseline metadata
orientation passed; it is not counted as a scientific replay.

## Scope, implementation limits and credit

This is a complete finite exclusion and exact finite endpoint family, not
an all-group or arbitrary-register no-sharing theorem. For targets with
separate bill eight through twelve, it supplies only the lower bound seven.
The cited #2069 result excludes earlier sharing layers; combined with it,
any first sharing word in this model has at least seven calls. That combined
statement retains #2069 as a premise and is not its independent revalidation.

Physical native realization, address/compiler routing, source ownership,
precision, stock, complete recursive costs and a multiplication theorem are
unresolved. No Lean, Docker or selected scientific replay was run. Independent
human and formal proof-kernel review are unclaimed.

The implementation uses no recursion. All mathematical loops have fixed
bounds of at most 12 group elements, 56 gates, three inventory depths, 178,809
raw words, 1,728 endpoints and 94,727 stored prefixes. Native functions remain
below 60 physical lines. Compiler diagnostics use warning-as-error settings.
Python exceptions keep scientific checks enabled under optimization.
Managed Python allocation and native unordered-map node allocation are explicit
fixed-allocation deviations: collection counts are bounded by those finite
limits, native matrices contain nine 12-bit masks, and the native state vector
reserves the complete raw-word capacity before expansion. Compiler/process
calls have 120-second timeouts and temporary resources have scoped cleanup.
No claim of adversarial compiler containment is made.

Credit Cinna Davis / 1337isnot1337 for #2069's group, alphabet, normalized
register model, earlier exclusions and explicit six-call question. Credit
David Govea / davidgovea #720, eumemic #288 and the retained scalar-idempotent
register-model lineage for the broader framework. Their original files and
credit lines are unchanged. The new search and exact seven-call family were
produced by Nick Petalas. Ordinary finite-group and meet-in-the-middle methods
are classical; no literature-priority claim is intended.

## Open next questions

- Does a seven-call word realize any target with separate bill at least eight?
  First price one concrete target and derive a structural restriction on its
  factor words. A depth-four inventory is substantially larger, and no such
  expansion was run or reserved here. The finite six-call exclusion does not
  settle that next layer.
- Can a uniform algebraic invariant replace the finite six-call join?
  Start with the exact seven-call example above and a named representation;
  the invariant must charge both positive labels and preserve arbitrary dirt.
  A nonfaithful represented endpoint alone cannot certify a construction.

These are mathematical side questions. Physical supplier development requires
a concrete native consumer and a complete paid budget before another
construction round. TASK.json records their relevance, first steps and blockers.
