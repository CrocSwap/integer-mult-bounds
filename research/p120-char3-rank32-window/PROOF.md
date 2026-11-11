# Characteristic 3 admits a rank-32 pattern on P120

No new κ. The selected record stays `781451/250000000`. This note does not
build a word, a decoder, or a paid profile, and it does not change the
selected frontier.

The window is the block-mask window of PR #6933. A physical decoder for
`k > 1` is not derived.

## 0. Definitions

`P120` is the 120 vectors in `F_2^9` of weight congruent to 3 mod 4. Two
distinct vectors are adjacent when their `F_2` dot product is 1 and orthogonal
when it is 0. `P104` is the port list of #6933, the same file vendored by
#6953, sha256
`691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c`. Its
complement is the two 8-cliques recorded in #6953.

A **1-block pattern** has nonzero diagonal and a zero in both off-diagonal
positions of every orthogonal pair. Adjacent entries are free, and the matrix
need not be symmetric. Write `w_1(S; F)` for the minimum rank of a 1-block
pattern on `S` over `F`, and `w(S; F)` for the infimum of `rank(B)/k` over
k-block patterns in the sense of #6933. Then `w(S; F) ≤ w_1(S; F)`.

#6953 proves `w_1(P120; F_3) ≤ 37` and `w_1(P104; F_3) ≤ 36` by one
degree-at-most-2 point, and proves that every class-constant pattern on
`P120` has rank 120 in characteristic 3. The lower bounds `w(P104) ≥ 13`,
`w(P112) ≥ 14` and `w(P120) ≥ 15` in odd characteristic are #6933, Theorem 4.
They are cited and not replayed. This note does not extend those lower bounds.

## 1. The degree-at-most-2 chart

Order monomials as the constant `1`, the coordinates `x_0, …, x_8`, and the
products `x_i x_j` for `0 ≤ i < j ≤ 8`. Evaluate them at a vector as integers
in `{0, 1}` and read the values in `F_3`.

**Lemma 1.** On `P120`, `sum_{i<j} x_i x_j = 0` as a function to `F_3`. The
remaining 45 monomials, with `x_7 x_8` omitted, have evaluation rank 45.

*Proof.* For a 0-1 vector the pair sum equals `binom(wt(v), 2)`. That binomial
coefficient is 3 at weight 3 and 21 at weight 7, both divisible by 3.
`verify.py` evaluates the sum at all 120 vectors and row-reduces the 45-column
evaluation matrix. The domain is finite and every vector is visited once. ∎

Every degree-at-most-2 function therefore has a unique coefficient vector in
this 45-coordinate chart. Call that space of functions `E`.

## 2. The witness span of the previous point

For each vertex `v`, let the legal equations require value 1 at `v` and value
0 at every vertex orthogonal to `v`. Gaussian elimination over `F_3`, with
free variables set to 0, produces a solution `q_v` in the 45-chart. This is
the point constructed in #6953. The matrix `M^0_{uv} = φ(u) · q_v` is a
1-block pattern of rank 37. The vectors `q_v` span a 37-dimensional subspace
`S ⊆ E`. Both statements are the row counts of the reduced forms in
`verify.py`.

The reduced row echelon form is unique: elimination runs left to right, each
pivot is scaled to 1, and the pivot column is cleared above and below. The
kernel basis used below is the standard one for that unique form. For each
free column, in increasing order, the basis vector has a 1 in that free
column, 0 in the other free columns, and pivot entries equal to the negation
of the reduced coefficient. It does not depend on row order.

## 3. Eight rigid columns

**Lemma 2.** Inside `S`, the eight weight-7 vectors that do not contain
coordinate 8 have no legal direction. Each has a unique legal column in `S`,
namely its witness column `q_v`, and those eight columns are linearly
independent.

The eight vectors are

```
127, 191, 223, 239, 247, 251, 253, 254.
```

*Proof.* A direction in `S` is a linear combination of an RREF basis of `S`.
`verify.py` imposes vanishing on `{v} ∪ orth(v)` and counts the kernel. The
kernel is zero at exactly these eight vertices, and the eight witness
coordinate vectors have rank 8. The vertex list is the full set of weight-7
vectors with bit 8 clear: a weight-7 vector with bit 8 clear has its single
other zero among the first eight coordinates, so there are eight of them. ∎

This uniqueness is inside `S`. It is not a uniqueness statement in `E`, and
not a uniqueness statement among all patterns.

## 4. One hyperplane of the witness span

Let `U` be the span of those eight rigid columns, and let `π_0, …, π_28` be
the canonical kernel basis of `U` in the 37 coordinates of `S`.

**Lemma 3.** The hyperplane `ker(π_1)` is the unique hyperplane in this
29-element basis that still meets every legal affine flat of `S`. The space
`W = ker(π_1) ∩ S` has dimension 36.

