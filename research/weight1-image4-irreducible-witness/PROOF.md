# A weight-1 no-edge pool of image dimension 4 can be irreducible

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

No new κ is claimed. At the base commit the selected record is
`363005817/100000000000`. This note does not change that record.
`docs/research/current-priorities.md` on the same commit still quotes an
older checkpoint; the selected record is the frontier value used here.

Evidence class: a **proof** that one explicit pool meets the hypotheses
below and acts irreducibly. The 67-element subspace lattice of its joint
image is an **exhaustive finite census** of that one four-dimensional
space and agrees with the proof. The width-4 through width-8 pool scans
are finite checks of those widths. They are not a census of all
weight-1 pattern spaces, and no search is used as a nonexistence proof.

## Witness

Work over `F2`. For a matrix `N`, write `off(N)` for `N` with its diagonal
deleted. For a linear space `P` of zero-diagonal matrices, the complete
noncoordinate pool is

```text
C(P) = {N = x y^T : y^T x = 1, off(N) ∈ P, off(N) ≠ 0}.
```

`V(P)` is the sum of the images of `C(P)`. A subspace `W ⊆ V(P)` is
invariant when `N(W) ⊆ W` for every `N ∈ C(P)`. The action is irreducible
when the only invariant subspaces are `0` and `V(P)`.

Index coordinates by `Z/4Z`. For each `i` put

```text
x_i = e_i + e_{i+1} + e_{i+2},    N_i = x_i e_i^T,
```

and let `P` be the span of the four off-diagonal patterns, padded by zero
rows and columns when the ambient width `W` is greater than 4. Each
covector `e_i` has weight 1. Each image `x_i` has weight 3.

**Witness.** For every `W ≥ 4`, this `P` has dimension 4 and contains no
matrix unit, `C(P) = {N_0, N_1, N_2, N_3}`, every pool covector has weight
1, and `dim V(P) = 4`. The action on `V(P)` is irreducible.

So the answer to the question left by #7138 is no: not every weight-1
no-edge pool of pattern dimension 4 and joint-image dimension 4 is
reducible. The four disjoint weight-1 lines recorded in #7138 meet the
same dimension counts and are reducible. Section 5 recalls them so this
witness is not read as a claim that every such pool is irreducible.

These four operators are the transposes of the #6962 four-cycle. There
`M_i = e_i x_i^T` has image weight 1 and covector weight 3. Here
`N_i = M_i^T = x_i e_i^T` swaps those weights. Completeness and
irreducibility are proved below for `N_i`; they are not quoted from the
argument for `M_i`, because the representation has changed.

## 1. The pattern space

Deleting the diagonal of `N_i` leaves

```text
p_i = E_{i+1,i} + E_{i+2,i}.
```

Column `i` has weight 2, and the other columns are zero. The four patterns
occupy four different columns, so they are linearly independent and
`dim P = 4`. A general element is indexed by `A ⊆ Z/4Z`,

```text
p_A = sum_{i ∈ A} p_i.
```

Column `i` of `p_A` is zero when `i ∉ A` and has weight 2 when `i ∈ A`.
The columns are disjoint, so `p_A` has weight `2|A|`. Every nonzero
element has weight at least 2, and `P` contains no matrix unit.

## 2. The pool is exactly the four projectors

Each `N_i` lies in `C(P)`: `e_i · x_i = 1`, and `off(N_i) = p_i`.

Let `x, y ∈ F2^W` satisfy `y · x = 1` and `off(x y^T) ∈ P`, with the
pattern nonzero.

Both vectors are supported on `{0,1,2,3}`. Every matrix in `P` is zero in
each row `t ≥ 4` and each column `t ≥ 4`. Suppose `x_t = 1` for some
`t ≥ 4`. The off-diagonal part of row `t` of `x y^T` is `y` with
coordinate `t` cleared, and that row of `P` is zero, so `y = e_t`. Then
`y · x = 1`. Column `t` of `x y^T` is `x`, and the off-diagonal part of
that column is zero, so `x = e_t`. The pattern is zero, which is excluded.
Thus `x_t = 0` for every `t ≥ 4`.

