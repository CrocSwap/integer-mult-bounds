# The P104 lifetime threshold depends on its history alphabet

Adding one complete monotone history moves the first rejecting lifetime floor
from **423 to 436** in the stated endpoint/cut/ideal-idle relaxation. This is a
cost-screen result, not a correction circuit, lifetime lower bound or supplier.
The selected conditional kappa remains unchanged.

[Sudarsh Chaturvedi's PR2924](https://github.com/CrocSwap/integer-mult-bounds/pull/2924),
head `d1660ed0a17b66ad0c86cd4aaea724926134e362`, correctly restricts its 423
threshold to the histories `(1,7,1)` and `(1,1,1,1,1,1,1,1,1)`. This successor
changes that restriction. It does not identify an error in PR2924 or claim that
its author extended the result beyond those two histories.

## Exact result

Write `C`, `U` and `M` for integer multiplicities of these rank-step histories:

| Name | Rank steps | Visited dimensions |
| --- | --- | --- |
| Cheap, C | 1,7,1 | 0,1,8,9 |
| Unit, U | 1,1,1,1,1,1,1,1,1 | 0,1,2,3,4,5,6,7,8,9 |
| Merged, M | 1,1,2,1,1,1,1,1 | 0,1,2,4,5,6,7,8,9 |

The new history replaces two consecutive rank-one steps by one rank-two step.
Every lifetime still pays nine rank units. Both U and M visit dimensions
1,2,7,8, so their proper-arrival dimension and post-source departure
codimension remain seven. Their separate endpoint hyperplane capacities and
the credited demand-saturated allocation curve are therefore unchanged.
This statement concerns separate endpoint constraints, not compatible joint flags.

At the selected complex primitive saving
`a = 67018507072324140917 / 40000000000000000000000`, keep 232 cheap histories
and replace `n` of PR2924's 191 unit histories by the merged history:

| C | U | M | Certified optimistic moment, decimal approximation |
| --- | --- | --- | --- |
| 232 | 191 | 0 | 1.000003548402828 |
| 232 | 181 | 10 | 1.000000083777248 |
| 232 | 180 | 11 | 0.999999737314690 |
| 232 | 0 | 191 | 0.999937374054245 |

**Eleven replacements are necessary and sufficient within this fixed-count
one-parameter family.** The exact outward intervals are in [RESULT.json](RESULT.json).
No floating-point value determines a sign or acceptance decision.

The eleven-replacement profile has
`3235 H1 + 69 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 240 H7 + 8 H8`.
Its local rank mass is 6,175 and its optimistic idle rank mass is 537.
The seven cut capacities are
`[12456,12104,12104,12456,12456,12456,12456]`, against the credited demands
`[4656,4656,4672,4680,4672,4656,4656]`.
Both endpoint dimension totals are 1,569, above 832. Both endpoint allocation
curves require at least 219 cheap helpers at 191 wide endpoint histories;
the profile has 232. All 192 members of this fixed-count family pass those
necessary constraints.

Optimizing over the entire three-history alphabet, with lifetime count at least
L and at most 482, gives:

| Floor L | Cheapest C,U,M | Optimistic moment, decimal approximation |
| --- | --- | --- |
| 423 | 232,0,191 | 0.999937374054245 |
| 435 | 245,0,190 | 0.999999349571449 |
| 436 | 246,0,190 | 1.000004768716193 |

Thus 436, not 423, is the first rejecting floor **for this enlarged alphabet
and this relaxation**. Neither number is an all-history or all-P104 barrier.

## Proof and inherited premises

The contract remains the frozen X-only, ZERO-to-FULL monotone relay model.
There are no new original-helper reads, target feedback or nonmonotone paths.
Initial segments of any ordered nine-vector basis realize these dimension
histories as nested frames. This does not bind them to actual source/target
frames. The merged history loses the dimension-three contact, which may matter
to source acquisition. A dimension history is not a chronological correction
program.

The new work uses PR2675's seven coupled cut inequalities and PR2920's separate
endpoint curve as pinned premises. It does not independently reprove their
original P104 geometry or the network-to-inequality implications. It reconstructs
the endpoint curve from all six endpoint types in both orientations, checks
all history-dependent quantities and reproduces PR2924's baseline moment
**exactly**, including both rational enclosure endpoints.

For a crossing from dimensions p to q at cut k, `p <= k < q`, the credited
capacity is zero if p=0 or q=9, otherwise `2^(7-q+p)`. The cheap history has
capacity one at each cut. The merged history has capacities
`[64,32,32,64,64,64,64]`. This proves the displayed fixed-family cut totals.
The first departure from a source line is still to dimension two; the last
proper arrival before a target hyperplane is still from dimension seven.
Consequently all existing endpoint dimension, support and separate allocation
rows used here survive the replacement. No simultaneous source/target
endpoint realization follows.

The whole original channel invoice is retained. At m=73, 832 families, nine
stages and centre charge 56, the total rank mass is 6,712. A lifetime contributes
nine local units, leaving `4344 - 9*(C+U+M)` idle units. The optimistic bill puts
that idle mass into fractional rank-51 children, as in PR2675/2920/2924.
At a>0, `cost(2) < 2*cost(1)`, so each U-to-M replacement strictly lowers the
moment without changing idle mass. The certified signs at n=10 and n=11
therefore prove the minimal replacement count.

For the full three-history minimum, replace all U by M. For each wide-helper
count K from zero through 482, the least feasible cheap count is the inherited
endpoint curve, or `L-K` if larger. Every feasible such all-merged profile
passes the seven cuts and endpoint dimension/count rows. The minimum cut
capacity over the endpoint-feasible minimal profiles is 6,248, above every
forced cut demand. Additional cheap helpers only improve those constraints.
Thus replacing U by M is feasible throughout this optimization domain.
The extra-helper prices are strictly positive, so only the least cheap count
at each K needs checking. Exact interval comparisons certify unique minima
at L=423,435,436. A passing profile at 435 and exclusion at 436, together with
nested floor constraints, establish the first rejecting floor.

## Independent arithmetic and reproduction

Standard-library Python 3.12 or later, no network or solver:

```sh
python3.12 -B scripts/research_package.py --package research/p104-three-history-threshold
python3.12 -I -O -B research/p104-three-history-threshold/verify.py
python3.12 -B research/p104-three-history-threshold/test_verify.py
```

The primary intervals reuse Douglas Colkitt's authenticated logarithm/exponential
engine. [independent.py](independent.py) instead encloses
`(r/73) * (1-z)^(-a)`, where `z=1-r/73`, by the positive binomial series.
Successive term ratios are `z*(a+k)/(k+1) <= z` for 0<a<1. Integer floor/ceiling
recurrences at denominator 2^128 enclose every term; the first omitted upper
term divided by `1-z` bounds the tail. A 4,096-term limit fails closed.
Both implementations certify every reported sign and overlap before decimal
outward rounding. The independent implementation does not import the primary
engine, use logarithms or use floating point.

Controls check exact rational-power oracles, an independent endpoint-allocation
DP, independent optimization including nonminimal cheap counts, invalid
histories/counts, insufficient endpoint and cut capacity, a changed endpoint
signature, duplicate keys, isolated optimized Git-free execution, source
corruption before engine import and complete receipt corruption. Source bytes
and the retained PR2924 result are authenticated before use. The full selected
cold replay is not required or claimed for this scoped successor.

## Family decision and limits

Finish this audit and stop. The result identifies a concrete hypothesis change
that a lifetime-floor argument must account for. It does not justify a new
construction campaign or infer a favorable *complete* bill.

Proved here: history arithmetic, the stated finite screen optima, independent
moment sign certificates and the eleven-replacement minimum. Inherited: original
channel correctness, binary endpoint geometry, cut implications and the
separate endpoint relaxation. Unknown: compatible joint flags, chronological
source acquisition, scalar coefficients, arbitrary dirty restoration, native
lowering, actual idle children, owners/routing, precision/tape, consumer and
all-size admission. Unknown costs are not zero. Passing an optimistic lower
cost screen is not a constructive upper bound on a supplier's cost.

Power of Ten inspection covers the new Python files only. All loops have
finite input-derived bounds: 482 lifetimes, nine dimensions, seven cuts, 104
endpoints, 4,096 binomial terms, 128-bit rational saving arguments and bounded
source JSON. The interpreter and
JSON decoder allocate dynamically, a managed-runtime deviation bounded by these
sizes. The independent cache holds at most 16 child intervals. The fixed primary
engine retains its existing recursive logarithm and convergence loops; it is
unchanged, its rank arguments here are at most 73, and the independent bounded
binomial checker guards all reported decisions. Dynamic imports are limited
to two explicit local files. Warning-as-error compilation, lint and optimized
execution are the local diagnostics. There is no physical-memory admission.

## Open next questions

Can the third history participate in an actual joint flag/dependency assignment
within the available cost margin? First bind its dimension-two departure and
dimension-seven arrival to actual source/target endpoint pairs. Reject an
incompatible assignment before scalar synthesis. Compatible acquisition,
restoration and the complete consumer/physical cost ledger remain blockers.
A further numeric threshold search alone does not close them.

## Credit and provenance

Sudarsh Chaturvedi/PR2924 supplies the audited two-history threshold. Credit Nick
Petalas/PR2920/2909/2896 for endpoint geometry and saturation; Arham Tahir/PR2675/2682
for the coupled profile budget; Hiroki Kumazaki/PR2889/2353 for endpoint spans and
the relay model; ywz65/PR2614; Sagar Thakrar's mixer handoff; Philippe Van Velzen's
relay and cost contract; and Douglas Colkitt's interval engine. Retain the Rohan
Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/PR1071,
Ali Romman/PR1125 and native/compiler/geometry lineage credited by those sources.
The PR2924 result is copied unchanged with its exact head, blob and SHA256.
Other predecessors remain live pinned inputs, not copied source packages.

Task p104-side-correction, refined to a changed-history cost-screen audit.
Scientific base `914cd73f563acaaa682d733a9fbfcc07272336a3`, priority revision 5.
[Task, freshness and verification limits](TASK.json), [source pins](SOURCES.json),
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18973831).
Evidence is locally checked; no independent human or proof-assistant review is
claimed. Apache-2.0.
