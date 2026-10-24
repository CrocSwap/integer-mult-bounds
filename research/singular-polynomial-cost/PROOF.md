# Exact singular polynomial costs

Let K be any field, R=K[t], and let the two data roles have paid factors
`I+u y^T`, where u is in R² and y is in K². Every GL2(K) map is free anywhere
in a word. Cost means the least number of paid factors. No scratch is used.

## Theorem

The zero matrix has cost two. Every nonzero matrix M with det M=0 has a
factorization `M=a b`, where a is a primitive column in R² and b is a nonzero
row in R². Primitive means that the entries generate R. Write

```text
V = span_K{b1,b2},       d = monic gcd(b1,b2).
```

Its exact cost is

```text
1  if a belongs to K² and V contains a nonzero constant;
2  otherwise, if a belongs to K² or d belongs to V;
3  otherwise.
```

Multiplying a by a nonzero scalar and b by its inverse does not change these
conditions. Every singular target is reachable with at most three factors,
although invertible polynomial targets can have unbounded cost as in #4763.

## Primitive factorization

Choose a nonzero column c of M and divide its entries by their monic gcd g,
obtaining a primitive a. Write the other column as c'. The determinant
condition says that c' is a fraction-field multiple h a. Choose r,s in R
with r a1+s a2=1. Then h=r c'1+s c'2 is a polynomial, so both columns are
polynomial multiples of a. This constructs b and proves existence. Two such
primitive a differ by a unit of R, hence by a nonzero scalar. These are
classical PID and Bezout facts.

A primitive a has a nonzero K-linear annihilating row exactly when a is in
K². Indeed, a nonzero relation makes its entries proportional over K, and
primitivity then makes the common polynomial factor a unit. The converse is
ordinary two-dimensional linear algebra.

## Three-factor construction

For every column a and row b over any associative unital ring, direct
multiplication gives

```text
[[a1,0],[a2,1]] [[1,b2],[0,0]] [[b1,0],[0,1]] = a b.
```

The three displayed factors have right vectors e1,e2,e1 respectively, so
all are legal paid factors over R. This uses no free maps. Applying the same
word with a=0 and b=0 also gives zero, but zero already equals the product
`diag(0,1) diag(1,0)` of two paid factors.

## Exact two-factor boundary

We use Theorem B of Nick Petalas's #4276, not a new proof of that predecessor:
a two-role target costs at most two exactly when some G,H in GL2(K) make
`N=G M H` satisfy `N12 in N11 R`. In this case `N11 C=N12` supplies the
literal two-factor word

```text
N = [[N11,0],[N21,1]] [[1,C],[0,N22-N21 C]].
```

For M=a b let phi be the first row of G and let x,z be the columns of H.
Then `N11=(phi a)(b x)` and `N12=(phi a)(b z)`.

If a is constant, choose phi annihilating a. Both entries vanish and the
criterion passes. If a is not constant, the primitive observation above
makes phi a nonzero for every allowed phi. Since R is an integral domain,
its factor cancels. The criterion becomes `b x divides b z`. The two
polynomials b x,b z generate the same ideal as b1,b2 because H is invertible.
Thus b x must be a nonzero scalar multiple of d. Conversely, if d is a
K-linear combination b x, then x is nonzero, extends to such an H, and d
divides b z. This proves

```text
cost(M)<=2  iff  a is constant or d belongs to V.
```

The cancellation and unit statements are specific to K[t]. They do not
assert the same classification in rings with zero divisors.

## Exact one-factor boundary

For every two-role target, cost at most one is equivalent to the existence
of nonzero x,w in K² with Mx=w. To see necessity, put a one-factor word in
the predecessor free-map normal form `(I+u y^T) S`. A nonzero constant v in
ker y is fixed by the paid factor; take x=S^-1 v and w=v. The free-only case
has the same property. For sufficiency, choose T in GL2(K) with Tw=x.
Then `(MT-I)w=0`, so the columns of MT-I span at most a one-dimensional
K-space. It is `u y^T` for some allowed u,y, hence `M=(I+u y^T)T^-1`.
This is the one-factor criterion already implicit in #4276, applied here.

For nonzero rank-one M=a b, equality Mx=w says `a(bx)` is a nonzero constant
column. A nonzero scalar polynomial times a nonzero polynomial has the sum
of their degrees. Consequently a is constant and bx is a nonzero constant.
The converse is immediate. Rank one prevents cost zero since free maps are
invertible. Zero has no nonzero constant image and cannot cost one; its
explicit two-factor word therefore has exact cost two. Combining these
bounds proves every case of the theorem.

## Sharp example over every field

Take

```text
a = (1,t)^T,       b = (t,t²+1),
M = [[t,t²+1],[t²,t³+t]].
```

The column is primitive and nonconstant. The row gcd is 1, but no K-linear
combination of t and t²+1 is 1, by comparing degrees two and one. Therefore
cost M=3 over every field, while the general column lower bound delta is at
most two. The above three factors attain it. Multiplying b by a nonzero
nonconstant polynomial leaves the exact cost three unchanged.

## Scope and credit

This contribution was produced by Nick Petalas. ToikY's #4334 explicitly
leaves singular targets outside its field-product theorem. Nick Petalas's
#4276 supplies the exact general two-factor criterion, and #4243 supplies
the free-map normal form, following Wentao Li's #4099 and #2513. The
invertible polynomial results #4763 and #4784 are complementary context.
The fixed e1,e2,e1 field-product template of #4780 is related precedent for
the outer-product construction; its basic matrix identity is elementary.
The new result is the complete singular K[t] classification, including the
attaining outer-product word and the all-field sharp example. The gcd and
rank-one factorization facts retain their classical status. Apache-2.0.

This is a scoped algebraic proof. Native coefficient preparation, routing,
precision, reversible restoration, stock and complete supplier costs remain
unknown. No new kappa, supplier admission or complete multiplication theorem
follows. Independent human and formal proof-kernel review are unclaimed.