Suppose instead `y_t = 1`. The off-diagonal part of column `t` is zero, so
`x ∈ {0, e_t}`. The case `x = 0` contradicts `y · x = 1`, so `x = e_t`.
That contradicts `x_t = 0`. Thus `y_t = 0` as well. For `W = 4` there is
no such `t`, and this paragraph is vacuous.

Now `x` and `y` lie in `F2^4`. Let `T` be the support of `y`. For each
`b ∈ T`, the off-diagonal column `b` of `x y^T` is `x` with coordinate
`b` cleared. The only possible nonzero column of an element of `P` in
position `b` is

```text
v_b = e_{b+1} + e_{b+2},
```

which has weight 2 and a zero in row `b`.

That off-diagonal column cannot be zero. If it were, then `x = e_b` and
`y · x = y_b = 1`. Any other index `s ∈ T` would then have off-diagonal
column `e_b`, which has weight 1. It is neither zero nor `v_s`. So no
such `s` exists, `T = {b}`, and the pattern is zero, which is excluded.
Therefore every `b ∈ T` has off-diagonal column `v_b`, and

```text
x = α_b e_b + e_{b+1} + e_{b+2},    α_b = x_b.
```

If `|T| ≥ 2`, take distinct `b, s ∈ T`. The two expressions for `x` agree.

When `s = b+1`, the expressions are `α e_b + e_{b+1} + e_{b+2}` and
`β e_{b+1} + e_{b+2} + e_{b+3}`. Coordinate `b` forces `α = 0`.
Coordinate `b+3` is 0 on the left and 1 on the right.

When `s = b+2`, the expressions are `α e_b + e_{b+1} + e_{b+2}` and
`β e_{b+2} + e_{b+3} + e_b`. Coordinate `b` forces `α = 1`. Coordinate
`b+1` is 1 on the left and 0 on the right.

Every pair in `Z/4Z` has difference 1 or 2. Both cases contradict.
Therefore `|T| = 1`. Let `T = {b}`. Idempotence forces `α_b = 1`, so

```text
x = e_b + e_{b+1} + e_{b+2} = x_b,    y = e_b,
```

and the pattern is `p_b`. This projector is `N_b`.

Hence `C(P) = {N_0, N_1, N_2, N_3}` at every width `W ≥ 4`. Every covector
has weight 1.

## 3. The joint image is four-dimensional and the kernel is zero

The four images lie in `span{e_0, e_1, e_2, e_3}`. In that basis, with
columns `x_0, x_1, x_2, x_3`, the matrix is

```text
1 0 1 1
1 1 0 1
1 1 1 0
0 1 1 1.
```

Add row 0 to rows 1 and 2. Add the new row 1 to rows 2 and 3. Add the new
row 3 to the new row 2. Add that row 2 and row 3 to row 0, then add row 2
to row 1. The result is the identity. The four images are a basis of the
coordinate subspace, so `dim V(P) = 4` and

```text
V(P) = span{e_0, e_1, e_2, e_3}
```

inside `F2^W`. Each covector is a distinct coordinate functional `e_i`.
Their common kernel on `V(P)` is zero. The kernel test of #7138, which
needs a positive-dimensional common kernel, does not see an invariant
subspace of this pool.

## 4. The action is irreducible

On `V = V(P)`, the operator `N_i` is `z ↦ (e_i · z) x_i`. Let `W ⊆ V` be
invariant and set

```text
A = {i ∈ Z/4Z : x_i ∈ W}.
```

If `i ∉ A`, then `x_i ∉ W`. For every `w ∈ W`, the vector `N_i(w)` is
either `0` or `x_i`, so invariance forces `e_i · w = 0`. Thus

```text
W ⊆ {z ∈ V : z_i = 0 for every i ∉ A} = span{e_j : j ∈ A}.
```

The right-hand side has dimension `|A|`, and it is contained in `V`
because Section 3 identifies `V` with the full coordinate subspace. Each
`x_i` with `i ∈ A` therefore lies in `span{e_j : j ∈ A}`, which means

```text
{i, i+1, i+2} ⊆ A.
```

If `A` is nonempty, pick `i ∈ A`. Then `i+1 ∈ A`, then `i+2 ∈ A`, then
`i+3 ∈ A`. So `A = Z/4Z`.

