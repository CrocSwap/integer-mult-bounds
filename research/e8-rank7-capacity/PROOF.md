# Rank-seven root supports and their equality cases

## Exact model and claims

Use the ordered doubled simple roots `SIMPLE` and fixed frame in the canonical
`research/p112-root-simplex-exclusion/geometry.py`. For each E8 root line r,
write its integral simple-root coordinates c. Its declared label is
`ell(r)=(1,c mod 2)` in F2^9, with leading coordinate the low bit. This is the
same convention as PR3269. It is not a claim about a different physical port
encoding.

Every subset of full E8 labels of binary rank at most seven has at most 36
elements. This is sharp on the fixed P112 obtained by deleting the eight frame
lines. The full 120-line set has exactly 5,440 rank-seven support spaces
attaining 36; exactly 448 of these still attain 36 on the fixed P112.

The capacity proof and equality criterion below are analytic. The counts and
fixed-frame intersection distribution have a complete finite certificate over
10,795 perpendicular two-spaces and four cosets each. These are binary support
claims, with no coefficient-field, shortening, decoder-cost or supplier claim.

## Bind the quadratic space

Let `G_ij=<s_i,s_j>/4` be the integral Cartan Gram matrix. On F2^8 set

```text
q(x) = sum_i x_i + sum_(i<j) G_ij x_i x_j mod 2,
B(x,y) = q(x+y)+q(x)+q(y).
```

The doubled norm identity gives `q(c mod2)=||sum c_i s_i||^2/8 mod2`.
The exact replay checks the distinct 120 root residues against all q=1
vectors, every declared live label, polar rank eight and Gauss sum
`sum_x (-1)^q(x)=256-2*120=+16`. It also checks every polarization pair.
The independent checker reconstructs roots and coordinates separately and
evaluates q through integer norms. Neither checker runs a global flat census
from a predecessor.

A nonempty rank-at-most-seven label support is contained in the leading-one
section of its linear span. Forget the leading bit. This is an affine space
`a+L` of dimension at most six, since the leading-coordinate functional is
nonzero. Extend to dimension six if necessary. It suffices to count q=1
points in an arbitrary affine six-space. A 36-point support has affine span
exactly six, since any affine five-space has only 32 points. Thus its containing
six-space, and its rank-seven label space, are unique.

## Signed character sum and the upper bound

Write `R=L intersect L^perp`, `t=dim R` and `2r=rank(B restricted to L)`.
For `k=dim L`, nondegeneracy gives `t<=8-k`. With
`S=sum_(x in L) (-1)^q(a+x)`, polarization and character cancellation give

```text
S^2 = 2^k sum_(h in R) (-1)^(q(h)+B(a,h)).
```

The exponent is a linear functional on R. If nonzero then S=0; otherwise
`|S|=2^(k-r)`. For k=6, only polar ranks four and six are possible.

At rank four, t=2 and `L=R^perp`. If the radical character is nonzero, S=0.
If it vanishes, let `q_a(x)=q(x)+B(a,x)`. On every coset of R outside
`R^perp`, the sum of `(-1)^q_a` vanishes. Hence the sum over all F2^8 equals
the sum over L. Translating q by a and multiplying by `(-1)^q(a)` shows
`S=+16`. The number of ones is therefore 32 or 24, never 40.

At rank six the radical is zero and `|S|=8`. The number of ones is 28 or 36.
These cases prove the uniform bound. Retaining the positive ambient sign is
necessary: the controls exhibit a nondegenerate minus-type form with an affine
six-space containing 40 ones.

## Complete equality criterion

Equality requires L nondegenerate. Its perpendicular U is a nondegenerate
two-space and `F2^8=L direct_sum U`. There is a unique b in U such that
`a+L=b+L`. Let `g_U=sum_(u in U) (-1)^q(u)`, which is +2 or -2.
Multiplicativity of the Gauss sum on the orthogonal direct sum gives
`g_L*g_U=16`, so

```text
S_(b+L) = (-1)^q(b) * 16/g_U.
```

It equals -8 exactly when `(-1)^q(b)*g_U=-2`.
If g_U=+2, b is U's unique anisotropic vector. If g_U=-2, b is zero, U's
unique isotropic vector. Thus every nondegenerate U supplies exactly one
36-root affine section, and every equality section arises this way.

There are `255*128/6=5440` such U. Each nonzero u has 128 choices v with
`B(u,v)=1`. Every plane has six ordered bases. Uniqueness of affine span
prevents two such sections from defining the same 36-root support.

For any support space of dimension below seven, equality is impossible. For a
rank-seven space W, equality holds exactly when its affine section satisfies
this criterion. On P112 it additionally requires that section to avoid every
deleted frame root. This is a necessary and sufficient classification, rather
than just a list of maximizing examples.

## Fixed frame and complete finite count

Enumerate every two-space U once as the sorted triple of its nonzero vectors.
There are `(255*254)/6=10795`. Since B is nonsingular, its two independent
pairing equations have four affine solution sets of size 64, exhausting all
affine six-spaces. The primary checker uses these polar equations. The
independent checker enumerates ordinary-dot two-row RREF annihilators instead.
Both reconstruct every full/live count and the same digest of all equality
support lists.

Among the 5,440 full equality sections, the numbers of deleted frame roots are:

```text
deleted frame roots     0      2      4     8
number of sections    448   3584   1344    64
```

Only the first group remains of size 36. No nonmaximal full section can become
an equality section after deletion. `RESULT.json` also records all section
types, a literal 36-label fixed-P112 witness and its two-plane/coset descriptor.
The witness's binary rank is checked as seven. Full arithmetic runs over a
fixed finite domain; there is no solver or floating-point inference.

## Scope and credit

PR3269, Nick Petalas at `ebe02d33157dc6c6d3b35df204e4a39242b7429e`, proves the
earlier rank-five/six capacities and supplies the signed quadratic method.
The current contribution extends the method to rank seven and classifies
equality and actual frame survival. It does not claim the numerical capacity
was previously unknown, replace the earlier proofs, or assert an actual
remaining TWOSIDE caller. PR3154, DreamingOfClouds at
`708f0ad8928c383de8294aea3c126e9461d2066d`, supplies the reduction context.
Canonical geometry retains the PR3161/3162, joaqcoo and E8/P112 lineage.
Neither pending PR is an executable dependency. Apache-2.0.
