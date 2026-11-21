# Weighted 2-adic subset certificates for P104 decoders

Status: an elementary paper deduction plus exact finite checks. No Lean build,
no proof for every decoder, no network or word wall, and no kappa improvement.
The pattern and instance are from PR #7852 head
`41beda1d6435760dc99e38bd7e65f36798aad212`, using the 2-adic gaugeable-subset
criterion in #7855 head `3a12128490d09cd2070678b989c647169c81c255`.
The exact data files, the first-round proof, and the related #7869 DEN4 note
are archived under [sources](sources/). See [SOURCES.json](SOURCES.json) for
path, blob, license and author mappings.

## A valid row-budget inequality

For a fixed rational decoder, write `D_k,G_k` for the actual nonzero supports
of row `k`, and `c_k = rank_F2 Q[D_k,G_k]`. Thus its full paid mass is
`C = sum_k c_k`. Let `S_1,...,S_m` be port subsets, each individually
gaugeable in the #7855 sense, allowing a *different* integer row gauge for
each subset. Define

```
r_ik = rank_F2 Q[D_k intersect S_i, G_k intersect S_i].
```

If nonnegative rational weights `lambda_i` satisfy every full-support
row budget

```
sum_i lambda_i r_ik <= c_k                 for every k,
```

then `C >= sum_i lambda_i |S_i|`. This is a sufficient condition; it is not
claimed necessary. Each separately gaugeable set has `|S_i| <= sum_k r_ik`
by the 2-adic reduction, even when other sets require incompatible gauges.
Multiply by its weight, sum over sets and apply the displayed inequality for
each row once. The allowed weights do not intrinsically have to be at most
one; a separate per-port constraint can be imposed if desired.

One support-independent sufficient condition is available: if the `S_i` are
pairwise disjoint, `Q[S_i,S_j]=0` for all distinct `i,j`, and `0 <= lambda_i
<= 1`, then every row budget follows automatically. Indeed the submatrix on
the union of these sets is block diagonal, so the sum of its block ranks is
at most the full rectangle's rank. More generally, the same reasoning works
row by row when only the actual cross-block rectangles for that row vanish.
This condition is sufficient, not necessary; the strict-improvement example
below uses direct rank checks instead.

This result is **factorization-specific**. The gauges and rank budgets must
be established for the actual decoder. Nothing here shows they exist for an
arbitrary P104 decoder in a putative sub-56 counterexample. Computing all full
row ranks also directly reveals its cost, so a certificate for a known decoder
is not by itself a universal lower bound.

### Relation to the later #7869 DEN4 note

DreamingOfClouds, with Claude Opus 5.5 via Claude Code, gives a deep-port
lemma and more general carry-polynomial rank bounds in [DEN4](sources/7869/den4.md)
at #7869 head `06c207a9feb3994a4b987dc3010657b6e85b7956`, sections 3 and 4.
Its single-gauge deep-port bound covers the #7855 single-subset result after
normalization: in a valid decoder, each port has `alpha+beta <= 0`, and a
#7855-gaugeable port has equality. Choose a common integer shift `c` and a
sufficiently large `e` so that all `w_k=2^(e+c) W_k` and
`v_k=2^(-c) U_k` are 2-integral in that chosen row gauge. The scaled decoder
has diagonal `2^e`; every selected port is deep in the DEN4 sense, though
other ports can also be deep. The bounded comparison
found no separately gauged weighted row-budget combination in those sections;
this note supplies that sufficient condition and its exact examples, without
claiming priority or dominance over the full 101-note #7869 package or other
decoder bounds. The DEN4 carry, Toeplitz, and Smith claims were not replayed.

## A strict improvement under unit, disjoint weights

`check.py` constructs an exact P104 decoder from 52 disjoint live pairs
`(a,b)`, so `Q[a,b]=1`. The full list of pairs is in [result.json](results/result.json). On each
pair use the following four rows; unspecified entries are zero:

| row | W(a) | W(b) | U(a) | U(b) |
|---|---:|---:|---:|---:|
| 0 | 1/2 | 1 | 0 | 1 |
| 1 | 1 | 1/2 | 1 | 0 |
| 2 | 1/2 | 0 | 0 | -1 |
| 3 | 0 | 1/2 | -1 | 0 |

Their four unmasked outer products sum to the 2-by-2 identity; each coefficient
appears in a live pattern cell, and different pair blocks do not interact. The
complete rational law is checked on all 10,816 P104 cells. Each of the 208
rows has full binary price 1, for `C=208`.

