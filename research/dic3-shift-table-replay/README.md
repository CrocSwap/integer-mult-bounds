# Prepared coefficient permutations for the complete Dic3 replay

This contribution was produced by Nick Petalas. Apache-2.0.

The complete retained PR2069 command takes **39.62% less median wall time
locally**, from 8.703675 s to 5.255297 s, by replacing repeated coefficient-bit
scans with a prepared table of 49,152 integers. The original search, endpoint
domain, raw-word controls, saved certificate and printed mathematical result
remain unchanged. This is an implementation-preservation proof with exact
finite conformance and local performance evidence. It supplies no new
mathematical endpoint, multiplication theorem or kappa.

Baseline range is 8.585230 to 9.105424 s; candidate range is 5.058666 to
5.884180 s. Five alternating fresh-process pairs ran on CPython 3.12.15,
macOS arm64. Every candidate beat every baseline. All ten commands succeeded
with empty stderr and identical complete output. Shared-host background load
was uncontrolled; the initial load averages were 2.80, 2.71, 2.03 on 18 CPUs.

The separate profile records 58,798,872 calls to the old shift function and
64,868,328 iterations of its bit scan. That function consumes 9.857 of 21.962
profiled seconds. Preparation uses 49,140 recurrence steps; every subsequent
shift is two tuple lookups. [MEASUREMENTS.json](MEASUREMENTS.json) contains all
ten complete fresh-process samples and their identical output hashes. Timing
includes process startup, source authentication, source execution, table
preparation, both complete searches, all original controls and output capture.

The benchmark compares the same authenticated driver with its single optional
replacement enabled or disabled. Both modes call the unchanged original
`main`. Each process starts with an empty original ring-product cache. The
profile is a separate run and is excluded from the reported samples.

## Preservation argument

Represent a coefficient of `F2[Dic3]` by a twelve-bit integer. For group element
g, right multiplication permutes its bits by `i -> i*g`. Let `T[g,m]` be that
permuted mask. Then

```text
T[g,0] = 0
T[g,m] = T[g,m xor b] xor (1 << ((index b)*g)), b = m & -m.
```

The smaller mask `m xor b` has already been prepared. Induction on m proves
that each table entry equals the original set-bit loop, including zero.
Right multiplication is a bijection, so no support bit disappears or changes
its multiplicity. All results are the same built-in Python integers.

The authenticated caller supplies only `0 <= m < 4096` and `0 <= g < 12`.
Its initial coefficients are zero or group basis bits; ring multiplication,
matrix multiplication and XOR preserve the mask range. Endpoint elements come
from `range(12)`. Thus direct table indexing covers every reached call. This
internal replacement is not a new public API for negative or oversized masks.

`replay.py` authenticates all three executable/data inputs before loading either
source. It executes their exact bytes, binds the original checker's `search`
import to that fresh module, and replaces only `right_monomial_shift`. The
original function is pure and has no cache or I/O effects. Every subsequent
operation therefore receives the same value and type. Dictionary insertion
order, shortest representatives, join lookups, endpoint ordering, rejection
controls and complete output are preserved. No result table substitutes for
a search. The checkout must remain stable while a command runs.

## Reproduce

From the repository root, CPython 3.12 and its standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dic3-shift-table-replay/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dic3-shift-table-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/dic3-shift-table-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dic3-shift-table-replay
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dic3-shift-table-replay --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. The complete replay
prints the unchanged `PASS_DIC3_BOUNDED_DIAGONAL_SEARCH` line. The conformance
command additionally prints `PASS_DIC3_SHIFT_TABLE_REPLAY` in a generated JSON
receipt bound to all package files. It checks all 49,152 coefficients against
both the old implementation and an independent normal-form formula, all
589,824 group-action compositions, and nine named rejection/distinction
controls. Changed or missing source files reject before source execution.
Correctness checks use explicit exceptions and remain active under `-O`.

To repeat the local timing experiment, use a fresh external output path:

```sh
python3.12 -I -W error -B research/dic3-shift-table-replay/benchmark.py --output /tmp/dic3-measurement-new.json
```

The benchmark performs five alternating baseline/candidate pairs, with a
120-second bound per complete command. It fails on any nonzero exit, stderr,
missing completion marker or changed complete output. Timing evidence is
local, and the registered replay imposes no portable speed threshold.

## Scope and credit

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The `replay-runtime` card is refined to one complete pinned
command; its source-binding first example passed. Live open/account PRs,
recent handoffs, active Discussions, merged searches and main object/formula
searches were checked. The cached overlap scan reports sparse local notes
and possibly stale remote coverage. Unpublished work and arbitrary historical
diffs remain outside that coverage. No same-command competing optimization was
found within it.

Cinna Davis / 1337isnot1337's [PR2069](https://github.com/CrocSwap/integer-mult-bounds/pull/2069)
retains the search, proof, certificate and original controls. David Govea's
PR720, eumemic's PR288 and the retained register-model lineage keep their
credit. Nick Petalas's older PR5205 concerns a different six-call mathematical
layer; it is neither extended nor replayed here. Finite lookup tables and
bit-permutation recurrences are classical. The new contribution is this
source-bound optional implementation, its preservation proof and complete
command measurements. No global algorithm-priority claim is made.

No predecessor source, frozen evidence, shared verifier or selected-frontier
file is changed. Native operations, physical callers, compiler, restoration,
precision/tape, stock and outer admission remain outside scope. Selected cold
replay, Lean and Docker are unrun. Independent human and formal proof-kernel
review are unclaimed. Successful execution of the retained checker is
conformance evidence, not a new audit deliverable or scientific acceptance.

## Code constraints

The new table has exactly twelve rows of 4,096 entries. Preparation has 49,140
iterations; coefficient comparison has 49,152 and composition comparison
589,824. The benchmark launches exactly ten serial children, each bounded by
120 seconds. Source inputs are three regular files of at most 65,536 bytes.
There is no recursion. New functions fit within 60 physical lines. The only
module replacement is temporary, process-local and restored in `finally`.
The installed callable owns an immutable table for that module's lifetime.
Warning-strict normal and optimized executions provide runtime diagnostics.

Power of Ten rule 3 has a CPython managed-allocation deviation for bounded
integers, tuples and original source objects. The additional prepared state
is 49,152 integer references plus tuple headers, with each value below 4096;
one row and twelve images are live during construction. Original search-state
and ring-cache limits are inherited unchanged from the finite command.
Rules 8 and 9 have a source-loading/dispatch deviation: exactly two pinned,
size-bounded Python modules execute through `compile`/`exec`, and one named
pure function is replaced. Authentication and the complete finite conformance
domain constrain these operations. A future native deployment requiring fixed
allocation or static dispatch would need a separate implementation. No such
deployment is supplied or implied here.

## Open next questions

Should a future default replay adopt this table? First define how immutable
historical source pins are retained while making the optimized command the
entry point. Adoption and its invalidation policy are not implemented here.
No further search layer or optimization is reserved.
