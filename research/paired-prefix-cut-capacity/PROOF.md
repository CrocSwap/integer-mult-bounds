# Sharp capacity change for a paired scalar ADD at a cut

This proof was produced by Nick Petalas. New work is Apache-2.0.

## Contract and statement

Let D=Z[1/2]. Use the saturated helper-cut interface of Ali Romman's
PR5615. There are finitely many independent dirty scalar fields. A and B
are invertible matrices over D. Their complete endpoint BA is identity
on the helper support G and is an invertible map on its complement.
Keep the eligible coordinate support F, helper support G, and endpoint
BA fixed. There is no live owned field at the cut.

The eligible row and column modules are

```text
L(A) = {v supported in F : v A is supported in G},
R(B) = {u supported in F : B u is supported in G}.
```

Pair full D-module bases by ordinary row-column multiplication. Let
c(A,B;F,G) be the largest size of a dyadic identity block obtainable by
left and right combinations of that pairing. The credited PR5615
Smith theorem gives

```text
c(K) = min_(odd primes p) rank_(F_p)(K mod p).
```

The minimum is attained. This includes a full-unit or empty pairing.
No predecessor capacity computation is needed for the result below.

An elementary update x_i += a x_j, i != j and nonzero a in D, has matrix
T=I+a e_i e_j^t and inverse T^-1=I-a e_i e_j^t. Change the prefix and
suffix to

```text
A' = T A,       B' = B T^-1.
```

The inserted update is immediately before the nominated cut and its
inverse immediately after it, in these physical coordinates. The entire
dirty endpoint stays B'A'=BA. Then

```text
|c(A',B';F,G) - c(A,B;F,G)| <= 1    if exactly one of i,j belongs to F,
c(A',B';F,G) = c(A,B;F,G)           otherwise.
```

Both signs of the one-channel difference occur. For any finite sequence
of such paired edits, its total capacity change in absolute value is at
most the number of crossing updates in the prefix-side edit sequence.
That sequence bound is attained for every nonnegative integer count.

The result concerns scalar elementary updates adjacent to a fixed cut.
An update inserted earlier inside a prefix becomes a generally dense
conjugate at the cut and is outside this elementary-update statement.

## A one-row or one-column comparison

Suppose a full pairing C gains at most one row to form K. Every old unit
block remains available by extending its row coefficients by zero, so
c(C)<=c(K). Choose an odd prime p attaining c(C). Adding a row raises
rank modulo p by at most one. Hence

```text
c(C) <= c(K) <= c(C)+1.
```

The same argument applies to a column. This is a use of the credited
Smith criterion and ordinary rank subadditivity, not a new Smith theorem.

## An update crossing out of the cut

