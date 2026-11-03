# Exact nonlinear recovery with a limited binary-cycle message

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: finite certificate with a scoped combinatorial proof.
Independent human and formal proof-kernel review are unclaimed.

Five receivers each demand one independent uniform bit and observe the
two original neighboring bits on a five-cycle. One encoder sees all five
bits and broadcasts one of at most M message values. Arbitrary nonlinear
encoders and decoders have the following sharp joint-success counts:

| Message values M | 1 | 2 | 3 | 4 | 5 | 6 | 7 | >=8 |
|---|---|---|---|---|---|---|---|---|
| Successful inputs out of 32 | 5 | 10 | 15 | 20 | 24 | 28 | 31 | 32 |

In particular, two fixed message bits have exact optimal success
probability 5/8. A seven-value message can fail on just one input, but
cannot recover all inputs. Independent public or private randomness
does not improve these uniform-input joint-success probabilities.

[PROOF.md](PROOF.md) reduces the problem to disjoint correct message
classes, proves the upper bounds from complete finite premises and
lists attaining classes. The verifier constructs literal encoders and
all receiver lookup tables, then executes them on every input.

## What this adds

ywz65's [PR2541](https://github.com/CrocSwap/integer-mult-bounds/pull/2541)
uses C5 to obstruct a linear paired-plane query interface. Tekalign's
[PR3362](https://github.com/CrocSwap/integer-mult-bounds/pull/3362) and
JoyboyBrian's [PR5023](https://github.com/CrocSwap/integer-mult-bounds/pull/5023)
give exact unequal-width linear query capacities. Their results are
cited context, not replay or audit targets.

The new step changes both linearity and complete recovery: it computes
the entire finite partial-success curve under arbitrary nonlinear
encoding. Nick Petalas's PR5873 concerns exact linear fits with total
payload seven; this result neither extends its orbit classification
nor changes only its payload widths. The five bits here have unit width.

Confusion graphs, the binary five-cycle maximum guessing fixed-set size five, and the
zero-error eight-message endpoint are classical. The proof cites Atkins,
Rombach and Skerman and Ong for that context. No literature priority for
those endpoints or methods is claimed. New credit is for this complete
partial-success table, its attainers and its repository certificate.
The retained Sagar Thakrar, Cinna Davis, Adam Gall and P112/query-mask
lineage remains credited in the predecessor packages.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nonlinear-cycle-success/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nonlinear-cycle-success/independent.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nonlinear-cycle-success
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nonlinear-cycle-success --check-source-history
```

Local CPython 3.12.15 normal/optimized primary checks took 1.043/0.977
seconds; the separate checks took 0.051/0.050 seconds. All passed.
These are check durations, not a performance improvement claim.

A reviewer may substitute their CPython 3.12 executable. VERIFY.json
registers both normal and optimized warning-strict runs of both checks.
Expected markers are PASS_NONLINEAR_CYCLE_SUCCESS,
PASS_NONLINEAR_CYCLE_TRUTH_TABLES and PASS_REGISTERED_RESEARCH_PACKAGE.

The complete nonconfusable class inventory has sizes
(1,32,256,640,480,32,0) for class sizes 0 through 6. The primary search
visits 3,249 size-five partial packings, obtains all 1,600 four-packs and
tests 25,280 complementary four-class pairs. Its separate truth-table
implementation obtains the same full inventory and uses a different
pair-union obstruction. All eight attaining protocols execute on all
32 inputs; eight malformed-witness/decoder controls reject.

The inventory digest is
`a39ed8349b302d38efbdacb422c394044ec1c2042364c21f4d01ddda1a555c73`.
The primary command generates a receipt bound to all seven package
files and all three cited live inputs. It writes nothing. Redirect
stdout outside the checkout to retain a receipt. No handwritten result
receipt is included, and no predecessor scientific verifier is run.

## Scope and remaining obligations

The complex-rank-shape-decoder card changes to a finite interface side
result. This is an exact benchmark for a changed decoder hypothesis,
without a complete paid-moment improvement. The selected source-binding
positive control passed; the selected record and frontier are unchanged.

The result fixes five unit binary payloads, one simultaneous common
message, the two original neighbor observations and joint success.
It proves no direct-product, adaptive-observation, input-correlated
side-information or general nonlinear native theorem. Physical reads,
the nonlinear encoding operations, dirty restoration, ownership,
frames, stock, precision, tapes, compiler and outer recovery are not
priced or implemented. No physical supplier, new kappa or complete
multiplication theorem is claimed. Lean, Docker and selected cold
supplier replay are outside this contribution.

Canonical base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority
revision 8. [TASK.json](TASK.json) preserves the card, changed scope and
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375558).
SOURCES.json pins the exact predecessor README bytes. Live claims,
open and merged PR bodies and the main-tree README corpus were searched
for nonlinear cycles, partial/joint success and the exact object.
The final cached overlap covered 581 open PRs and 6,655 Discussion records with
reported complete pagination, but only 132 of 8,917 local notes in the
sparse checkout. Separate main-tree searches supplement those notes;
arbitrary diffs, unindexed literature and unpublished work remain limits.

## Implementation bounds

Every search concerns at most 32 inputs, subsets through size six,
32 size-five classes or 480 size-four classes. All functions fit within
60 physical lines. There is no recursion, dynamic code, network access,
external solver or third-party runtime dependency. Explicit exceptions
retain every scientific check under optimization. Source and package
files are bounded below one MiB; the declared source list has five rows.
Both registered modes treat Python warnings as errors. No external
static analyzer or independent proof kernel is claimed.

Power of Ten rule 3 deviation: CPython dynamically allocates integers,
tuples and bounded sets during these one-shot enumerations. Static
allocation is unavailable in this runtime. The fixed 32-input domain
bounds all live collections, including at most 114,960 four-class pairs
and 1,600 four-pack unions. The separate enumerations and optimized
replays check those capacities and the complete finite domain. A native
steady-operation implementation would require fixed-capacity storage
before removing this deviation.

## Open next questions

1. Can a legal source-owned physical query layer realize the two-bit
   5/8-success witness with a useful complete bill? First specify all
   original observations, arbitrary dirty fields and the whole encoder/
   receiver operator. Nonlinear native operations, restoration and a
   compatible complete caller remain blockers.
2. What is the exact joint-success tradeoff for two copies with coupled
   encoding? First form the 1,024-input confusion graph for one named
   message budget. The present one-copy packing certificate gives no
   direct-product theorem; coupled confusability is a separate obstacle.

Research stops at this first verified finite result.
