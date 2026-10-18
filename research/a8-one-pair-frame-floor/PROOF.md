# The complementary A8 simplex frame orbit

This proof follows PR1248's deficiency method and PR1304's punctured-frame
extension. The changed frame, orbit coverage and finite lemmas below are
recomputed; no pending theorem supplies an assumed lower bound.

## Statement

Let V be the sum-zero subspace of R^9. Take the 120 root lines represented by
`e_a-e_b` for `0<=a<b<=8`, followed by `r_S=1_S-(1/3)1` for three-element S,
lexicographically within each group. Puncture the frame

```
F = [0,85,94,99,105,108,112,113]
```

or any of its coordinate-permutation images. On the 112 live roots set
`G_ij=r_i dot r_j` and fix `T_ik=r_ik`, for `k=0,...,8`.
For every complex D satisfying `D T^t=2G` on all live pairs, the sum of the
nine separate term costs is at least 71. Here the cost of a term is the F2
rank of `(G_ij+1) mod 2` on its nonzero row and column supports. Transpose is
ordinary transpose. The bound is attained with all nine terms active.

The orbit of F contains exactly 1,080 frames. Each has one pair root and seven
triple roots forming a Fano plane on the seven coordinates outside that pair.
Together with the 945 matching frames of PR1304, these exhaust all 2,025
orthogonal eight-frames. The sharp bound proved here concerns the new orbit.

## 1. Geometry and complete orbit coverage

Use labels `u_ab=1+e_a+e_b` and `u_S=1_S` in F2^9. All 14,400 entries of

```
u_i dot u_j = (G_ij+1) mod 2
```

are checked from exact integer coordinates. The live roots span V, and the
labels on each column support `{i:r_ik != 0}` span F2^9. These are finite
rank calculations; no root-hyperplane classification premise is needed.

The frame census recursively lists every increasing eight-clique in the
orthogonality graph. Its completeness follows by partitioning continuations
by their least next index and intersecting with that root's later neighbors.
The size bound only prunes a branch with too few remaining vertices. It finds
2,025 frames.

Adjacent coordinate transpositions generate S9. Applying their explicitly
checked root-line permutations to F until closure gives 1,080 frames. Doing
the same for `[0,15,26,33,42,89,112,119]` gives 945. The two sets are disjoint
and their union equals the entire clique census. Every frame in the first
orbit has one pair root; every frame in the second has four.

The second implementation independently obtains the same complete frame sets
from rational Gram entries. On seven points it enumerates all coordinate
images of F's seven triples, obtaining 30 labeled Fano planes. Choosing any
of the 36 coordinate pairs and any of these 30 planes constructs exactly the
1,080 one-pair frames. Equality of the enumerated sets is checked, not inferred
from their cardinalities.

Coordinate permutations preserve the fixed simplex normals up to permutation.
Signs needed to restore the chosen pair-root representatives preserve supports
and binary pairings. Applying those same row signs to D and T preserves the
all-pairs equation. Thus a bound and witness for F transport to its entire
orbit without changing costs.

## 2. Arbitrary complex coefficients reduce to deficiencies

Since the live roots span V, `D T^t=2G` is equivalent to

```
D_ik = 2r_ik + t_i,  with arbitrary t_i in C.
```

Indeed `D_i-2r_i` annihilates V and hence is a multiple of the all-ones vector.
The argument holds over C with the bilinear transpose and needs no positivity.

Let K_k be the binary annihilator of the labels on the nonzero row support
of column k, and let `delta_k=dim K_k`. Full label span on each T column makes
its pairing map injective on the D support, so its term cost is `9-delta_k`.
The total cost is therefore `81-sum delta_k`.

If `w in K_j` and `z in K_k` both evaluate to one on `u_i`, then
`D_ij=D_ik=0`, forcing `r_ij=r_ik`. Call this compatibility of the functionals
at j and k. This necessary condition concerns zero patterns, so includes all
complex shifts, even shifts giving no zero entries.

## 3. Exhaustive finite cover and upper bound

If all nine deficiencies are at most one, their sum is at most nine. Otherwise
choose an anchor j and a binary plane U inside K_j. Each plane has exactly
one encoding `0<a<b<a xor b`, so there are `511*510/6=43,435` planes.