The empty set forces `W ⊆ {0}`. The full set puts every `x_i` into `W`.
Those four vectors are a basis of `V`, so `W = V`. No subspace
`0 < W < V` is invariant.

In particular no line `span(x_i)` is invariant: `e_{i+1} · x_i = 1`, so
`N_{i+1}(x_i) = x_{i+1}`, and Section 3 says `x_{i+1}` is not a scalar
multiple of `x_i`.

## 5. The four disjoint lines stay reducible

#7138, Section 5, records a different weight-1 pool. On twelve
coordinates, for `b = 0,1,2,3`,

```text
u_b = e_{3b} + e_{3b+1} + e_{3b+2},    L_b = u_b e_{3b}^T.
```

That note proves the four operators are the complete pool of their
pattern span: dimension 4, no matrix unit, image dimension 4, and trivial
common kernel, with each line `span(u_b)` invariant. This package does not
reprove that completeness statement. The operators themselves already show
the contrast used here. Each covector has weight 1, the four images are
independent, and `e_{3c} · u_b = 0` for `c ≠ b`, so each line is invariant
and the common kernel on the image is zero.

The same dimension counts and a trivial kernel therefore occur both for a
reducible pool and for the irreducible witness of Sections 1 through 4.
Kernel dimension zero does not decide the question.

## 6. An irreducible example has four columns of dimension 1

This lemma locates the witness. It is not a classification.

Let `P` be a linear space of zero-diagonal `W` by `W` matrices with
`dim P = 4` and with no matrix unit. Suppose every covector of `C(P)` has
weight 1, `dim V(P) = 4`, and the action on `V(P)` is irreducible. Then
`P` is the direct sum of four one-dimensional column spaces, on four
distinct columns, and the four coordinate functionals are a basis of the
dual of `V(P)`.

A weight-1 covector is some `e_j`. The pattern `off(x e_j^T)` is supported
in column `j`. Let `U_j` be the space of patterns in `P` supported in
column `j`. Patterns in different columns occupy disjoint positions, so
`sum_j dim U_j ≤ dim P = 4`. The hypothesis that every pool covector has
weight 1 says that every pool pattern is a nonzero vector of some `U_j`.
Such a vector has weight at least 2, because `P` contains no matrix unit.
Its lift is `(e_j + v) e_j^T`.

The active columns are those with `U_j ≠ 0`. Each contributes the
coordinate functional `e_j` on `V = V(P)`, and that functional is nonzero
because it pairs to 1 with the image `e_j + v`. The common kernel

```text
K = {z ∈ V : e_j · z = 0 for every active column j}
```

is invariant, since every pool operator is `z ↦ (e_j · z) x`. Some image
pairs to 1 with its covector, so `K ≠ V`. Irreducibility forces `K = 0`.
The active coordinate functionals therefore span the dual of a
four-dimensional space, and at least four of them are linearly
independent. Hence there are at least four active columns. Combined with
`sum_j dim U_j ≤ 4` and `dim U_j ≥ 1` on each active column, there are
exactly four active columns, each of dimension 1, and their sum of
dimensions equals `dim P`. Those four lines are all of `P`.

The witness in Sections 1 through 4 is one pool of this shape, and it is
irreducible. The four lines of Section 5 are another pool of this shape,
and they are reducible. The lemma does not say which of the two behaviors
occurs.

## 7. What this does not claim

The selected κ and its five framework assumptions are unchanged. Nothing
here re-proves the weight-1 image bound of #7138 or the all-width
dimension-4 bound of #7139. Both already allow an irreducible joint image
of dimension 4; #6962 attains it with covector weight 3. The new
statement is the weight-1 case at image dimension 4.

#7094 attains irreducible dimension 5 with a heavier covector. That pool
is outside the weight-1 hypothesis, and this note does not extend it.

Section 6 is not a list of the irreducible four-column pools. The finite
scans in `verify.py` cover one pattern space, widths 4 through 8, and the
67 subspaces of one four-dimensional image. They corroborate the
width-independent casework. They are not a search over all
four-dimensional pattern spaces.

The note produces no rational-address word, native primitive, supplier
admission, or multiplication identity.
