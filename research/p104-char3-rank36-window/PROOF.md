# Characteristic 3 admits a rank-36 pattern on P104

No new κ. The selected record stays `781451/250000000`. This note does not
build a word, a decoder, or a paid profile, and it does not change the
selected frontier.

The window below is the block-mask window of PR #6933. A physical decoder
for `k > 1` with exactly this mask is not derived, there or here.

## 0. Definitions

`P120` is the 120 vectors in `F_2^9` of weight congruent to 3 mod 4 (weights
3 and 7). Two distinct vectors are adjacent when their `F_2` dot product is
1 and orthogonal when it is 0. `P104` is the 104-vector subset in
`data/ports_p104.json`, byte-identical to the port list of #6933 at
`a967c521074c2c7450255ae237fda9c439ee1b35` (sha256
`691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c`). Its
complement in `P120` is 16 vectors and exactly two cliques of size 8. Each
of those cliques, added to `P104`, is a 112-vector set `P112`.

A **1-block pattern** on a vertex set `S` is a matrix, indexed by `S`, with
nonzero diagonal and with a zero in both off-diagonal positions of every
orthogonal pair. Entries on adjacent pairs are free, and the matrix need not
be symmetric. Write `w_1(S; F)` for the minimum rank of a 1-block pattern
over `F`, and `w(S; F)` for the infimum of `rank(B)/k` over k-block patterns
in the sense of #6933. Then `w(S; F) ≤ w_1(S; F)`.

The predecessor note (fork PR 151, discussion comment 19492602) proves
`w(S; F) ≤ 36` for every nonempty `S ⊆ P120` and every field of
characteristic not 3, by the matrix `3I − A`, and proves `w(S; F_3) ≤ 38` by
a degree-at-most-2 factorisation with no constant term. Characteristic 2 is
already settled by #6933 and is not reopened. The lower bounds
`w(P104) ≥ 13`, `w(P112) ≥ 14` and `w(P120) ≥ 15` in odd characteristic are
#6933, Theorem 4. They are cited and not replayed.

## 1. The adjacency square vanishes

**Lemma 1.** Let `A` be the adjacency matrix of the odd graph on `P120`.
Over every field of characteristic 3, `A^2 = 0`.

*Proof.* For an undirected simple graph, `(A^2)_ij` is the number of walks of
length 2 from `i` to `j`, including the degree on the diagonal. `verify.py`
enumerates all 120 vertices and all `C(120, 2) + 120` unordered pairs
`{i, j}` with `i ≤ j`, counts the common 1-bits of the two neighbor masks,
and checks that every count is divisible by 3. The domain is finite, every
pair is visited once, and the walk interpretation is the definition of `A^2`.
The same integer counts remain 0 in every field of characteristic 3. ∎

The predecessor proves that the graph is strongly regular with parameters
`(120, 63, 30, 36)`, which gives the integer identity
`A^2 = 27I − 6A + 36J`. All three coefficients are divisible by 3, so that
identity specialises to Lemma 1. The parameter census is not repeated here.
Lemma 1 does not depend on it.

## 2. The class-constant ansatz cannot have rank 36

Call a matrix **class-constant** when its diagonal entries are equal, its
adjacent entries are equal, and its orthogonal entries are equal. Every such
matrix has the form

```
α I + β A + γ (J − I − A).
```

**Lemma 2.** Over every field of characteristic 3, every class-constant
1-block pattern on `P120` has rank 120. In particular, no class-constant
pattern has rank 36.

*Proof.* An orthogonal pair has `A`-entry 0 and `(J − I − A)`-entry 1, so the
matrix entry there is `γ`. A pattern forces `γ = 0`. The diagonal entry is
then `α`. If `α = 0`, the diagonal vanishes and the matrix is not a pattern.
The reduction of `3I − A` is this illegal case: in characteristic 3 it equals
`−A`. If `α ≠ 0`, the matrix is `α(I + c A)` with `c = β α^{-1}`. Lemma 1
gives

```
(I + c A)(I − c A) = I − c^2 A^2 = I.
```

So the matrix is invertible and has rank 120. ∎

This is a proof for one restricted ansatz: matrices constant on the three
relations of the odd graph. It is not a proof that an arbitrary pattern has
rank greater than 36. The legal class-constant patterns are exactly the
invertible ones. `verify.py` checks the three monic cases `I + β A` over
`F_3`, including the inverse identity, and checks that `3I − A` has zero
diagonal modulo 3.

The same lemma is why the predecessor's rank-36 matrix does not reduce into
characteristic 3. Closing the gap needs a matrix that is not class-constant.

## 3. The degree-at-most-2 witness

