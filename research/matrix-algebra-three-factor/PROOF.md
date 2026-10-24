# Three factors for every full-matrix-algebra target

Let K be any field, let m>=1, and put R=M_m(K). There are two data
roles. A paid factor is I+u y^T, with u in R^2 and y in K^2.
Arbitrary GL_2(K) maps are free, including maps at either endpoint.
The cost of a target M in M_2(R) is the least number of paid factors.
Ordinary rank below is rank on K^(2m).

## Theorem

Every target M has cost at most three. This includes every singular
target, with no ordinary-rank restriction. More precisely, after possibly
swapping its two block rows and its two block columns, M has a factorization

```text
N = [I  0] [I  B] [E  0]
    [b  I] [0  d] [F  I].
```

The right vectors of these three paid factors are e1,e2,e1. No auxiliary
roles are used. The bound is sharp for every m>=2 and every field.

This extends the invertible semilocal theorem of Nick Petalas #4749 to all
targets over a single full matrix algebra. It resolves the full-matrix-algebra
case of the three-factor question in Nick Petalas #4276. The all-algebra
version is false by #4763's polynomial example. No theorem for singular
radical extensions or products of matrix algebras is asserted here.

## A classical subspace lemma

Let V and Z be subspaces of a finite-dimensional space W, with
dim(Z)<=dim(V). Then there is a complement U to V in W such that
U intersects Z only at zero.

Here is a constructive proof, including the binary field. Start with U=0.
If dim(U)<dim(W)-dim(V), both V+U and Z+U are proper subspaces of W.
Their union cannot be W. To see this, choose x outside V+U. If x is outside
Z+U, use x. Otherwise choose y outside Z+U. If y is outside V+U, use y.
In the remaining case x+y is outside both subspaces. Adjoin that vector to
U. Both intersections remain zero. Repeat exactly dim(W)-dim(V) times.
The resulting U is the required complement.

## Choosing the row and column

Write r=rank(M). The ranks of its two block rows sum to at least r,
as do the ranks of its two block columns. Choose a block row of rank
at least r/2 and a block column of rank at least r/2. Independent free
block swaps put the selected row first and the selected column second.
Write the transformed matrix as

```text
N = [A B]
    [C D].
```

Let W=im(N), V=im([B;D]), and let pi be projection onto the first K^m
output block. Set Z=W intersect ker(pi). Then

```text
dim(Z) = r - rank([A B]) <= rank([B;D]) = dim(V).
```

The lemma supplies W=U direct-sum V with U intersect ker(pi)=0.

## Lifting the complement to a graph

Let E2=0 direct-sum K^m in the input. Since N(E2)=V and W=U+V,
the preimage N^(-1)(U) surjects onto K^(2m)/E2. Choose a linear section
of that surjection. Its image L is a complement to E2 contained in
N^(-1)(U), so L is the graph of a map -F:K^m -> K^m.
Equivalently, for each standard input column, solve

```text
[B;D] F + U X = [A;C].
```

These equations are solvable because U+V=W. Thus

```text
N [I;-F] = [A-BF; C-DF]
```

has image inside U. Projection pi is injective on U, so
ker(A-BF) is contained in ker(C-DF). A linear map on im(A-BF) therefore
sends (A-BF)x to (C-DF)x. Extend it to K^m and call the extension b.
We obtain

```text
C-DF = b(A-BF).
```

Define E=A-BF and d=D-bB. Direct multiplication now gives

```text
[I 0] [I B] [E 0] = [E+BF      B] = [A B].
[b I] [0 d] [F I]   [bE+DF     D]   [C D]
```

The factors equal I+(0,b)^T e1^T, I+(B,d-I)^T e2^T, and
I+(E-I,F)^T e1^T. Their left coefficients belong to R; their right
vectors belong to K^2. Undoing the free block swaps proves the theorem.
The zero target is included. One may take b=F=0, E=d=0 in that case.

## Sharpness and exact cost decision

For m>=2, take the identity on K^(2m) and transpose coordinates 1 and
m+2, leaving every other coordinate fixed. On the first two internal
coordinates its four blocks are

```text
A=E22, B=E12, C=E21, D=E11.
```

The other m-2 internal coordinates carry a two-role identity.
For every nonzero scalar block row phi, the compressed row (phi tensor I)M
has rank m, because M is invertible. For every nonzero scalar input t,
the further compression on the first two internal coordinates is

```text
[phi2*t2  phi1*t2]
[phi2*t1  phi1*t1],
```

of rank one. On the remaining coordinates it is the scalar
phi1*t1+phi2*t2 times I_(m-2). Its total rank is at most m-1.
The cited two-factor criterion of #4276 therefore excludes cost at most
two. The new construction supplies three, proving sharpness. The m=2
example is already the sharp predecessor example; its extension and the
universal upper bound are included to state the theorem's full range.

Together with #4276's one/two-factor criteria, the upper bound decides
every cost. Define delta(M)=min over T in GL_2(K) of dim_K((MT-I)K^2).
Then cost is delta if delta<=1, is two if delta=2 and some nonzero scalar
phi,t satisfy

```text
rank((phi tensor I)M) = rank((phi tensor I)M(t tensor I)),
```

and is three otherwise. These low-factor criteria are cited predecessor
theorems, not new claims of this package. For m=1 all targets already cost
at most two. For m>=2 the maximum is exactly three.

## Scope and credit

The universal statement is a written scoped algebraic proof. The finite
verifier corroborates the new constructor, not every field or block size.
No physical cost for coefficient preparation, overwriting, restoration,
routing, frames, precision or stock is supplied. No new kappa, native
supplier or complete multiplication theorem follows.

This contribution was produced by Nick Petalas. Nick Petalas #4276
supplies the exact one/two-factor criteria; #4749 supplies the invertible
comparison; #4265/#4243 supply the cost question and free-map framework.
ToikY #4334 supplies the related field-product three-factor construction.
Wentao Li #4099, following #2513, supplies the alphabet and column bound.
The subspace-complement lemma, rank inequalities, linear sections and
extension of a linear map are classical linear algebra. The new result is
their stated all-target restricted-alphabet consequence. Apache-2.0.
