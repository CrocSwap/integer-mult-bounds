# A coupled GL3 COPY obstruction with explicit essential hypotheses

All coefficients in the statement are complex. Transpose is ordinary. The
binary rank objective is inherited from the fixed P112 separate-total model;
this proof does not establish its complete physical realization.

## 1. Model and precise statement

Use the 112 live E8 root lines obtained by removing the standard orthogonal
frame. Let X have entries in {-1,0,1}, and let G be the norm-two Gram matrix.
Then `XX^T=2G`, `X^T X=56I`. The binary constrained-entry matrix is
`B_ij=(1+G_ij) mod2`, which is symmetric, has diagonal one and rank nine.
For complex factors d,s, charge

`beta(d,s) = rank_F2 B[supp(d),supp(s)]`.

The eight original coordinate terms cost eight apiece. Choose columns x=X[:,4]
and y=X[:,6]. For **nonzero** u,v, assume `B[U,V]=0`, where U=supp(u), V=supp(v).
The matrix uv^T vanishes on every constrained entry and costs zero in this
objective. Leave the other six original terms unchanged.

For any `M in GL(3,C)`, define
`D=[x,y,u]M`, `S=[x,y,v]M^(-T)`. Let q_j,p_j be the first two coordinates of
column j of M and M^(-T), respectively. Suppose **each q_j and p_j is nonzero**.

Theorem: each replacement term has beta at least six. More precisely, if k_j
and l_j are the numbers of nonzero entries of q_j and p_j, respectively, then

`beta(D_j,S_j) >= 4+k_j+l_j`.

Thus the full decoder has COPY-rank sum at least 66. If all these coefficients
are nonzero, its sum is at least 72. These bounds are not asserted sharp for
the GL3 family. At unchanged width and normalization its full COPY power bill
is at least 33/32 of the original for `0<1-a<=1`.

## 2. Complete complex support reduction

For a nonzero complex pair (alpha,beta), consider `alpha*x+beta*y`. Scaling
by a nonzero number does not change support. If one coefficient is zero, its
support is an axis support. Otherwise set z=beta/alpha. At every row the two
coordinates belong to {-1,0,1}.

A cancellation with both row coordinates nonzero requires z=1 or z=-1. At
z=1 use (1,1); at z=-1 use (1,-1). Every other nonzero z has support exactly
the union of the two axis supports, represented by (1,2). This covers complex,
nonreal and unbounded coefficients without sampling or denominator limits.
Consequently five representatives exhaust every nonzero projected normal.
Their active-coordinate counts are 1,1,2,2,2.

## 3. Exact finite survivor lemma

For a representative q, put C(q)=supp(q_1*x+q_2*y), and define

`E(q,j) = {r in C(q): B_rj=1}`.

For every one of the 25 ordered representative pairs q,p and every one of the
5,824 ordered live-port pairs (i,j) with B_ij=0, the complete exact census gives

`rank_F2 B[E(q,j),E(p,i)] >= 4+k(q)+k(p)`.

The right sides are 6,7,8. The certificate gives an attaining port pair for
each representative pair, so the finite premise's minima are exact. It also
records all 25 rank histograms, slice-span dimensions and a transcript hash
covering every cost in class-major and then lexicographic port-pair order.
The record count is 25*5,824=145,600, not a count of distinct support matrices.

Primary verification generates both elementary E8 root families from exact
integer coordinates, removes the frame and binds the resulting X and binary
pairings to the immutable source snapshot. It computes these ranks with
112-column integer bitmasks and high-pivot binary elimination.

The separate checker uses the source's nine-bit labels and duals, with their
complete pairing factorization first checked by the primary oracle. It spans
reader labels and source duals using low pivots. Restriction of their binary
bilinear pairing to these spans has the same rank as the original support
matrix: replacing spanning lists by bases does not change row or column span.
Its complete transcript, histograms, minima, witnesses and dimensions agree.
No predecessor geometry/search code or primary census is imported.

This is complete finite evidence for a finite lemma plus a written exhaustive
class reduction. It is not a proof-assistant certificate of multiplication.

## 4. Surviving supports for arbitrary free rectangles

Choose any i in U and j in V; both exist by the nonzero hypothesis, and B_ij=0.
For a replacement term, write its left factor as
`q_1*x+q_2*y+c*u` and its right factor as `p_1*x+p_2*y+d*v`.

If r belongs to E(q,j), then it cannot belong to U: every row in U pairs to
zero with every column in V, whereas B_rj=1. Outside U, the u correction
vanishes, so the left factor is nonzero at r. Hence E(q,j) is contained in
its actual support, regardless of c and all cancellation choices on U.
Similarly E(p,i) is contained in the right factor's actual support: symmetry
of B gives the needed exclusion from V.

Binary matrix rank cannot decrease when rows or columns are added. Apply the
finite lemma and the five-class reduction to obtain
`beta(D_j,S_j)>=4+k_j+l_j`. This covers arbitrary supports and amplitudes for
u,v; it never assumes the rectangle is a singleton or maximal. It proves the
stated per-term and total COPY bounds.

## 5. Power invoice and surviving algebraic boundary

Grant every extra gathering, source-access, frame, mixing, restoration,
hosting and child-management expense zero, retaining the common width m and
normalization. Put q=1-a, with 0<q<=1. The original two terms contribute
`2*(8/m)^q`; the replacements contribute at least `3*(6/m)^q`. Their ratio is

`(3/2)*(3/4)^q >= (3/2)*(3/4) = 9/8`.

The other six original terms contribute the same amount on both sides.
They form 3/4 of the original eight-term COPY bill, while the replaced pair
forms 1/4. The full ratio is therefore at least
`3/4 + (1/4)*(9/8) = 33/32 > 1`.
When all projected coefficients are nonzero, each rank is at least eight;
the replacement ratio is at least 3/2 and the full ratio at least 9/8.
Additional nonnegative expenses cannot make these lower bills favorable.
This does not address savings elsewhere or a changed width/normalization.

Set A to the first two rows of M and C to the first two rows of M^(-T).
Then `AC^T=I_2`, or `sum_j q_j p_j^T=I_2`. A sum of at most one nonzero
rank-one matrix cannot have rank two. Thus at least two projected products
are nonzero for every GL3 change. With a nonzero free rectangle, any COPY
improvement in this mechanism must lie in the **exactly-two-product** branch.
This theorem supplies no lower bill or physical implementation for that branch.

## 6. Boundary counterexamples and limits

With M=I, both u,v nonzero on an odd singleton pair, the replacement costs are
(8,8,0). The third projected product is zero. This valid masked decoder cannot
be subjected to the six-per-term claim.

The nonzero rectangle hypothesis is independent. Set u=0, v=x and

```text
M = [1 0 1]
    [0 1 1]
    [1 0 2].
```

All three q_j and p_j are nonzero, and M has determinant one. Its actual
factors are `(x,y,x+y)` and `(x,y,0)`, so the costs are again (8,8,0).
The free-pairing condition is vacuous when U is empty; dropping the nonzero
hypothesis therefore falsifies both the per-term bound and the claimed total
floor 66. The certificate checks every entry of this identity.

The exponent range also matters: at q=2 the lower comparison reads
`3*6^2=108 < 2*8^2=128`. No power obstruction outside (0,1] is claimed.
Four exact Gaussian-integer fixtures, including complex column phases,
check ordinary-transpose factor identities; they are regressions, not an
enumeration of GL(3,C). Ten controls check the mathematical and accounting
boundaries. No stronger kappa, all-coordinate-pair theorem, complete supplier
recurrence, physical admission or full multiplication theorem follows.
