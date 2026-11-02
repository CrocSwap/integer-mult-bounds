# Exact Fibonacci lane requirement of the Gray layout

This scoped written proof with exact finite corroboration was produced by
Nick Petalas. The n-bit reflected Gray address map

    g_n(x) = x XOR (x >> 1),       0 <= x < 2^n,

and its inverse need exactly **F_(n+1) stable lanes in one pass**, where
F_0=0, F_1=1. For n=16 the exact requirement is 1,597 lanes. A matching
increasing-chain assignment attains the bound for arbitrary record payloads.
Any sequence of stable-lane passes must have capacity product at least
F_(n+1). No optimal multi-pass depth or new kappa is claimed.

The address map is a product of n-1 adjacent binary shears for n>=1. Its
small algebraic factor count therefore does not imply a small one-pass lane
requirement. This is an abstract layout cost, with no selected-caller
occurrence or complete physical implementation asserted.

## Proof and exact boundary

Input records have distinct IDs 0,...,2^n-1 in that order. One pass splits
them into T streams and interleaves those streams into the output. Each
stream preserves input order, and every record moves exactly once. The output
order is g_n(0),...,g_n(2^n-1). Placing record x at position g_n(x) instead
gives the inverse order and the same lane requirement.

[PROOF.md](PROOF.md) derives the exact recurrences

    L_n = L_(n-1) + D_(n-1),     D_n = max(L_(n-1), D_(n-1)),
    L_0 = D_0 = 1,

for longest increasing and decreasing subsequences. Thus L_n=F_(n+2) and
D_n=F_(n+1). Coloring records by decreasing-subsequence depth gives exactly
D_n increasing streams and a literal attaining split/merge. Lane-choice
tuples across multiple passes prove the product lower bound.

The reflection formula, Fibonacci numbers, patience sorting and general
chain-coloring argument are classical tools. The contribution is their exact
Gray-layout lane consequence and its independently reproducible certificate
under this explicit interface; no global historical-priority claim is made.

## Evidence and reproduction

From the repository root, with CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gray-layout-lane-number/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gray-layout-lane-number/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gray-layout-lane-number
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gray-layout-lane-number --check-source-history
```

Other machines may substitute their CPython 3.12 path. The verifier checks
both orders for n=0,...,16, producing attaining lanes and a matching decreasing
witness. It literally splits and merges all 262,142 records in these 34
cases. Independent quadratic subsequence DP covers 22 cases through n=10;
an exhaustive increasing-subset partition oracle covers eight cases through
n=3. Seven adjacent-shear compositions check the tuple-color product bound.
Boundary and semantic controls reject malformed permutations, unstable lane
maps and false witnesses, and distinguish increasing length and fixed XOR
layouts from the claimed Gray quantity.

The expected status is `PASS_GRAY_LAYOUT_LANE_NUMBER`. Stdout is a generated
receipt with actual enumerated counts and SHA256 of all six package files.
No receipt is hand-written. Default verification writes nothing and also
works in a Git-free export. Both registered checks retain explicit guards
under optimization. Universal quantifiers rest on the written proof, not on
these finite computations.

## Scope, sources and credit

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The `uniform-transfer-audit` card changes to this original layout side result;
no selected framework assumption is discharged. The selected source-binding
orientation passed. [TASK.json](TASK.json) records the scope change and
[SOURCES.json](SOURCES.json) pins exact provenance. No predecessor executable
or scientific receipt is imported or replayed.

Credit Matarener's [PR3825](https://github.com/CrocSwap/integer-mult-bounds/pull/3825)
for distinguishing linear address algebra from stable-pass layout costs,
and James Reed's [PR3839](https://github.com/CrocSwap/integer-mult-bounds/pull/3839)
for permutation-composition context. Nick Petalas's older PR4858 counts XOR
subsequences and PR5148 constructs reversal passes. Those different endpoints
are context, not claimed again here. Their retained native/Walsh/compiler and
coverage predecessors keep their credit. New material is Apache-2.0.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361586)
precedes the proof package. Live open PRs, recent account work, handoff claims,
active Discussions, cached overlap and distinctive all-main/merged searches
were checked. Sparse notes, non-atomic snapshots, arbitrary historical diffs
and unpublished work remain coverage limits. No exhaustive novelty claim
follows from those searches.

No actual caller, physical lane allocation, merge controller, head movement,
reversible scratch cleanup, native invoice, compiler, precision or analytic
recovery is supplied. More tapes, random access or another routing model may
escape this stable-lane bound. No selected cold replay, Lean proof, native
suite, supplier admission or complete multiplication theorem was run or
claimed. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Determine optimal fixed-capacity multi-pass depth for this same Gray layout.
  Start with exact two-lane factorizations at small dimensions and compare the
  necessary Fibonacci product bound. The one-pass coloring does not supply a
  factorization attaining that bound.
- Bind an actual native producer/consumer to this layout and price the full
  split assignment, merge control, storage, head movement and restored state.
  A caller occurrence and physical stream implementation are missing, so the
  abstract lane count cannot yet alter a supplier invoice.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Verifier constraints

The verifier is nonrecursive and accepts no external mathematical input.
Arrays have at most 2^16 records. Quadratic DP is capped at 1,024 records;
the partition oracle has at most 256 states and 256 candidate subsets per
state. Composition checks have at most eight passes, and the registered
shear fixtures have at most 256 records. Witness reconstruction performs
exactly its declared number of predecessor steps. Functions are under 60
physical lines. Explicit contracts stay enabled under optimization.

Power of Ten rule 3 has a bounded managed-runtime deviation. Python allocates
integers, tuples and queues during this terminating verifier; it is not a
fixed-allocation runtime. Record, pass, oracle and one-MiB file-read caps bound
live collections. Rule 9 permits only the standard-library sort callback
for indexing a local position table; its target and table lifetime are fixed.
Warning-strict normal/optimized replay and in-memory source compilation supply
the available interpreter diagnostics. No repository analyzer configuration
or shared build setting is changed.
