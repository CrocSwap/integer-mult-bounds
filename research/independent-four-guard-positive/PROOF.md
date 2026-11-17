# Four independent full guards are strictly above their product

Let K be a finite field of order q, let m >= 4, and put d = m-1. Fix a
nonzero column u and four linearly independent rows v_i with v_i u = 1.
For a uniform G in GL_m(K), let E_i mean that every leading principal minor
of orders 1 through m-1 of G(I-u v_i)G^-1 is nonzero.

**Theorem.** If p = Pr(E_i), then

```text
Pr(E_1 and E_2 and E_3 and E_4) > p^4
```

for every q and m in this domain. This is a four-event statement. It does
not assert association of every subfamily of an arbitrary dependent tuple.

The new steps below are the explicit four-dimensional subspace
classification, its closed formula, and the all-field four-event sign.
SHIN09-git's #6710 supplies the general subspace counting law and the
enlarged-space method used for triples. Those are cited premises, not new
results or executable dependencies.

## An explicit formula

Define

```text
A = q + (q-1)^2
W = q^4 + (q-1)^5
D = (q^(d+1)-1) q^d (q^d-1)(q^d-q)(q^d-q^2)
B_s = q^2 + (q-1)^2 (q+1-s),                  s = 2,3,4
H_s = (q-1)^(4-s) [(q-1)^s + (-1)^s(q-1)] / q
C_s = q^3 + (q-1) H_s

(a_2,a_3,a_4) = (7, 6(q-2), (q-2)(q-3))
(b_2,b_3,b_4) = (6, 4(q-2), q^2-3q+3).
```

Then the exact joint law is

```text
J_4 = (q-1) [W^d - sum_s b_s C_s^d
                    + q sum_s a_s B_s^d - q^3 A^d] / D.
```

To derive it, apply #6710's law to S = K^4 and t = (1,1,1,1).
For a subspace L containing t, that law uses

```text
h(L) = #{x in L : every coordinate of x is nonzero}
lambda(L) = q^dim(L) + (q-1) h(L)
mu(L,K^4) = (-1)^c q^(c(c-1)/2), c = 4-dim(L).
```

In dimension one, L = <t>, h = q-1, and mu = -q^3. In dimension four,
h = (q-1)^4 and mu = 1.

A two-dimensional L is spanned by t and a nonconstant vector x. Let s
be the number of distinct coordinates of x. Replacing x by ax+bt, with
a nonzero, preserves s and gives exactly q(q-1) representatives of the
same L. The number of ordered four-tuples using exactly s distinct field
values is S(4,s) q(q-1)...(q-s+1). Since the three relevant Stirling numbers
are 7, 6, 1, division gives a_s as above. Counting x_0+t_0 x with all
coordinates nonzero gives h = (q-1)(q+1-s). Thus lambda = B_s and mu = q.
When s > q the corresponding a_s is zero, so no nonexistent class enters.

A three-dimensional L is a hyperplane a dot x = 0, where a dot t = 0.
Its normal is unique up to nonzero scale. If its support has size s, the
number of full-support vectors in L is H_s. Indeed, after scaling the
s constrained coordinates, the number of nonzero s-tuples summing to zero
is

```text
Z_s = [(q-1)^s + (-1)^s(q-1)] / q.
```

This follows from Z_1 = 0 and Z_(s+1) = (q-1)^s - Z_s: choose the first
s entries, and the last nonzero entry is forced precisely when their sum
is nonzero. There are binom(4,s) Z_s/(q-1) normal lines of support s.
For s = 2,3,4 these are exactly b_s. Thus lambda = C_s and mu = -1.
These classes exhaust both projective planes of size q^2+q+1 in the
subspace interval. Substitution proves the formula over every finite field.

## A sufficient tail inequality

Write Q = q^d, t_1 = 1-1/q+1/q^2, and

```text
c = (1-1/q)/(1-q^(-m)),     p = c t_1^d.
```

Sample u' uniformly among the nonzero columns. Conditional on u', sample
four normalized rows independently and uniformly from v u' = 1. This
affine hyperplane has Q points. Let I be the event that the four rows
are independent. Normalization makes linear independence equivalent to
affine independence, so