*Proof.* `verify.py` tests each of the 29 basis vectors. For a form `π`, it
solves the legal equations inside `S` together with `π · c = 0`. The system
is consistent for every vertex if and only if `i = 1`. The two nonzero scales
of `π_1` determine the same kernel. Consistency is checked at all 120
vertices. This is an exhaustive census of this basis, not of every hyperplane
of `S`. ∎

The same space `W` is the set of coefficient vectors satisfying the nine
independent equations

```
c + a_8 = 0,
sum_{i=0}^{7} a_i + 2 a_8 + 2 sum_{0≤i<j≤7} b_{ij} = 0,
b_{i8} = 0 for i = 0, …, 6,
```

with `b_78 = 0` already built into the chart. `verify.py` checks that these
nine rows span the annihilator of `W`.

## 5. The rank-32 pattern

Let `ψ_1, …, ψ_36` be the canonical kernel basis of `π_1` inside `S`, lifted
to the 45-chart, and let `Φ` be their `120 × 36` evaluation matrix. For each
vertex `v`, let `y_v` be the solution of the legal equations `Φ y = e_v` with
free coordinates set to 0. Define `M_uv = Φ_u · y_v`.

**Theorem 1.** `M` is a 1-block pattern over `F_3` of rank 32. Its pivot
columns and the coordinates of the remaining columns are a `120 × 32`
factorisation of `M` over `F_3`. Extending scalars does not change the rank,
so for every field `F` of characteristic 3,

```
w(P120; F) ≤ w_1(P120; F) ≤ 32.
```

The same matrix has principal rank 32 on `P104` and on both `P112`
extensions. A principal submatrix of a pattern is a pattern, so the same
upper bound 32 holds for those three sets.

*Proof.* `verify.py` rebuilds `Φ` and every `y_v`, checks every diagonal
entry and both off-diagonal entries of every orthogonal pair, and counts
pivots of `M`, of the column-reversed matrix, and of the transpose. All three
counts are 32. The sha256 of `M`, entries in `{0, 1, 2}` in increasing vertex
order, row by row, is

```
81e209bb5be3c3e9b9a5d593190fd9b19540656bb0162164f4df7a1f0bf4a8c4
```

The 32 pivot columns are linearly independent, and every column of `M` reduces
into their span, which is the factorisation. A minor vanishes over `F_3` if
and only if it vanishes over an extension, and a nonzero value stays nonzero,
so the rank is unchanged by scalar extension. The port-file principal
submatrix and both 112-vertex principals are checked in the same way. ∎

`M` is not class-constant: it is asymmetric, and the adjacent entries take
more than one value. The class-constant matrices `I + β A` still have rank
120, as in #6953. The pure quadratic monomials remain inconsistent, so this
is not that smaller map.

## 6. What the rank is attached to

`W` is 36-dimensional, but the free-zero rule depends on the basis. In the
canonical kernel basis of the nine relations of section 4, the same legal
systems have a solution, and that other point is a 1-block pattern of rank
36. `verify.py` rebuilds it. Rank 32 belongs to the basis carried from `S`
in Theorem 1. It is not an invariant of the set of all patterns with columns
in `W`.

Inside that basis the legal solution spaces have affine dimensions 0 at 36
vertices, 2 at 56 vertices, and 5 at 28 vertices. `verify.py` counts these
nullities. The witness uses one point of each affine space, the free-zero
point. It was not minimized over those spaces. The checked rank-36 point of
the previous paragraph already shows that `W` does not by itself force rank
32.

So three statements stay distinct:

1. **Proof, one witness.** The matrix of Theorem 1 has rank 32. The checks
   that identify it are exhaustive on a finite domain: every vertex, every
   orthogonal pair, one reduced form, and all 29 vectors of one kernel basis.
2. **Proof, one other point of the same space.** Another explicit basis of
   `W` gives a legal pattern of rank 36.
3. **Not settled.** Whether some pattern, inside `W` or outside `E`, has
   rank at most 31, and whether every 1-block pattern on `P120` has rank at
   least 32. A search that did not find a smaller pattern would not decide
   either question. This note does not report one.

Accepting #6933, Theorem 4, without replaying it, the characteristic-3
intervals are now

| set | lower bound, cited | upper bound proved here |
|---|---|---|
| P104 | 13 | 32 |
| either P112 extension | 14 | 32 |
| P120 | 15 | 32 |

#6953 had upper bounds 36, 36, 37 and 37 on these four sets. The upper end
32 is strictly smaller than the rank of `3I − A` off characteristic 3, which
is 36. No equality is claimed. Characteristic 2 stays inside #6933.

## 7. What this does not say

A rank-32 pattern is not a multiplication algorithm, not a paid profile, and
not a change to the selected frontier. It does not show that 32 is the
minimum on `P120` or on `P104`. It does not touch the `F_5` rank-13
factorisation. The construction uses the coordinate chart of `F_2^9` and is
not claimed to be invariant under a larger automorphism group. No human has
reviewed this note.
