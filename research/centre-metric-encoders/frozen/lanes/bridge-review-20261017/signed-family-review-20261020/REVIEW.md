# Review of the general signed-family word and restrictions

The root's complete scalar word, exact price, and prefix bounds are
correct. The oblique lane's diagonal-metric classification and
rank-two-per-block lower bound are also correct. The general basis
was first supplied by this review lane. Thus this is an independent
check of the root's word and cost, not an independent second review
of this lane's own basis.

The checked sources are:

- [Root proof](../../../root/SIGNED-METRIC-DYADIC-FAMILY-20261020.md),
  SHA256 `c19042d37e37921de9a67fbdaf262305811190f7e886f199b89a09f2c044667a`.
- [Root checker](../../../root/check_signed_metric_family.py),
  SHA256 `9daacf3e3f5683477235824a18afb92b09aad42c5ac297862aa1d2c7c5dea9fa`.
- [Family restrictions](../../oblique-native-20261017/signed-metric-reciprocal-20261020/FAMILY.md),
  SHA256 `d5764b5fd29ccd897a7a666b22d8e77bdca415f65072d44974b0ff7b70f37e43`.
  Its separate freeze is
  `a6088c38e984e7c4f15fb462d0cb89ac2c73cb2b6bbba0501513c236b32107b1`.

## Scalar word

Put \(k=2^r\), \(n=k+4\), and use the root's coordinate order.
After the Walsh transform and the first two-field butterfly, the
named fields hold \(S,T,d,b,c\). The six instructions then give

\[
 S=v=S_{\rm old}-b_{\rm old},\qquad
 T=\ell=-T_{\rm old}-v,
\]

and

\[
 b=-b_{\rm old}-(k/2)\ell-((k+2)/4)v
   =(k/2)T_{\rm old}-b_{\rm old}+((k-2)/4)v=w'.
\]

The final butterfly gives \(v+w'\) and \(v-w'\). This proves the
word implements the stated basis for every \(r\). Each instruction
is invertible on arbitrary input contents. Reverse order with
inverse instructions therefore gives the complete inverse without
a zero target or an extra field.

There are \(kr/2\) Walsh butterflies and two further butterflies.
Each costs 20 real primitives. The four unit/sign instructions in
the middle cost 20. The other two ADD coefficients are \(k/2\) and
\((k+2)/4\).

For \(r\ge2\), their prices are \(2r+6\) and \(2r+10\). For \(r=0\)
they cost 10 and 16; for \(r=1\) they cost 8 and 8. Thus the total
price, in either direction, is

\[
 86\ (r=0),\qquad 96\ (r=1),\qquad 10kr+76+4r\ (r\ge2).
\]

The instruction count is \(3kr/2+12\). The tariff charges the
non-power-of-two dyadic ADD coefficient by its complete numerator
bit length and population count. It is not priced as a unit ADD.

## Prefix bounds

At the end of the initial Walsh and pair blocks, the row one-norm
is at most \(\max(k,2)\). Relative to those inputs, the middle
S and T rows have norms at most two and three. Its b row has norm
at most

\[
 1+(k/2)3+((k+2)/4)2=2k+2.
\]

The last butterfly has prefix norm at most \(4k+4\): the doubled
row gives that bound, and the final subtraction gives \(v-w'\).
This proves the root's forward bound
\(4(k+1)\max(k,2)\).

For the inverse, the first inverse butterfly has prefix norm at
most two and completed norm one. In the three-field inverse,
the b row is bounded by \(1+(k+2)/4+k/2\); the T row by two; and
the restored S row by one plus the b bound. All are at most
\(k+5\) for \(k\ge1\). Every remaining inverse butterfly has
prefix norm at most two and completed norm one. Completed stages
therefore do not multiply the bound repeatedly. This proves
the inverse bound \(2(k+5)\).

The forward word introduces denominators only in the two middle
ADDs, at height at most two. In reverse, the first inverse
butterfly adds one binary division. The middle block can add
at most two more. The disjoint inverse Walsh and pair parts add
at most \(\max(r,1)\). Thus the stated inverse height
\(\max(r,1)+3\) is valid. These are scalar-word bounds only.

## Diagonal-metric classification

For the reciprocal family, write \(m=n-4>0\) and let
\(D=\operatorname{diag}(d_0,\ldots,d_{n-3},e,f)\).
The last column of E has one unit entry in row b. Its norm
equation gives \(e=f\). The ordinary column norm equations give

\[
 \sum_jd_j+m^2f=2d_i.
\]

Thus every \(d_i=d\). Since there are \(m+2\) such entries,
these equations give \(m(d+mf)=0\), and hence \(e=f=-d/m\).
The known metric identity proves sufficiency. The entire space
of invariant diagonal metrics is therefore the scalar multiples
of \(J\).

A nonsingular real such metric is indefinite. If all its entries
are units of \(\mathbb Z[1/2]\), their ratio \(m\) must be a
signed power of two. Since \(m>0\), it is \(2^r\). Conversely,
that condition makes both J and its inverse diagonal dyadic units.
The criterion is exact for this family.

The excluded small dimensions matter. At \(n=3\), this family is
a three-cycle and permits a positive diagonal metric. At \(n=4\),
the off-diagonal equations force the ordinary weights to zero;
the remaining two weights agree. Such a metric is singular.

## Minimum displacement and scope

If \(A=I+vw^T\) has zero diagonal, then \(v_iw_i=-1\) and
\(w^Tv=-n\). For \(n\ge3\) in characteristic zero, its inverse
has diagonal \((n-2)/(n-1)\), which is nonzero. Thus an invertible
response and its inverse cannot both have zero diagonal with
\(\operatorname{rank}(A-I)<2\).

The family E attains rank two in each block. Rank 32 is therefore
sharp for the stated direct sum of sixteen independent blocks.
The proof does not give a rank-32 bound for coupled 112-port
responses or a changed baseline. In particular, \(E-P\) has
rank sixteen and is the quantity captured by the signed code.

## Checks and attribution

[check_family_review.py](check_family_review.py) imports this lane's
frozen exact arithmetic, not producer code. It constructs the
basis from \(v,w'\), replays the complete word and inverse on
arbitrary inputs, and checks both inverse orders, the Gram,
determinant square, exact cost, and bounds for \(k=1,\ldots,64\)
in powers of two. Five additional input fields remain unchanged.
A deleted gate fails.

A separate calculation builds every coefficient equation for a
diagonal invariant metric, for \(n=5,\ldots,24\). It verifies
nullity one, reciprocal zero diagonals, and both displacement
ranks. These checks support the all-size proofs above.

Run in normal Python and in `python3 -O`, with separate
`--output` files. The expected status is
`PASS_SIGNED_FAMILY_WORD_AND_METRIC_CLASSIFICATION`.
The receipts must match.

The root lane supplied the combined scalar word and its prices.
This lane supplied the underlying basis and this word review.
The oblique lane supplied the metric classification and sharp
blockwise restriction. AI assistance was used.

No general native row placement, phase recipe, caller, host,
or supplier bound is proved here. Publication is coordinated by
the parent; this lane does not create a PR. Before a PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