```text
P_I = (1-1/Q)(1-q/Q)(1-q^2/Q),
1-P_I <= (1+q+q^2)/Q.
```

Conditioning on I gives the uniform independent-four tuple orbit by
#6710's equal-fiber argument.

Let z(u') be the conditional single-guard pass probability. Its mean is p.
It vanishes unless the last coordinate u'_m is nonzero. To see this,
the rank-one determinant identity gives the order-j minor as
1-sum_(a<=j) u'_a v_a. If u'_m = 0, the order-d minor is zero by
v u' = 1. The last-coordinate event has probability c.
Conditional Jensen therefore gives

```text
T = E[z^4] >= p^4/c^3.
```

Since the joint event outside I has probability at most 1-P_I,
P_I J_4 >= T-(1-P_I). It is sufficient for J_4 > p^4 that

```text
p^4 (c^-3 - 1) > 1-P_I.
```

Now c^-1 = 1+q^-1+...+q^-d, so c^-3-1 >= 3/q.
Also c > 1-1/q. Hence the following exact rational inequality suffices:

```text
L(q,d) = (3/q)(1-1/q)^4 (q t_1^4)^d > q^2+q+1.          (1)
```

For q >= 4, t_1 >= 3/4 and q(3/4)^4 > 1. For q = 3,
q t_1^4 = 2401/2187 > 1. Thus a successful tail threshold persists
as d increases for every q >= 3.

## Uniform large-field coverage and the finite remainder

For q >= 25, at d = 3,

```text
L(q,3) = 3q^2(1-1/q)^4 t_1^12
       > 3q^2(1-1/q)^16
       >= 3q^2 - 48q
       > q^2 + q + 1.
```

The middle step is Bernoulli's inequality. The last difference is
2q^2-49q-1, positive at q=25 and strictly increasing thereafter.
This covers every d >= 3 at every field order q >= 25.

For q=2, the event u' supported on the last coordinate passes all four
guards and has probability b = c 2^-d. Since c < 1 and
(3/4)^4 < 1/2, we have p^4 = c^4(3/4)^(4d) < b.

The remaining finite field orders and exact thresholds in (1) are:

| q | first d_0 >= 3 satisfying (1) | dimensions 3 <= d < d_0 |
| ---: | ---: | ---: |
| 3 | 45 | 42 |
| 4 | 9 | 6 |
| 5 | 6 | 3 |
| 7 | 4 | 1 |
| 8 | 4 | 1 |
| 9 | 4 | 1 |
| 11 | 4 | 1 |
| 13 | 4 | 1 |
| 16 | 3 | 0 |
| 17 | 3 | 0 |
| 19 | 3 | 0 |
| 23 | 3 | 0 |

The verifier checks (1) at each d_0 and evaluates the closed formula
against p^4 with exact rational arithmetic in each of the 56 remaining
cases. It prints every exact ratio, which is strictly greater than one.
Together with the analytic bounds, these finite comparisons prove the sign
in all dimensions and over every finite field. No numerical approximation
or assumption about unenumerated exceptions enters the argument.

## Separate finite corroboration of the formula

The verifier explicitly enumerates all two- and three-dimensional
subspaces in the above interval over F_2, F_3, F_4, F_5 and F_7 and checks
both class multiplicities and every h(L). F_4 uses x^2+x+1, rather than
arithmetic modulo four.

A second computation treats the first new ambient dimension m=4 over
F_2, F_3, F_4 and F_5. Conditional on u'_m != 0 and exactly j zero
coordinates among its first three entries, an invertible triangular
coordinate change makes the allowed rows the box
K^j times (K without zero)^(3-j). The coordinate change preserves
affine independence. The number of such u' is
(q-1) binom(3,j)(q-1)^(3-j).

To count ordered affine bases of a box, enumerate every unordered triple
of points. A noncollinear triple defines one affine plane. Each point
outside that plane is a valid fourth point, and each unordered triple
has six orderings. This counts exactly the ordered affinely independent
quadruples, without using the subspace formula. Weight the four box counts
by the image-column multiplicities and divide by
(q^4-1) q^3(q^3-1)(q^3-q)(q^3-q^2). The resulting fractions agree with
the formula. These are new bounded checks, not replays of a predecessor's
scientific suite.