First suppose i belongs to F and j does not. For every column u supported
in F, u_j=0, so T^-1 u=u. Consequently R(B')=R(B).

For a row v supported in F, v T=v+a v_i e_j^t. In particular v T=v
whenever v_i=0. Therefore the two left modules have exactly the same
coordinate-zero submodule

```text
L0 = L(A) intersect {v_i=0} = L(A') intersect {v_i=0}.
```

The coordinate map v -> v_i identifies each quotient L(A)/L0 and
L(A')/L0 with a submodule of D. Such a submodule is free of rank at most
one, since D is a PID. The quotients are finitely generated, and their
short exact sequences split. A full basis of L0 therefore extends to a
full basis of either left module by at most one row.

Pair these bases with one fixed full basis of R(B). The two pairing
matrices extend a common matrix C by at most one row each. By the
preceding comparison, both capacities belong to {c(C),c(C)+1}. Their
difference has absolute value at most one. This uses full saturated
modules; merely counting rational kernel dimensions would not suffice.

## An update crossing into the cut

Suppose i is outside F and j belongs to F. Every supported row v has
v_i=0, so v T=v and L(A')=L(A). On supported columns satisfying u_j=0,
T^-1 u=u. The common right submodule is thus

```text
R0 = R(B) intersect {u_j=0} = R(B') intersect {u_j=0}.
```

Both right modules extend R0 by at most one basis column. The identical
one-column comparison proves the result in this orientation.

## Updates within one side

If i and j both belong to F, multiplication by T and T^-1 preserves the
row and column coordinate modules supported in F. Exactly

```text
L(A') = L(A) T^-1,        R(B') = T R(B).
```

Transport any two full bases accordingly. Their pairing is unchanged,
because (v T^-1)(T u)=v u. If both indices are outside F, T acts as the
identity on every supported row and column, so both modules themselves
are unchanged. These two cases prove invariance. Summing the per-edit
absolute differences proves the finite-sequence bound.

## Sharpness with every dirty field restored

Take two arbitrary fields x,z and F=G={x}. Use prefix x += z and its
inverse suffix x -= z. Thus

```text
A = [[1,1],[0,1]],     B = [[1,-1],[0,1]].
```

The left eligibility equation is v_x=0, so L=0 and the old capacity is
zero. Insert x -= z immediately before the cut and x += z immediately
after it. Now A'=B'=I_2. Both eligible modules have basis e_x and pair
to [1], so the new capacity is one. The complete chronological word is

```text
x += z;  x -= z;  CUT;  x += z;  x -= z.
```

It restores both arbitrary dirty inputs, and the x value at the new cut
is exactly its independent input value. Reversing the edit gives the
negative difference. For d disjoint pairs, take F=G to consist of every
x field. The original left constraint matrix is I_d, giving capacity
zero. All d paired edits give A'=B'=I_(2d), hence capacity d. There are
d crossing prefix-side updates, d matched suffix updates, 2d original
scalar updates and 4d total scalar updates in the edited identity word.
No extra storage is allocated. This proves sharpness for every d; it is
not a source-bound native construction or productive Gaussian invoice.

## Exact finite corroboration

The new verifier constructs fresh small prefixes and computes their full
eligible modules. It imports no predecessor executable. For at most three
coordinates, row reduction determines rational constraint rank. A rank-one
kernel is its primitive integral cross product or perpendicular vector.
For a single primitive constraint (a,b,c), write sa+tb=g=gcd(a,b) and
h=gcd(g,c). When g is nonzero the complete integer kernel has basis

```text
(b/g,-a/g,0),    (-sc/h,-tc/h,g/h).
```

Indeed the constraint forces z to be a multiple of g/h. Subtract the
corresponding multiple of the second vector; every remaining solution
has z=0 and is an integer multiple of the first vector. The g=0 case
has basis e_0,e_1. Localizing these full integer kernels at two gives
the full D-kernels, since a dyadic solution can have its denominator
cleared by a power of two. Thus no nonsaturated rational basis is
substituted for a module basis.

The capacity oracle enumerates all minors and their integer gcds after
clearing dyadic denominators. A k-minor ideal is the whole dyadic ring
exactly when its nonzero integer gcd is a power of two. This is the
determinantal-divisor form of the cited criterion. Literal scalar
updates separately check the sharp family on arbitrary signed small
dirty states. The finite checks corroborate the universal written
argument; they do not prove it by extrapolation.

## Scope and credit

zxv's PR6064 posed the changed-prefix opening after proving the sharp
two-per-added-coordinate bound for fixed prefixes. Here the supports
are fixed and the program changes by paired elementary updates. Ali
Romman's PR5615 supplies saturated module capacity, with PR5602/5611/5599
and the retained P104/native/controller lineage. Coordinate kernels,
module splitting over a PID, rank bounds and Bezout identities are
classical. No claim of general literature priority is made for them.

No physical chart, timing, native-map, delivery, productive-target,
precision, storage, ownership, compiler or complete supplier cost is
established. A scalar ADD is not a recursive paid child. This theorem
does not imply a kappa ceiling or improve kappa. All five selected
framework assumptions retain their status. Independent human and
formal proof-kernel review are unclaimed.
