# Odd-character window of the P120 odd graph

No new κ. The selected value stays `781451/250000000`. This note bounds the
window of a port set from above. It does not build a word, a decoder, or a
paid profile.

## 0. Definitions

Let `P120` be the 120 vectors in `F_2^9` of weight 3 or 7 (weight congruent to
3 mod 4). Two distinct vectors are **adjacent** when their `F_2` dot product
is 1 and **orthogonal** when it is 0. The **odd graph** has those adjacencies
as edges.

`P104` is the 104-vector subset stored in `data/ports_p104.json` (70 of weight
3 and 34 of weight 7). Its complement in `P120` has 16 vectors and exactly two
cliques of size 8. Each of those cliques, added to `P104`, is a 112-vector set
`P112`. These are the same sets as in PR #6933: the port file is byte-identical
to `research/p104-port-window-haemers/data/ports_p104.json` at head
`a967c521074c2c7450255ae237fda9c439ee1b35`, and the induced odd graph on `P104`
is 55-regular, as recorded there.

A **1-block pattern** on a vertex set `S` is a matrix, indexed by `S`, with
nonzero diagonal and with a zero in both off-diagonal positions of every
orthogonal pair. Entries on adjacent pairs are free, and the matrix need not
be symmetric. Write `w_1(S; F)` for the minimum rank of a 1-block pattern over
`F`, and `w(S; F)` for the infimum of `rank(B)/k` over k-block patterns on `S`
in the sense of #6933. Then `w(S; F) ≤ w_1(S; F)` because the infimum includes
the case `k = 1`. The identification of this window with the fractional
Haemers bound is #6933, Theorem 1, and is not used below.

## 1. Degree

**Lemma 1.** Every vertex of the odd graph on `P120` has degree 63.

*Proof.* There are `C(9,3) = 84` weight-3 vectors and `C(9,7) = 36` weight-7
vectors.

Let `u` have weight 3, and let `T` be the complementary 6-set. A weight-3
neighbor meets `u` in one coordinate: 3 choices there and `C(6,2) = 15` in
`T`, so 45 neighbors. A weight-7 vector has a 2-set complement `s`. Its dot
with `u` is odd if and only if `|u ∩ s|` is even, because the two pieces
partition the three coordinates of `u`. The even possibilities are `|u ∩ s| = 0`
(`C(6,2) = 15` sets `s`) and `|u ∩ s| = 2` (`C(3,2) = 3` sets). That is 18
neighbors. The degree is `45 + 18 = 63`.

Let `u` have weight 7, with 2-set complement `t`. A weight-3 vector `v` has odd
dot with `u` if and only if `|v ∩ t|` is even. There are `C(7,3) = 35` such
`v` disjoint from `t`, and 7 that contain `t`. A different weight-7 vector has
2-set complement `s ≠ t`, and the same parity count used above shows that the
dot is odd if and only if `s` is disjoint from `t`. There are `C(7,2) = 21`
such 2-sets. The degree is `42 + 21 = 63`. ∎

`verify.py` recomputes both sides of this count and then enumerates every
vertex.

## 2. Strongly regular parameters

**Lemma 2.** The odd graph on `P120` is connected and strongly regular with
parameters `(n, k, λ, μ) = (120, 63, 30, 36)`.

*Proof of the census.* `verify.py` counts common neighbors of every unordered
pair twice, once with bitsets and once with set intersection, and requires the
two counts to agree. The degree is constantly 63, adjacent pairs have exactly
30 common neighbors, and orthogonal pairs have exactly 36. A walk from vertex 0
reaches all 120 vertices. ∎

The constant parameters are a complete finite enumeration, not a sample. The
hand argument of Lemma 1 covers only the degree.

## 3. The rank-36 pattern

Let `A` be the adjacency matrix and `J` the all-ones matrix. Lemma 2 is the
matrix identity

```
A^2 = k I + λ A + μ (J - I - A) = 27 I - 6 A + 36 J.
```

**Lemma 3.** `(A - 3I)(A + 9I)(A - 63I) = 0`, the three factors are pairwise
coprime over `Q`, and

```
dim ker(A - 63I) = 1,  dim ker(A - 3I) = 84,  dim ker(A + 9I) = 35.
```

*Proof.* The displayed square rearranges to `A^2 + 6A - 27I = 36 J`. The
scalar polynomial factors as `x^2 + 6x - 27 = (x - 3)(x + 9)`, since
`(-6)^2 + 4·27 = 144`. Right-multiplication by `A - 63I` kills `J`, because
`AJ = 63 J` by regularity, so

