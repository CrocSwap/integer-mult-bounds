# Quadratic ranks of the two E7 receipt representatives

The selected conditional value stays `363005817/100000000000`. This note does
not enumerate kernel words and does not change that value.

## Data

Let the 63 roots and 135 orthogonal frames be the lists returned by
`intrinsic_e7` and `orthogonal_frames` in the pinned PR #5238 geometry,
`research/e7-bitsliced-exhaustion/source/vendor/PR5238.py`. The two quadratic
forms are the functions `form_a` and `form_b` in
`research/e7-bitsliced-exhaustion/source/verify.py`:

```text
Q_a(x) = x0^2 + x1^2 + x2^2 + x3^2 - x4^2 - x5^2 - x6^2 - x7^2
Q_b(x) = (x0 - x1)(x2 - x3)
```

Write `β_Q(u, v) = (Q(u + v) - Q(u) - Q(v)) / 2`. The pinned
`quadratic_matrix` evaluates `β_Q` on the ordered slice

```text
e1, e2, e3, e5, e6, e7, w = (1, 0, 0, 0, -1, 0, 0, 0).
```

## Theorem

On this slice, `β_{Q_a}` has matrix `diag(1, 1, 1, -1, -1, -1, 0)` and rank 6.
`β_{Q_b}` has rank 2. The omission statement is separate and uses one exact
elimination, recorded below. These supports, evaluation lists and quadratic
ranks are the two `representative_*` and `quadratic_rank` fields of
`research/e7-bitsliced-exhaustion/source/RESULT.json`.

## Polarization

For `Q_a`, `β_{Q_a}(u, v) = u0 v0 + u1 v1 + u2 v2 + u3 v3 - u4 v4 - u5 v5 - u6 v6 - u7 v7`.
The six unit vectors are pairwise orthogonal, with signs `+1` on `e1, e2, e3`
and `-1` on `e5, e6, e7`. The vector `w` meets none of those six coordinates,
and `β_{Q_a}(w, w) = 1 - 1 = 0`. The matrix is therefore diagonal of rank 6.
Its first six diagonal entries sum to 0, which is the restricted trace checked
by `quadratic_matrix`.

For `Q_b`, set `L1(x) = x0 - x1` and `L2(x) = x2 - x3`. Then
`β_{Q_b}(u, v) = (L1(u) L2(v) + L1(v) L2(u)) / 2`. Both linear forms vanish
on `e5, e6, e7`, so those three rows are zero. Also `L1(w) = 1`, `L2(w) = 0`,
`L1(e1) = -1` and `L2(e1) = 0`, so `β_{Q_b}(w, v) = L2(v) / 2 = -β_{Q_b}(e1, v)`.
Likewise `L2(e3) = -L2(e2)` and `L1(e2) = L1(e3) = 0`, so the `e3` row is the
negative of the `e2` row. The remaining two rows are

```text
β(e1, ·) = (0, -1/2, 1/2, 0, 0, 0, 0)
β(e2, ·) = (-1/2, 0, 0, 0, 0, 0, 1/2)
```

They are independent: one has a nonzero `e2` coordinate where the other is
zero. The matrix therefore has rank 2. Every diagonal entry is 0, so the
restricted trace is 0.

## One dependence among the twelve columns

**Lemma.** Let `A` be a matrix over `Q` with `n` columns and rank `n - 1`,
and suppose some kernel vector has every coordinate nonzero. Deleting any
one column leaves rank `n - 1`.

The column map `Q^n -> Q^{rows}` has one-dimensional kernel. A dependence
among the columns that remain after deleting column `j` would be a kernel
vector with a zero in position `j`. Every kernel vector is a multiple of the
given one, and that coordinate is nonzero, so no such dependence exists.
The remaining `n - 1` columns are independent.

The verifier sums `Q_a` and `Q_b` on all 135 frames and gets 0. That sum is
an exhaustive check of this frame list, not a hand identity for a general
root system. Zeros off the 12-root support do not contribute, so the
support-values vector lies in the kernel of the indicator matrix. Dividing
by 8 and by 4 clears those values to

```text
(-1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1)
(1, -1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1)
```

Exact rational elimination, in `verify.py`, shows that each indicator matrix
has rank 11 and a one-dimensional kernel equal to the displayed vector.
Those two facts are a finite certificate for these two matrices. They are
not expanded by hand. Every displayed coordinate is nonzero, so the lemma
gives rank 11 after every single deletion. The verifier also row-reduces
each of the 24 deleted matrices directly.

## What this does not prove

The two orbit sizes 630 and 1008, the reflection hashes, and the statement
that every other weight-12 word has one of these ranks are not recomputed.
Neither is a `2^27` codeword census. The five selected framework assumptions
stay assumptions. No new `κ` is claimed.
