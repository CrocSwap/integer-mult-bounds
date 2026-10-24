# Reciprocal responses with two correction coordinates

The six-mode transfer family admits an integer unit E such that E and
E^-1 have zero diagonal and rank(E-I)=2. A symmetric rational response
with these two diagonal conditions cannot attain rank two. Thus the
change from a symmetric response to a reciprocal pair reduces the
number of correction coordinates from three to two per centre vertex.

This is a response theorem for the actual pair-mode family. It does not
give a cheap terminal decoder. The native phases, complete 112-port
response, routed controller, and final cost require separate checks.

## An integer construction in every dimension at least three

Let n>=3, put m=n-2, and write an input as (a,b,c), where a has m
coordinates. Write s for the sum of the coordinates of a. Define

```text
E(a,b,c)    = (a-s*1+b*1, c, -(m-2)*s+(m-1)*b),
E^-1(a,b,c) = (a-s*1+c*1, -(m-2)*s+(m-1)*c, b).
```

All coefficients are integers. Both displayed matrices have zero
diagonal. Their two products are I.

A short factorization proves invertibility and the correction rank.
Let P exchange b and c. Define the column u and row l by

```text
u = (1,...,1,m-2,0)^T,
l = (-1,...,-1,1,0).
```

Then l*u=-2, so R=I+u*l satisfies R^2=I. Direct substitution gives
E=P*R and E^-1=R*P. Each factor has determinant -1. Thus det(E)=1.
The factor R changes only the one scalar l*x. This factorization does
not assert that R or P alone has a legal native transfer schedule.

An explicit factorization of the complete correction is

```text
E-I = U V,

U = [ 1  0 ] repeated m times,
    [ 0  1 ],
    [ m-2 -1 ],

V = [ -1 ... -1   1  0 ],
    [  0 ...  0  -1  1 ].
```

Both U and V have rank two, and

```text
I_2+VU = [[1-m,1],[m-2,-1]]
```

has determinant one. The two nonzero rows of V and the first and
(m+1)-st rows of U show that rank(E-I)=2. Also
E^-1-I=-E^-1(E-I), so rank(E^-1-I)=2. The fixed space has dimension
n-2 and is given by s=b=c. In particular, for n=6 each response fixes
four dimensions.

## Two correction coordinates are necessary

Work over a field of characteristic zero. Suppose A is an invertible
n by n matrix, and both A and A^-1 have zero diagonal. Rank(A-I)
cannot be zero. If it is one, write A=I+u*v. Each diagonal equation
gives u_i*v_i=-1, so v*u=-n. The rank-one inverse formula gives

```text
A^-1 = I-u*v/(1-n).
```

Every diagonal entry of this inverse is (n-2)/(n-1). It is nonzero
for n>=3. This is a contradiction. The construction therefore attains
the minimum correction rank in this matrix family.

The statement is about rank(A-I). It is not a lower bound on native
children, storage, or the cost of a routed code.

## Symmetry forces a third correction coordinate in dimension six

Suppose A is a symmetric rational six by six unit, with both A and
A^-1 of zero diagonal. Assume rank(A-I)=2. Symmetry gives an
orthogonal eigenbasis. Four eigenvalues are one. Let the other two
be a and b. The two trace equations give

```text
a+b=-4,       1/a+1/b=-4,
ab=1,        {a,b}={-2+sqrt(3),-2-sqrt(3)}.
```

Let u and v be unit eigenvectors for a and b. At coordinate i, the
two diagonal equations are

```text
1+(a-1)*u_i^2+(b-1)*v_i^2=0,
1+(b-1)*u_i^2+(a-1)*v_i^2=0.
```

Their difference gives u_i^2=v_i^2, and either equation then gives
u_i^2=v_i^2=1/6. Hence u=sigma/sqrt(6) and v=tau/sqrt(6), where
sigma and tau are sign vectors. The spectral formula is

```text
A = I - (sigma*sigma^T+tau*tau^T)/2
      + sqrt(3)*(sigma*sigma^T-tau*tau^T)/6.
```

Rationality forces the coefficient of sqrt(3) to be zero. The two
rank-one projectors are then equal, which contradicts u perpendicular
to v. Thus the correction rank is at least three. Three disjoint
coordinate exchanges attain it. The symmetric matching response is
optimal under these hypotheses; an asymmetric reciprocal pair escapes
that restriction.

The proof uses real symmetry and rational entries. It does not assert
the same conclusion for complex symmetric matrices, or for a matrix
whose inverse has a nonzero diagonal.

## Binding to the actual 48 pair modes

The pinned cyclic family has eight vertices with six pair modes at
each vertex. Let A_pair be its signed pair code. It satisfies
A_pair*A_pair^T=2I. Put one copy of E_6 on each vertex and set

```text
B = direct_sum_v E_6,
E_physical = A_pair^-1 B A_pair.
```

Both B and B^-1 have zero diagonal, so both belong to the proved
cyclic transfer family. The backward transfer convention produces the
negative transpose of its coefficient matrix. Therefore the native
generator for a reciprocal backward response must use B^-T.

The physical response has determinant one and
rank(E_physical-I)=16. Its inverse has the same correction rank.
The corresponding symmetric matching has correction rank 24 on these
48 ports. Conjugation by the invertible pair code preserves each rank.
The checker verifies both full 48 by 48 inverse orders and both ranks
from the literal pinned pair code.

The rank-two coordinates depend on five modes at each vertex. The
rank-one reflection R uses four a modes and the b mode. Their actual
source planes span six binary directions, including the common
radical. A proposed capture to that radical would have rank five.
This observation is not a capture implementation: the permutation P
has fixed modes, and R has nonzero diagonal. Neither factor alone
belongs to the zero-diagonal transfer family.

The cyclic family proves logical transfers and nested frame access.
Its fixed path gives native mass 1792 on all 224 data fields, with
zero response on the other 64 ports in that family packet. This
theorem does not supply a compatible 64-port unit or a full native
phase replay. The two-coordinate factorization must not be treated
as free physical access at a hole frame.

## Checks and continuation

Run the adjacent checker in normal and optimized Python modes. It
checks dimensions three through sixteen, the exact factors, both
inverse orders, the rank-two factor, the fixed space, and the pinned
48-port application. The proof above covers all n>=3; the finite
checks do not replace that proof.

Next steps are native phase lowering of the actual reciprocal pair,
selection of a compatible ordinary 64-port response, and a costed
capture or terminal scheme that uses the smaller correction space.
The general one-pair controller can also use an arbitrary unit raw
backward response through legal current-stage codes. That result
removes reciprocal native synthesis as a prerequisite, but leaves
the physical output code explicit.

This result builds on the root pair geometry, the oblique-native
pair-code construction, and the independent-review cyclic flag
theorem. OpenAI Codex assisted the work. No PR or publication is
authorized. Before any PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
