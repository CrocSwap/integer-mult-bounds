# Reciprocal response and diagonal metric

## Integer construction

Let `n>=3`, `k=n-2`, and `m=n-4`. Use coordinates `(a,b,c)`, where
`a` has `k` entries. Let `s=sum(a)`. Define

```text
u=(1^k,m,0)^T,       ell=(-1^k,1,0),
R=I+u ell,           P(a,b,c)=(a,c,b),
E=P R.
```

Since `ell u=-2`, we have `R^2=I`. Thus `E^-1=R P`. In coordinates,

```text
E(a,b,c)    = (a-s*1+b*1, c, -m*s+(m+1)*b),
E^-1(a,b,c) = (a-s*1+c*1, -m*s+(m+1)*c, b).
```

Both matrices are integer matrices with zero diagonal. Each factor
`P,R` has determinant minus one, so `det(E)=1`. The factorization

```text
E-I=U V,

U = [ 1  0 ] repeated k times,
    [ 0  1 ],
    [ m -1 ],

V = [ -1 ... -1   1  0 ],
    [  0 ...  0  -1  1 ]
```

has two independent columns in `U` and two independent rows in `V`.
Therefore `rank(E-I)=2`. Also `E^-1-I=-E^-1(E-I)`, so the inverse
has the same correction rank. The fixed space is `s=b=c`; it has
dimension `n-2`. Relative to `P`, the difference `E-P=P u ell` has
rank one. This last rank does not remove the cost of `P`.

## Sharp rank bound in the stated matrix class

Let `A` be an invertible matrix of size `n>=3` over a field of
characteristic zero. Suppose that both `A` and `A^-1` have zero
diagonal. Rank zero for `A-I` is impossible. If its rank were one,
write `A=I+v w^T`. Each diagonal equation gives `v_i w_i=-1`, so
`w^T v=-n`. The rank-one inverse formula gives

```text
A^-1=I+v w^T/(n-1).
```

Its diagonal is `(n-2)/(n-1)`, which is nonzero. This contradicts
the hypothesis. The construction above therefore attains the minimum
correction rank two.

The bound applies to `rank(A-I)`. It is not a lower bound on native
children, record fields, or a global supplier. On sixteen independent
blocks of sizes six and eight it gives the sharp sum 32. It gives no
such bound for an arbitrary coupled 112-port response.

## The rational symmetric six-mode restriction

Suppose a rational symmetric six-by-six matrix `A` and its inverse
both have zero diagonal. If `rank(A-I)=2`, four eigenvalues are one.
The other two eigenvalues `a,b` obey

```text
a+b=-4,     1/a+1/b=-4,     ab=1,
{a,b}={-2+sqrt(3),-2-sqrt(3)}.
```

Let `u,v` be orthonormal eigenvectors for `a,b`. The two diagonal
equations imply `u_i^2=v_i^2=1/6` at every coordinate. Hence
`u=sigma/sqrt(6)` and `v=tau/sqrt(6)` for sign vectors `sigma,tau`.
The spectral expression is

```text
A=I-(sigma sigma^T+tau tau^T)/2
    +sqrt(3)*(sigma sigma^T-tau tau^T)/6.
```

Rationality forces the last coefficient matrix to vanish. The two
rank-one projectors would then be equal, in conflict with orthogonality.
Thus the minimum rank is at least three. Three disjoint exchanges
attain three. The rational-entry hypothesis is needed: the independent
review includes a real, nonrational symmetric example of rank two.

## Classification of diagonal metrics

Assume now `n>=5`, so `m=n-4>0`. Set

```text
J=diag(1^k,-1/m,-1/m),       K=J^-1.
```

Then `Ju=-ell^T`, `u^T J u=2`, and `ell K ell^T=2`. Expansion
gives `R^T J R=J`. The last two metric entries agree, so
`P^T J P=J`. Consequently

```text
E^T J E=J,       E^-T=J E J^-1.
```

Every diagonal invariant real metric is a scalar multiple of `J`.
To prove this, write it as `D=diag(d_0,...,d_(k-1),e,f)`. The last
column norm gives `e=f`. The norm of column `a_i` gives

```text
sum_j d_j + m^2 f = 2 d_i.
```

Thus all `d_i` equal a common value `d`. Since `k=m+2`, the equation
is `m(d+m f)=0`, so `e=f=-d/m`. These necessary conditions are
sufficient by the identity for `J` above.

A nonzero real scale gives inertia `(n-2,2)` or `(2,n-2)`. In
particular, no positive diagonal metric exists for `n>=5`. A metric
whose entries are units in `Z[1/2]` exists if and only if `m` is a
power of two. The units of this ring are the signed powers of two;
the ratio of `d` and `-d/m` must be a unit. Conversely, the displayed
`J` has unit entries when `m` is a power of two. The allowed sizes are
therefore `n=4+2^h`, `h>=0`.

The dimension limits are material. At `n=2`, an exchange has correction
rank one. At `n=3`, this construction is a three-cycle and has a
positive diagonal metric. At `n=4`, every diagonal invariant metric
of this construction is singular. The actual native geometry in this
package supplies sizes six and eight; it does not supply every size
in the abstract family.

## The actual physical response

The pinned role placement gives eight six-mode blocks and eight
eight-mode blocks. Let `H` be the actual 24 pair codes on the large
48-port sector, with identity on the other 64 ports. In each large
block the mode order is

```text
centre, pair_difference_a, pair_difference_b,
negative_difference, contrast, negative.
```

Use the pinned order for each small eight-clique. Apply the block
formulas above, then set each physical matrix to `H^-1 A H`.
The last two modes in every block form complete physical pairs.
Therefore the physical metric remains diagonal. Its entries are
80 copies of one, 16 copies of `-1/2`, and 16 copies of `-1/4`.

The pair matrices satisfy `H_pair^T H_pair=2I`. This scale is constant
on the large sector, and each mode response preserves that sector.
These facts preserve the metric identity under the physical basis
change. Similarity alone would not prove it.

The complete response satisfies both inverse orders and

```text
E=P R,       P^2=R^2=I,
rank(E-P)=16,       rank(E-I)=32,
E^-T=J E J^-1.
```

Both physical diagonals are zero. Each nonzero response entry joins
orthogonal pinned port labels. Physical `P` is the identity on 80
ports and acts within the other 32. It has 160 nonzero entries,
including signed halves; it is not a physical field permutation.

For the physical factor `R-I=U L`, the exact centre Gram is

```text
L J^-1 L^T=diag(4 I8,2 I8).
```

The large-sector factor four comes from the actual pair code. A later
centre encoding must retain this normalization.

The two correction rows in the six-mode rank-two factor have supports
of sizes five and two. Their union contains all six modes. Only the
first row is the reflection query. The rank-two factorization does
not supply a physical capture or terminal access.

## Evidence

The quantified arguments above are proofs. The replay adds exact
regressions in dimensions 3 through 16 for the rank-two construction
and 5 through 24 for the metric classification. It verifies the
actual 48-port pair binding and the complete 112-port model.

The independent algebra review uses a separate column calculation.
It checks both inverse orders, physical ranks, determinants, query
supports, and meaningful boundary controls. The native results and
their separate verification scope are in [NATIVE.md](NATIVE.md).