```
(A - 3I)(A + 9I)(A - 63I) = 0.
```

The linear factors are distinct over `Q`. If a matrix satisfies `fg(A) = 0`
with `gcd(f, g) = 1`, polynomials `a, b` with `af + bg = 1` split the space
into `ker f(A)` and `ker g(A)`. Applying that twice, `Q^{120}` is the direct
sum of the three kernels. The all-ones vector lies in `ker(A - 63I)`. If
`(A - 63I)x = 0`, every coordinate of `x` equals the average of its neighbors.
A coordinate of maximum value forces the same value on its neighbors, and
connectedness forces `x` to be constant. Thus that kernel is one-dimensional.

Let `f = dim ker(A - 3I)` and `g = dim ker(A + 9I)`. Then `f + g = 119`.
The diagonal of `A` is zero, so `tr(A) = 0`, and that trace is
`3f - 9g + 63`. Equivalently `f - 3g = -21`.
Substitution gives `4g = 140`, so `g = 35` and `f = 84`. ∎

**Theorem 1.** Let `H = 3I - A`. Over `Q`, `H` has rank 36, diagonal 3, and
zeros on every orthogonal pair. For every field `F` of characteristic not 3,
the reduction of `H` is a 1-block pattern of rank at most 36. For every
nonempty `S ⊆ P120`,

```
w(S; F) ≤ w_1(S; F) ≤ 36.
```

*Proof.* `H = -(A - 3I)`, so Lemma 3 gives rank 36 over `Q`. The diagonal is 3
and the off-diagonal support is the edge set. In characteristic not 3 the
diagonal remains nonzero, and rank cannot rise under reduction. A principal
submatrix is a 1-block pattern on its index set and has rank at most 36. ∎

`verify.py` checks that the reduction has rank exactly 36 modulo 5, 7, 11 and
10007, which matches the rational rank, and that a single planted orthogonal
entry is rejected. Modulo 3 the diagonal of `H` is 0, so this matrix is not a
pattern in characteristic 3. That control is the reason for the next section.

In characteristic 2 the same reduction is a legal pattern of rank at most 36.
It does not improve the rank-9 Gram pattern already recorded for `P104`,
`P112` and `P120` in #6933. The new ceiling is the odd-character one.

## 4. Characteristic 3

Index features of a vector `v` by the nine coordinates and the `C(9,2)`
coordinate products, evaluated in `{0,1}` and read in `F_3`. This is a
45-column matrix `Φ`. For each vertex `v`, the linear system

```
Φ_u · y = 1 if u = v,   Φ_u · y = 0 if u is orthogonal to v,
```

with adjacent rows unconstrained and with free variables set to 0, has a
solution `y_v`. `verify.py` solves all 120 systems and substitutes the
solutions back into the equations. The matrix `M_uv = Φ_u · y_v` is therefore
a 1-block pattern over `F_3`, and `M = Φ Y^T` has rank at most 45. Gaussian
elimination gives rank exactly 38.

**Theorem 2.** Over `F_3`, `w(S; F_3) ≤ w_1(S; F_3) ≤ 38` for every nonempty
`S ⊆ P120`.

The nine linear coordinates alone do not solve these systems: all eight
sampled columns in `verify.py` are inconsistent. The quadratic coordinates are
part of this factorisation, not an unused pad. The same eight samples are not
a proof that no rank-36 pattern exists in characteristic 3.

## 5. The interval, conditional on #6933

#6933, Theorem 4, states that in every characteristic other than 2,

```
w(P104; F) ≥ 13,   w(P112; F) ≥ 14,   w(P120; F) ≥ 15,
```

because `n/8` equals those three integers and the E8 root-line form has rank
at most 8. That argument is not replayed here. Accepting it, Theorems 1 and 2
give

| field | P104 | P112 | P120 |
|---|---|---|---|
| char ≠ 2, 3 | [13, 36] | [14, 36] | [15, 36] |
| char 3 | [13, 38] | [14, 38] | [15, 38] |

#6933 already places the characteristic-2 window of `P104` in `[53/6, 9]` and
the characteristic-2 windows of `P112` and `P120` at exactly 9. Theorem 1 does
not narrow those characteristic-2 intervals.

The lower bounds are not claimed for arbitrary subsets. #6933 exhibits a
14-port subset with a 2-block pattern of rank 17, ratio `17/2 < 9`.

## 6. What this does not say

The window is the block-mask quantity of #6933. That note already records that
a physical decoder for `k > 1` with exactly this mask is not derived. A rank-36
pattern is not a multiplication algorithm, not a paid profile, and not a
change to the selected frontier. No human has reviewed this proof.
