# Independent review of the reciprocal rank-two response

The response theorem passes. The construction is an integer unit in each
dimension n at least three. Both the response and its inverse have zero
diagonal. Each differs from the identity by rank two, which is the least
possible rank under these hypotheses. The literal 48-port pair code gives
rank 16 in each direction.

The frozen proof has one wording defect about query support. Its addendum
corrects that defect. The first correction coordinate uses five modes;
the second uses two; their union uses all six. Only the first coordinate
has the stated proposed rank-five capture to the common radical. No
capture implementation or price follows from this observation.

This review covers exact response algebra, the pair-coordinate binding,
and the balanced response in the addendum. It does not cover new native
phases, a response on the other 64 ports, a controller, a terminal decoder,
or the complete recursive cost.

## Independent derivation

Put m=n-2. Let P exchange the final two coordinates. Let
u=(1,...,1,m-2,0) and l=(-1,...,-1,1,0). Their product l*u is -2.
Thus R=I+u*l is an involution:

```text
R² = I + (2+l*u)u*l = I.
```

R has eigenvalue -1 on u and is the identity on the kernel of l. Its
determinant is -1. Since det(P)=-1, E=P*R has determinant one, with inverse
R*P. Direct action on a basis vector gives the two displayed formulas in
the producer proof. This also proves their zero diagonals.

For the displayed E-I=UV factor, U is injective and V is onto its
two-dimensional range: their indicated two by two minors are units.
Therefore rank(UV)=2. This uses the injectivity of U, not just the separate
rank statements. Also E^-1-I=-E^-1(E-I), so the inverse has the same
correction rank. The equation Vx=0 is exactly sum(a)=b=c.

For the lower bound, rank zero contradicts a zero diagonal. In rank one,
A=I+u*v and u_i*v_i=-1 for each i. Therefore v*u=-n. The inverse formula
has denominator 1-n, which is nonzero in characteristic zero. Its
diagonal is (n-2)/(n-1), which is nonzero for n at least three. The
dimension and characteristic hypotheses matter. The two-dimensional
coordinate exchange has correction rank one and is its own inverse.

No commutation between P and R is used. In fact E is not an involution
in dimension six. Replacing the inverse by E fails the exact check.

## The symmetry restriction

The producer's six-dimensional proof is valid. A stronger statement also
holds: for every integer n at least five, a symmetric rational unit with
zero diagonal and zero-diagonal inverse cannot have rank(A-I)=2.

To prove it, diagonalize A over the reals. There are n-2 eigenvalues equal
to one and two other eigenvalues a,b. The two trace equations give

```text
a+b=-(n-2),       1/a+1/b=-(n-2),       ab=1.
```

For n at least five the two eigenvalues are distinct and real. Their
difference is sqrt(n(n-4)). Let u,v be their orthonormal eigenvectors.
The diagonal equations for A and A^-1 have the coefficients of u_i²
and v_i² exchanged. Their difference gives u_i²=v_i². Either equation
then gives u_i²=v_i²=1/n. Write u=sigma/sqrt(n) and v=tau/sqrt(n), where
sigma,tau are sign vectors. The spectral formula is

```text
A = I - (sigma*sigma^T+tau*tau^T)/2
      + sqrt(n(n-4)) (sigma*sigma^T-tau*tau^T)/(2n).
```

For every n at least five,

```text
(n-3)² < n(n-4) < (n-2)².
```

The left difference is 2n-9, and the right difference is 4. Thus the
square root is irrational. Rational entries of A force the last
coefficient matrix to vanish. The two rank-one projectors would then
be equal, in conflict with u perpendicular to v. This proves the claim.
For odd n, orthogonality of the two sign vectors already fails over
the reals.

This extension gives a lower bound of three, not a claim of attainment
in every dimension. In dimension six, three disjoint exchanges attain
rank three. The rational premise is necessary: with n=6, sigma all
positive, and tau=(1,1,1,-1,-1,-1), the displayed formula gives a real
symmetric rank-two example over Q(sqrt(3)). The checker verifies its
zero diagonals and both inverse orders with exact pairs of rationals.

## Actual pair coordinates and orientation

The review pins the cyclic-family payload and checks its two partitions:
24 signed physical pairs and eight six-mode vertex lists. It applies
each pair code to a physical basis column, applies P and R directly to
each vertex's six values, and applies the inverse pair code. It does
not import the producer or multiply the producer's response matrices.

All 48 forward columns and all 48 inverse columns equal the frozen
producer matrices. Both composition orders are the identity. The two
physical determinants are one; both correction ranks are 16; both
physical diagonals are zero. The checker also verifies the actual
binary query-plane dimensions. They are six for the first query,
three for the second query, and seven for their combined support,
including the common radical in each case.

The cyclic transfer family requires zero diagonal in the mode matrix.
Both E and E^-1 meet this condition. The backward transfer computes the
negative transpose of its mode matrix. A reciprocal backward response
therefore uses E^-T as its generator. The pair code satisfies AA^T=2I,
which gives A^-1 B^T A=(A^-1 B A)^T. This is the required compatibility
with the physical transpose. It does not move a matrix through a C_q
chart. The physical inverse is not symmetric, so omitting the transpose
would change the required map.

The rank reduction is a response-space result. A scalar rank-two factor
does not grant access to the two values at a hole frame. The reflection
and the coordinate exchange each have nonzero diagonal entries, so they
cannot each be substituted into the zero-diagonal transfer schedule.

## Balanced response

The addendum's conjugation D^-1 E D, with
D=diag(1,1,1,1,-2,2), gives its two stated formulas. Both are integer
units; both have correction rank two and zero diagonal. The maximum
absolute row sums fall from 11 to 7 in each direction. The four by four
a-to-a block stays unchanged.

The independent coefficient invoice is 188 real scalar primitives per
six-mode transfer in either direction, before and after this change.
This is the sum of the cyclic family's stated ADD tariffs. It is not a
complete native invoice. In particular, it does not price the pair
codes, source access, frame changes, or a terminal. The row-sum bound is
a bound on this matrix, not on all prefixes or a recursive child's state.

## Reproduction and scope

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/reciprocal-rank-two-review-20261020/check_review.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/reciprocal-rank-two-review-20261020/check_review.py
```

Expected output starts with `PASS_INDEPENDENT_RECIPROCAL_RANK_TWO`.
The receipt must be byte-identical in the two modes. The checker verifies
the source hashes before it uses any data. Its arithmetic uses exact
integers and fractions. Finite checks in dimensions 3 through 32 support
the all-dimension derivation above; they do not replace it.

Controls reject a changed reflection coefficient, the use of E as its
inverse, and an omitted pair undo. The checker also distinguishes the
inverse from its transpose, the excluded n=2 case, and the real
nonrational symmetric example. No producer code is imported.

The root lane supplied the reciprocal response and its balanced form.
The cyclic family supplies the actual coordinate system and transfer
condition. This lane supplied a separate derivation, column check,
support correction, and the symmetry extension. OpenAI Codex assisted
this work. No PR, push, or publication is authorized. Before any PR
description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