Order the 46 monomials of degree at most 2 on `F_2^9` as the constant `1`,
the coordinates `x_0, …, x_8`, and the products `x_i x_j` for `0 ≤ i < j ≤ 8`.
Evaluate them at a vector as integers in `{0, 1}` and read the values in
`F_3`. This is a `120 × 46` matrix `Φ`.

For each vertex `v`, let `C_v` be the matrix whose rows are the rows of `Φ`
indexed by `v` and by the vertices orthogonal to `v`. The system
`C_v y = e`, with right-hand side 1 on the `v` row and 0 on the orthogonal
rows, is consistent. Its reduced row echelon form has a unique set of pivot
columns. Take the unique solution `y_v` supported on those pivot columns
(free coordinates equal to 0). Define `M_uv = Φ_u · y_v`.

**Theorem 1.** `M` is a 1-block pattern over `F_3` of rank 37. Its principal
submatrix on `P104` has rank 36. Extending scalars, the same matrix is a
1-block pattern of those same ranks over every field of characteristic 3.
Consequently, for every such field `F`,

```
w(P104; F) ≤ w_1(P104; F) ≤ 36,
w(P120; F) ≤ w_1(P120; F) ≤ 37.
```

Of the two `P112` extensions, the one that adds the clique

```
(7, 25, 42, 52, 76, 82, 97, 127)
```

has principal rank 36, and the one that adds

```
(67, 104, 137, 162, 266, 289, 448, 491)
```

has principal rank 37. So one 112-port extension meets the same ceiling 36,
and the other only meets 37.

*Proof.* `verify.py` rebuilds `Φ` and every `y_v`, substitutes the solutions
back into the equations, and checks every diagonal entry and both
off-diagonal entries of every orthogonal pair. Rank is the number of pivots
in Gaussian elimination over `F_3`. A minor is zero over `F_3` if and only
if it is zero over an extension, and a nonzero value in `F_3` stays nonzero,
so the rank is unchanged by scalar extension. A principal submatrix of a
pattern is a pattern. The sha256 of the `104 × 104` principal submatrix, in
the port-file order, is

```
473541e0dcc7e2c22e879d37ebd3cd3e1f88c1de5c0306fd42fa38ff134c6e6a
```

with entries written as bytes in `{0, 1, 2}` row by row. ∎

The same solver with the constant monomial omitted reproduces the
predecessor's pattern: rank 38 on `P120`, and rank 37 on the `P104` principal
submatrix. The predecessor recorded only the upper bound 38 for every subset.
The constant monomial is what drops the `P104` principal rank from 37 to 36
in this construction. `M` is not class-constant: it is asymmetric, and the
adjacent entries take more than one value. Lemma 2 does not apply to it.

## 4. What the witness does not minimise

`Φ` has rank 45. Its one-dimensional kernel is contained in the homogeneous
solution space of every vertex. The coefficient space of solutions with
diagonal normalised to 1 therefore has dimension 4 at each weight-3 vertex
and dimension 9 at each weight-7 vertex, while the space of legal columns
`Φ y` has dimension 3 and 8 respectively. `verify.py` checks these dimensions
for every vertex.

Theorem 1 uses one point of that affine family, the point whose free
coordinates are 0. It is not an exhaustive search of the family, and a
different point might have smaller rank on `P120`. No such point is claimed
here. The pairs-only and linear-only feature maps are inconsistent; that
rules out those smaller maps and does not rule out another 36-dimensional
model.

So three statements stay distinct:

1. **Proof, restricted ansatz.** Every class-constant pattern has rank 120
   in characteristic 3 (Lemma 2).
2. **Proof, one witness.** The explicit matrix of Theorem 1 has rank 36 on
   `P104` and rank 37 on `P120`.
3. **Not settled.** Whether every 1-block pattern on `P120` has rank at
   least 37, and whether some other point of the degree-at-most-2 family
   has rank 36 on `P120`. A search that did not find such a point would not
   decide either question. This note does not report one.

Accepting #6933, Theorem 4, without replaying it, the characteristic-3
intervals are now

| set | lower bound, cited | upper bound proved here |
|---|---|---|
| P104 | 13 | 36 |
| P112, clique `(7, 25, 42, 52, 76, 82, 97, 127)` | 14 | 36 |
| P112, the other deleted clique | 14 | 37 |
| P120 | 15 | 37 |

The lower bounds are not claimed for arbitrary subsets. Characteristic 2
stays inside #6933's interval `[53/6, 9]` on `P104` and the value 9 on
`P112` and `P120`.

## 5. What this does not say

A rank-36 pattern is not a multiplication algorithm, not a paid profile, and
not a change to the selected frontier. It does not show that 36 is the
minimum on `P104`: the cited lower bound is 13, and the star floor `53/6`
of #6933 is weaker. It does not show that `P120` admits rank 36. It does
not touch the `F_5` rank-13 factorisation. No human has reviewed this note.
