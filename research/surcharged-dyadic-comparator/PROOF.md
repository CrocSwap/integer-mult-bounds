# Surcharge-aware equality and strict order

Fix integers m=2^k>=2 and W>0. For each profile let n_r>=0 be integers at
dyadic ranks 1<=r<=m, N=sum n_r>0, and lambda=32m^2/10^16. Define

`F(a)=sum n_r r^(1-a)+lambda N-Wm^(1-a)`.

This is the signed source residual underlying PR1392: the difference of two
such residuals with common W is exactly its signed price, including the
count fee. It is not the full replicated-and-idle PR589 caller equation.

Multiplication by t^k with t=2^a gives exactly

`P(t)=sum_(j=0)^k n_(2^j)2^j t^(k-j)+lambda N t^k-mW`.

All coefficients of positive powers are nonnegative, and the coefficient
of t^k is n_1+lambda N>0. In particular degree is exactly k even if all
calls have full rank. Dropping zero-count entries does not change P. If
P(1)<0, its constant term mn_m-mW is negative. For every t>0, P'(t)>0;
P(0)<0 and P(t) tends to infinity. Hence it has exactly one positive root
alpha, that root is simple, and alpha>1. Multiplication by t^k is positive,
so log2(alpha) is the unique positive root of F. Comparing alphas therefore
compares savings without approximating logs or exponentials.

## Equality lemma

Take two admitted polynomials P,Q, and their monic rational GCD g. The
constant terms of P,Q are nonzero, so g has no zero root. It has at most
one positive real root, which if present is simple and greater than one,
since every root of g is a root of both P and Q. Negative real factors
`1-beta` are positive at one. Every nonreal conjugate pair contributes
`(1-z)(1-conj(z))=|1-z|^2>0`. All such factors include multiplicity, and
the leading coefficient of g is positive (one). Thus g(1) is negative
exactly when g has the positive common root; otherwise it is positive.
It cannot vanish since P(1),Q(1)<0. A constant gcd is one and takes the
second case. This proves

`alpha_P=alpha_Q  iff  g(1)<0`.

The fixture with common factor t+3 shows why merely checking deg(g)>0
is false. Rational-root detection alone is also incomplete: two actual
surcharged profiles below share the irreducible factor t^2-1025/1024.

## Strict order and independently checked certificates

If g(1)>0, the two positive roots are distinct. Doubling rational H from2
eventually makes P(H),Q(H)>0. Exact bisection encloses each root in [1,H],
retaining a point interval when the midpoint is an exact root. The lengths
shrink to zero. Since the distance between distinct roots is positive,
finite refinement makes the enclosures disjoint and determines their order.
This proves termination, not a uniform efficient separation bound. An
explicit resource budget may return UNRESOLVED without asserting equality.

The independent checker needs no GCD implementation. For equality it checks
a monic proposed factor g with g(1)<0, two quotient polynomials, and product
degree at most k. It evaluates each product against the direct source
residual at k+1 distinct rational t. Two degree-at-most-k polynomials equal
at those points are identical. Thus g really divides both source residuals;
the same sign argument proves a shared positive root. For strict order it
checks source residual signs at each rational bracket endpoint and checks
strict separation. Monotonicity proves that each bracket contains the unique
root. These tests do not rely on the compiler coefficients or a primary
decision being correct.

## Constructed retained-fee ties

Use m=64, lambda=p/q in lowest terms, u=1025, v=1024. For d=1 or2 set
R=2^d and h=6/d. Let A contain only rank1 and B only rankR, with pre-scaled
counts `A0=R v q+p u`, `B0=u(q+p)`. Put `t^d=u/v`. Dividing F by t^{-6}
is equivalent to the P equation, and at that t,

`A0 (1+lambda) t^6 = B0 (R t^(6-d)+lambda t^6)`.

Both sides equal `(R v q+p u)(q+p)u^h/(q v^h)`.
Scale both counts by `64 q v^h` and choose
`W=(R v q+p u)(q+p)u^h`; then both moments equal mW.
Dividing all counts and W by their common integer factor preserves the
identity. Counts differ, and t>1 makes P(1)<0 by strict monotonicity.
For d=1 the root is rational; for d=2 it is irrational since 1025 is not a
square. `(1025/1024)^10<2` places both positive a values below 1/10, as
required by the unchanged predecessor signed-price enclosure. Its strict
interval around zero is a sound unresolved answer, not a false comparison.

All-input statements above rest on exact identities and monotonicity.
Finite census and corruption tests exercise implementation and source
binding; they do not assert circuit realization or a new multiplication bound.
