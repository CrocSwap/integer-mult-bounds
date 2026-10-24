# Analytic source-frame and root-support capacities

The full 120 source labels form the one-set of a quadratic function Q on
the affine odd-parity space, parametrized by eight binary coordinates.
Its polar form is nonsingular and its full character sum is positive
sixteen. The checker verifies these facts on all 256 points.

The full source counts in binary frames of ranks zero through nine are
bounded above by

```text
0, 1, 2, 4, 8, 12, 20, 36, 64, 120.
```

The bounds also hold for the retained 112 labels, with the last count
replaced by 112. No large frame enumeration is required.

## Positive character sums on coisotropic slices

Let q be an affine quadratic function with nonsingular polar form in even
dimension n and full character sum positive `2^(n/2)`. Restrict q to an
affine subspace with direction L of dimension t. Its restricted polar
rank s is at least 2t-n. Put `R=L intersection L^perp`.

If s=2t-n, then R has dimension n-t and `L=R^perp`. If the restriction
varies on R, its character sum is zero. Otherwise translate the affine
origin to zero, and choose a symplectic basis with the first n-t e vectors
in R. Their quadratic linear coefficients are zero. The full character
sum over each corresponding e,f pair is two. The restricted sum omits
the f variable and instead sums the e variable, also giving two.
All remaining factors agree. Thus the restricted sum equals the full
positive character sum, rather than its negative.

Consequently this minimum-rank branch has at most half of its points in
the one-set. Every other polar rank is at least 2t-n+2. The general
character-sum magnitude gives at most
`2^(t-1)+2^(t-s/2-1)` ones. For n=8 and t=4,5,6 this gives maxima
12,20,36. At t=7 only the minimum-rank branch is possible, so the maximum
is 64. A binary rank-r frame intersects odd parity in affine dimension
at most r-1. Smaller dimensions have no larger count. This proves the
displayed bounds.

## A rank-seven frame meets a root support in at most 32 ports

Fix any full E8 root port alpha with binary label p. Distinct roots with
nonzero real inner product have binary pairing zero with p. The root's
own label has binary pairing one. Thus the full root-query support is
its own port together with the source labels in `p^perp`. There are 56
labels in that hyperplane. The literal root and binary Gram identity
binds this statement to the current roots.

In the eight affine coordinates, the hyperplane is seven-dimensional.
Its restricted polar rank is six, and its character sum is positive
sixteen. The checker verifies both facts for all 120 choices of p. Its
one-dimensional radical has constant values along it. The quotient is
a nonsingular six-dimensional quadratic function with positive character
sum eight and 28 ones.

An affine subspace of dimension at most five has at most 32 points. For
an affine six-dimensional subspace in this hyperplane, consider its
direction. If it excludes the radical, its projection is an affine copy
of the whole six-dimensional quotient and has 28 ones. If it contains
the radical, its projection is an affine five-dimensional slice. Apply
the coisotropic result above with n=6 and t=5: its maximum is sixteen.
The radical duplicates each point, giving at most 32 ones.

A rank-seven source frame contained in `p^perp` has an odd-parity slice
of dimension at most six. Its root-support intersection is therefore
at most 32. A frame not contained in `p^perp` has an intersection of rank
at most six, with at most twenty nonself source ports. Adding the self
port gives at most 21, still at most 32. A rank-six frame has at most
twenty source ports altogether. Hence the root-support intersection
bounds are twenty and 32 at frame ranks six and seven, respectively.

Restriction to 112 ports can only reduce these counts. An invertible
change of minimal binary factor coordinates preserves frame dimensions
and all counts. These are source-capacity bounds. They do not establish
a physical cost, shared-carrier rule, or supplier improvement.