Let `S_A` contain all first ports and `S_B` all second ports. Both have size
52. On each block the row-gauge exponents `(0,-1,0,-1)` work for `S_A` and
`(-1,0,-1,0)` work for `S_B`. The script checks all difference constraints,
conjugated 2-integral coefficients, and reduced identities. For every block,
the respective restricted-rank vectors are `(0,1,0,0)` and `(1,0,0,0)`.
Their sum is at most the full row-price vector `(1,1,1,1)`. With both weights
equal to 1 the new bound is therefore **104**. The sets are disjoint, so this
example also obeys a per-port weight cap of one.

No single gaugeable subset can contain both ports of any pair. For its first
two rows, the difference constraints force both `lambda_1-lambda_0 <= -1`
and `lambda_0-lambda_1 <= -1` when both ports are selected. The 52 disjoint
negative cycles bound a single gaugeable set by 52; `S_A` attains 52. Thus
104 is a strict improvement over the exact best single-set bound 52 for this
decoder. The 104 figure is not an additional amount charged on top of 208,
nor a theorem that all P104 decoders admit such subsets.

## Pinned E8 example

`e8_check.py` parses the exact displayed eight-row #7852 non-vacuity instance,
checks all live rational cells and computes the full row ranks independently
by packed and dense binary elimination. They are `[9,9,9,8,7,9,9,9]`, with
actual mass 69. This is the displayed factorization, not a claim about the
minimum over E8 bases or decoders.

There are 87 ports with a negative self-loop, so none can occur in a gaugeable
set. The other 17 ports are each gaugeable on their own. Of their 136 pairs,
59 have a negative cycle; exhaustive enumeration of their incompatibility
graph gives independence number 6. The set `(3,36,56,62,77,93)` attains that
upper bound using gauge `(-1,0,0,-2,-1,-2,-1,0)`. Therefore **6 is the exact
best single gaugeable-subset size** for this factorization, not merely the
previous simple upper bound of 17.

Taking all 17 singleton sets at weight one uses the eight row budgets by
`[3,2,2,1,0,2,2,5]`, all within `[9,9,9,8,7,9,9,9]`. Their combined bound is
**17**, with disjoint ports and unit weights, versus the best single set 6.
Every singleton gauge and its mod-2 reduction are verified. It remains below
56.

Without a per-port weight cap, seven singleton sets can use weights
`{12:9, 62:9, 3:9, 93:8, 49:9, 36:9, 7:9}`. They use row budgets
`[9,9,9,8,0,9,9,9]`, giving **62** for this specific decoder. This is valid
under the row-budget lemma but simply exploits seven already-known full row
prices. It neither covers the 87 excluded ports nor proves Wall56 for any
other decoder. The 17 unit-weight result is the less permissive packing check.

## Why overlap and naive submodularity do not provide the budgets

Disjointness of the sets or a port-wise total weight at most one does **not**
imply the row-budget condition. On ports `0,6`,
`Q=[[1,1],[1,1]]`. Take the two-row rational decoder `W=[[1,1],[1,2]]`,
`U=[[2,-1],[-1,1]]`, with matrices indexed by port then row, so `WU^T=I`.
Both rows have full price 1, while each singleton restriction has price 1.
The two disjoint singletons would each charge the same row once, `1+1>1`.
Padding the remaining 102 ports with singleton rows yields a valid full P104
decoder, verified exactly. Its total cost is 104; this is a counterexample to
the proposed *row budget inference*, not to the final numeric lower bound.
Two ports are minimal for this port-disjoint overlap obstruction.

Nor is `r(S)=rank_F2 Q[D intersect S,G intersect S]` generally a submodular
set function. P104 ports `(0,6,11)` have principal pattern
`[[1,1,0],[1,1,1],[0,1,1]]`. For `D=G={0,6,11}`, `A={0,6}`, and
`B={6,11}`, the tuple `(r(A),r(B),r(A intersect B),r(A union B))` is
`(1,1,1,3)`, so the submodular inequality would read `2 >= 4`. This full
support occurs in an actual 2-integral P104 decoder: use `W=I+2J` and
`U=I-(2/7)J` on the three ports, and singleton rows elsewhere. The script
checks the entire decoder law. Thus a proof must establish the relevant row
budgets, not assume set submodularity.

## Reproduce

```
python3 -I -B verify.py
```

Run from the extracted package directory; no absolute filesystem path is
required. The inputs are SHA-256 pinned in the scripts. `e8_check.py` imports and runs
`check.py` under captured stdout, then parses the pinned instance separately.
The pair graph and a maximal gauge witness are in [e8_result.json](results/e8_result.json).
The scripts use only Python's standard library and execute in a single process.
