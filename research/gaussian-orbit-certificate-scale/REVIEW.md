# Independent review of the Gaussian symmetry-orbit certificate scale

Outcome: PASS for the stated exact homogeneous-kernel certificate class and
its explicitly separated finite-precision extension. No multiplication,
displacement-rank, arbitrary-order or implicit-generation lower bound follows.
Prepared for @CubeJerry with substantial OpenAI assistance. The orchestrator
proposed the research question and separately checked the worker's derivation;
this is not independent human or proof-kernel acceptance.

## Universal proof review

Entry-transpose products remove the positive shift and recover every squared
Euclidean distance. Polarization against one origin and its d opposite axis
corners extends any vertex symmetry to an affine Euclidean isometry. Mapping
the convex hull onto itself forces a signed coordinate permutation. A nonunit
positive shift preserves the coordinate sum and excludes each negative sign.
The inverse has the same symmetry group because permutation conjugation
commutes with inversion; Vandermonde factorization proves nonsingularity.

Coordinate cycle orders are at most g(d); signed cycle orders divide twice
the coordinate order. Every vertex cycle is no longer than that order. This
proves the lower bound on the NUMBER OF BOUNDARY CYCLES. It imposes no lower
bound on the rank of their boundary displacement or an optimized generator
basis.

The finite prime-power characterization of g(d) follows from assigning each
maximal prime power of an lcm to one contributing coordinate cycle. Distinct
prime-power lengths have coprime word periods, including shorter periods, so
products of block orbits form single simultaneous orbits. The exact Burnside
correction is bounded by the prime's first-power correction. The sole small
exception in the rough bound, length4, has exact correction n^-2+2n^-3<=n^-1.
Summing the odd-prime envelope over all odd integers gives8/9. The geometric
majorant for the exponential yields C<=419/114<4. The maximum-order witness
is only a constant-factor construction: the d5 binary example correctly
separates it from finite cycle-count optimality.

The classical asymptotic log g(d)~sqrt(d log d) is explicitly cited, not
claimed as new. The root separately opened Deléglise--Nicolas--Zimmermann,
JTNB20(2008),625--671, DOI10.5802/jtnb.644, and confirmed equations2 and6.
The new use of this fact is the certificate scale and dense-format consequence.

## Precision and cost review

The grid graph proof is sound: minimum degree identifies corners; corner
graph distances identify the cube action; distances to the origin and its
axis-opposite corners recover every interior coordinate. Entry-error disks
for adjacent and nonadjacent values are disjoint under the stated strict
gaps. In the shifted case ideal entries have magnitude at most1, giving
pair-product error2delta+delta^2. A second directed edge gap excludes sign
reversals, but is not needed for the factor-two asymptotic scale.

Arbitrary errors give only containment. Distinct tiny diagonal perturbations
can force the identity group. Common scalar rounding preserves original
symmetries; equal rounded factors preserve coordinate permutations and, in
the unshifted case, reversals. Factor errors must first be converted to the
global bound d epsilon (1+epsilon)^(d-1). Inverting a nonsingular perturbed
matrix preserves its symmetry group but is not a stability or rounding
result for an independently rounded inverse.

The grouped DP's conservative polynomial bit bill allows whole-table scans
and schoolbook arithmetic. Vertex enumeration pays for repeated cycles and
full label scans; ingress and restoration each pay a sequential sort. The
2cT dense-slot count includes prescribed zeros. Removing dependent or zero
vectors, changing the basis, or using implicit access escapes this specified
format and is explicitly excluded. Coefficient generation and arithmetic
can only add to its write bill. Comparing this optimistic size against the
separable axis method proves the stated obstruction within this format.
Actual matching of source factors, local owners, gauges and full caller costs
remain open; none is obtained from the matrix classification.

## Independent executable evidence

The root checker imports no worker code and uses exact rational arithmetic.
It enumerates every permutation of the vertex set for10 kernel fixtures,
including a3-by-3 grid. Integer-partition lcms and a separately written
prime-group knapsack agree through dimension14. Twenty-eight dimension/base
families compare the exact minimum over all coordinate cycle types with the
constructed cycle count. Eight explicit word-orbit traversals agree with
Burnside sums, and81 prime-power/base cases check the correction envelope.

Six controls cover noncoprime period products, finite maximum-order
nonoptimality, fine common rounding, a tiny nonzero shift acquiring
reflections, coarse rounding acquiring noncoordinate symmetries, and
arbitrarily small diagonal errors destroying all symmetries. The last
example is checked by distinct diagonal entries, which force every vertex
to be fixed; it does not depend on a search over32-factorial permutations.

Both warning-strict normal and optimized Python3.12 executions pass and
produce byte-identical receipts. These are bounded checks, not proofs of
the universal classification or Landau asymptotic.

```
python3 -I -W error -B check_scale_independently.py
python3 -I -W error -O -B check_scale_independently.py
```
