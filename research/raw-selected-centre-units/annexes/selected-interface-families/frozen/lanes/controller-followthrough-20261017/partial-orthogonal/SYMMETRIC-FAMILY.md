# A sharp weighted obstruction for the 42 symmetric responses

Let `S_0,...,S_41` be the exact dyadic matrices in the pinned file
`oblique-native-20261017/interior-cut/SYMMETRIC-RESPONSE-SEARCH.json`.
The modular entries in that file have the small dyadic lifts checked by
`check_symmetric_family.py`. This note concerns their specified real
linear span. It does not concern every response that a different native
word can supply.

For real coefficients `w_i`, set `E = sum_i w_i S_i`. If `D` is any
positive diagonal matrix and `E D E` is diagonal, then

`w_32 = w_33 = ... = w_41 = 0`.

Thus such a response has rank at most 64. The bound is attained. In
particular, no invertible real diagonal row and column gauges can turn a
full-rank member of this family into an orthogonal matrix, even if the
required squared row lengths can differ by component.

## The 48-port geometry

Directions `S_0,...,S_31` act only on a set of 64 ports. Directions
`S_32,...,S_39` act only on the complementary 48 ports. Write

`c_32 = c_37 = 2`, and `c_i = -1` for the other six indices.

Each `S_i/c_i`, for `32 <= i <= 39`, is the adjacency matrix of `K_6` on
an orthogonal six-dimensional pair-mode space. Each mode is a sum or a
difference of two physical coordinates. The eight mode spaces are
mutually orthogonal and cover the 48 physical coordinates.

The 24 physical coordinate pairs form the edges of `K_8` with the matching
`{(0,5),(1,6),(2,7),(3,4)}` removed. The vertices label directions 32
through 39. A physical pair supplies one mode to each of its two endpoint
vertices, with opposite pair signs. `SYMMETRIC-FAMILY.json` gives every
pair, its signs, its vertices, and the exact six-column basis at each
vertex. The checker verifies the `K_6` matrices and all range projectors.

Directions 40 and 41 have no entries inside the 48-by-48 restriction.
They couple the two port sets and also act within the 64-port set. The
proof below includes both directions.

## Proof with a positive certificate

Define the symmetric matrix

`Y = (S_32/2 - S_33 - S_34 - S_35 - S_36 + S_37/2 - S_38 - S_39)/6`.

Its diagonal is zero. Its support is contained in the 48-port set. Let
`d_j > 0` be the diagonal entries of `D`. The exact column identities give

```text
trace(Y E D E)
  = sum_{j in the 64-port set} d_j *
      ((w_40 - 2*w_41)^2/6 + 5*w_41^2/24)
    + sum_{j in the 48-port set} d_j *
      (5/3) * sum_{i incident to j} c_i^2*w_i^2.
```

Each physical coordinate in the second sum is incident to exactly two
vertices in the pair graph. Every index from 32 through 39 occurs.

Here is a direct verification of the identity. For a fixed physical
column `j`, form the 42-by-42 matrix with entries

`Q_j(i,k) = (S_i e_j)^T Y (S_k e_j)`.

On each of the 64 columns, its only nonzero block, at indices 40 and 41,
is

```text
 1/6  -1/3
-1/3   7/8
```

On each of the other 48 columns, its only nonzero entries are the two
diagonal values `(5/3)*c_i^2` at the incident vertices. The checker
verifies every entry of these 112 quadratic forms with exact fractions.
The displayed two-by-two block is positive definite: its determinant is
`5/144` and its first diagonal entry is positive.

If `E D E` is diagonal, the zero diagonal of `Y` makes the trace zero.
Every term on the right is nonnegative. Since every `d_j` is positive,
the first sum forces `w_40 = w_41 = 0`. The second sum forces all eight
remaining coefficients to vanish. This proves the claim.

For invertible real diagonal gauges `A` and `B`, the row Gram matrix of
`A E B` is `A E B^2 E A`. It is diagonal only if `E B^2 E` is diagonal.
The theorem applies because `B^2` is positive diagonal. A nonsingular
monomial real Gram matrix cannot give an additional case: a positive
definite symmetric monomial matrix is diagonal.

To attain rank 64, give directions 0 through 31 weight two at indices
congruent to 2 or 3 modulo 4, and weight one at the other indices. Give
all remaining directions weight zero. The resulting matrix has square
`4I` on the 64-port set and is zero on its complement.

## Consequence and limits

Changing coefficients or diagonal gauges in this symmetric family
cannot close the remaining 48-port response. A successful orthogonal
construction must add a response outside this family or change the
native word. The pair graph gives a concrete target: change the local
`K_6` scattering, its available projector terms, or the coupling between
the eight pair-mode spaces.

This theorem does not forbid a nonsymmetric reciprocal pair. It does
not establish a native-child lower bound. It does not concern a larger
response family from added legal transfer sites. It makes no claim about
the complete kappa bound.

Run from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/partial-orthogonal/check_symmetric_family.py
python3 -O work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/partial-orthogonal/check_symmetric_family.py
```

Both commands must print `PASS_SYMMETRIC_FAMILY_METRIC_OBSTRUCTION`.
`FREEZE.json` pins the proof, checker, receipt, and source files. This work
builds on the oblique-native response-space calculation. It is
AI-assisted research, and it is not a PR or a selected frontier result.
