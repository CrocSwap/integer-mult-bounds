# Exact scalar-pivot dimension

This proof was produced by Nick Petalas. Apache-2.0.

Let K be any field, let lambda be nonzero, and prescribe h in K. Among
commuting idempotents P,Q on K^n with P11=Q11=lambda and (PQ)11=h, let
N(lambda,h) be the least n for which their one-coordinate Schur complements
have commutator rank two. Then

```text
                    4 + [1-2lambda != 0],  h=0,
N(lambda,h) =       5 + [lambda != 1],     h=lambda,
                    3 + [1-2lambda+h != 0], otherwise.
```

The brackets denote the indicator of a field inequality. The first two cases
are disjoint because lambda is nonzero. Every minimum is attained. Matrices
need not be symmetric. This is a scalar-pivot theorem, not a theorem about a
prescribed matrix product for a larger deleted block.

## Sector compression

Put U=K, V=K^n. Let i:U -> V be coordinate inclusion and pi:V -> U the
coordinate projection. Since pi i=1, V=i(U) direct-sum ker pi.
The four joint eigenspace projectors are

```text
E00=(I-P)(I-Q), E10=P(I-Q), E01=(I-P)Q, E11=PQ.
```

These mutually annihilating projectors sum to I in every characteristic. Set
Vj=im Ej, rj=dim Vj, Yj=Ej i and Xj=pi restricted to Vj. Their products are

```text
t00=X00 Y00=1-2lambda+h,
t10=X10 Y10=lambda-h,
t01=X01 Y01=lambda-h,
t11=X11 Y11=h.                                      (1)
```

They sum to 1. Conversely, any such four pairs of maps with these products
give pi i=1. Equip their direct sum with diagonal P0,Q0 having eigenvalues
00,10,01,11. Complete i to a basis [i N], with N a basis of ker pi.
Conjugation into this basis gives commuting idempotents with exactly the
required coordinate pivots and leading product. This standard sector
construction is the predecessor method of ssafwann's #4671 and Nick Petalas's
#4746. The products and sharpness conditions below change with lambda.

## Rank-two criterion

Use the scalar factorization from Nick Petalas's #4278, with equal pivots
lambda. Its ambient factors are

```text
A = [PQ i - (h/lambda)Q i, (P-Q)i/lambda] : K^2 -> V,
B = [pi(P-Q)/lambda; -pi PQ + (h/lambda)pi Q] : V -> K^2.
```

They satisfy pi A=0 and Bi=0. The Schur commutator is the product of A's
coordinates in ker pi and B's restriction to ker pi. Therefore it has rank
two exactly when A has rank two and B has rank two. Indeed, a rank-two A is
injective and a rank-two B is onto. The identity Bi=0 and the displayed direct
sum imply that B restricted to ker pi is still onto.

For each sector, A is Yj times the following row, and B is the following
column times Xj:

```text
sector     row for A                         column for B
00         (0,0)                             (0,0)^T
10         (0,1/lambda)                      (1/lambda,0)^T
01         (-h/lambda,-1/lambda)             (-1/lambda,h/lambda)^T
11         ((lambda-h)/lambda,0)             (0,-(lambda-h)/lambda)^T
```

Since the sectors form a direct sum, rank A is the span dimension of the
listed rows whose Yj is nonzero. Similarly, rank B is the span dimension of
the listed columns whose Xj is nonzero. There is no cross-sector cancellation.

If h is neither 0 nor lambda, all three active products in (1) are nonzero.
Thus Xj and Yj are nonzero in sectors 10,01,11. The 10 and 01 rows are
independent since h!=0; the corresponding columns are also independent.
Both factors automatically have rank two.

If h=0, A's first column is supported only in sector 11. It is nonzero
exactly when Y11 is nonzero. The nonzero products t10=t01=lambda already
give the second independent direction. The dual statement for B requires
X11 nonzero. Hence sharpness is exactly X11!=0 and Y11!=0.

If h=lambda, A's first column is supported only in sector 01. Its 01 row
is proportional to (lambda,1), whereas its only possible independent row is
the 10 row. The 11 row vanishes. Therefore rank A=2 exactly when Y01 and
Y10 are both nonzero. Dually, rank B=2 exactly when X01 and X10 are both
nonzero. The nonzero t11=lambda already ensures a nonzero 11 sector.

These are exact replacement criteria for the identity-pivot six-map argument;
they do not assume that all three sectors always require both maps.

## Lower bounds and attainment

One scalar compressed product t!=0 needs at least one dimension. If t=0
and both X and Y must be nonzero, at least two dimensions are necessary:
nonzero maps between one-dimensional spaces have nonzero product.
If neither map is required, a zero product needs no dimension.

For h outside {0,lambda}, sectors 10,01,11 each need one dimension, and
sector 00 needs exactly [1-2lambda+h!=0]. This gives the third case.
For h=0, sectors 10,01 need one each, sector 11 needs two, and sector 00
needs [1-2lambda!=0]. This gives the first case.
For h=lambda, sectors 10,01 need two each, sector 11 needs one, and sector
00 needs [1-lambda!=0]. This gives the second case.

Attain all these bounds by choosing, independently in each sector,

```text
nonzero t:                  Y=(1),       X=(t),
zero t, both maps required: Y=(1,0)^T,   X=(0,1),
zero t, no maps required:   zero-dimensional sector.
```

The products are (1), so their sum is 1 and the coordinate construction
above applies. Each stated sharpness criterion holds. This proves existence
at exactly the lower bound over every field, and completes the proof.

## Consequences and boundary

For a nonidentity scalar pivot lambda, the prescribed product h=lambda
forces dimension six. Thus substituting lambda into the old identity-pivot
formula, which would predict five for an endpoint product, is invalid.
For example, over F3, lambda=h=2 has exact minimum six, whereas h=0 or h=1
with the same pivot has exact minimum four.

The generic minimum three occurs exactly when h=2lambda-1 avoids 0 and
lambda. Such lambda exists over every finite field with at least four
elements. F2 and F3 give minima five and four respectively when lambda,h
are unrestricted. The F2/F3/F5 unrestricted minima were already established
by Ryanson Jonathan's #4609. The contribution here is the exact dependence
on both prescribed scalar values over every field.

No header frequency, later Schur-state law, physical caller, supplier
admission, new kappa or complete multiplication theorem follows. Uniform
physical and analytic costs remain separate unknown obligations.