For each other coordinate k, define H_k(U) as the functionals z compatible
with both basis vectors of U. This is the annihilator of the labels at rows
where `r_ij!=r_ik` and some basis vector evaluates to one. Compatibility with
the basis is equivalent to compatibility with all of U: a nonzero evaluation
of a linear combination needs a nonzero basis evaluation. Thus
K_k is contained in H_k(U).

The finite census checks `dim H_k<=2` for every anchor and plane. Enumerate
every subspace L_k of every H_k: zero, each line, and H_k itself when it is a
plane. Retain only tuples whose members are mutually compatible. For a
retained tuple let Q be the span of labels at rows where, for some k other
than j, `r_ij!=r_ik` and some vector of L_k evaluates to one. Necessarily

```
K_j subset Q^perp,
sum delta_k <= 9 - dim Q + sum_(k != j) dim L_k.
```

The actual tuple `L_k=K_k` occurs and is retained. Some relaxed tuples need
not be realizable by a decoder, which can only weaken the upper bound.
Planes with identical ordered partner spaces are grouped because the tuple
enumeration and Q depend only on these spaces and the anchor. Every plane
still contributes to the recorded multiplicities.

The exact exhaustive results are:

| Anchor | Planes | Ordered partner-space tuples | Compatible subspace choices | Largest upper bound |
|---|---:|---:|---:|---:|
| Each of 0,1 | 43,435 | 2,131 | 52,829 | 10 |
| Each of 2,...,8 | 43,435 | 2,251 | 39,482 | 9 |
| Total | 390,915 | 20,019 | 382,032 | 10 |

The primary checks all nine rows individually. The second checker derives
label coordinates from nine independent columns of the rational Gram pairing
matrix, computes H_k by nullspace algebra, enumerates Cartesian products, and
tests the forced coefficient values row by row. It checks representatives 0
and 2. Explicit coordinate permutations preserving F have orbits `{0,1}` and
`{2,...,8}`, establishing coverage of all anchors; its tables agree with the
primary. Both implementations are credited adaptations of PR1304, not separate
human review.

For every possible deficiency tuple, `sum delta_k<=10`. Hence cost is at
least 71. Mutual compatibility is material: at anchor 0 with
`U=span(1,508)`, dropping it permits an upper bound of 11, whereas including
it gives 10. The apparent cost 70 in that relaxation is not a decoder.

## 4. Sharp witnesses and COPY power contribution

Set `t_i=-2r_i0`. The costs are `(0,8,9,9,9,9,9,9,9)`, totaling 71.
At just the live root `e_0-e_2`, change its shift to `t_i=-2r_i2`.
All nine terms then become active, with costs `(1,8,8,9,9,9,9,9,9)`, also 71.
Both identities are checked on all `112^2=12,544` live pairs. The second
checker computes the active witness costs directly from pairing submatrices,
without the full-column-span shortcut.

There is also a COPY-only power comparison, when width, normalization and
term multiplicity are fixed. Each of the nine ranks lies between zero and
nine, and their sum is at least 71. For `0<p<=1`, monotonicity followed by
concavity bounds their total p-power below by `7*9^p+8^p`: first reduce the
sum to 71, then move mass from a smaller positive interior rank to a larger
one until only one rank is interior. Each move does not increase the concave
sum. The resulting ranks are seven nines, one eight and one zero. Therefore

```
sum rank_k^(1-a) >= 7*9^(1-a)+8^(1-a) > 8*8^(1-a),  0<=a<1.
```

This is strictly worse than the eight rank-eight coordinate COPY terms under
those same accounting parameters. It does not compare complete suppliers
with changed widths, role counts or shared-copy mechanisms.

## Scope

The result does not cover changed nine-normal families, unrestricted factors,
masked identities, other live-set sizes or shared-copy billing. No physical
word, frame/restoration/hosting proof, selected cold replay, new κ or all-size
multiplication theorem is supplied. The selected construction's inherited
algorithmic, analytic, precision and bit-interface obligations remain open.

Credit commdata2338/PR1304, Philipp/mightyOil/PR1248, joaqcoo/PR1224 and the
decoder/label lineage listed in README.md. Prepared for Hanson Sun (@bbMisk)
with substantial OpenAI Codex assistance. Apache-2.0.
