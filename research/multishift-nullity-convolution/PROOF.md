# Exact coefficient reduction

Let q be a prime power. Let n >= 0 and let lambda_1,...,lambda_t be
distinct elements of F_q, with 0 <= t <= q. Let a_i >= 0 and R=sum a_i.
The target N(a) counts n by n matrices H with nullity(H-lambda_i I)=a_i.
If R>n, distinct eigenspaces cannot fit, and N(a)=0.

This proof starts from the exact multi-shift formula in the retained
[Discussion](DISCUSSION-5261.md). That formula extends Nick Petalas's
[two-shift proof](../schur-rank-pair-law/PROOF.md). We claim the coefficient
reduction, not a new eigenspace counting formula.

Put P_j=product_{l=1}^j(q^l-1), P_0=1, and m=n-R. Define coefficients by

```text
C(z) = product_i [sum_{u=0}^m z^u / (P_u q^(a_i u))] mod z^(m+1)
c_U = coefficient of z^U in C(z).

N(a) = P_n / product_i P_(a_i)
       * sum_{U=0}^m (-1)^U
         q^[n(n-R-U) + binom(R+U,2) - sum_i binom(a_i,2)]
         c_U / P_(m-U).
```

All operations use rational numbers. The final value is a nonnegative
integer because it equals the matrix count below. The exponent in the
outer sum is nonnegative. The first term is nonnegative, and
binom(R+U,2) >= sum_i binom(a_i,2).

## Derivation

In the prior formula write k_i=a_i+u_i, K=sum k_i=R+U, and
s_i=sum_{j<i} k_j. Gaussian coefficients satisfy

```text
product_i G(n-s_i,k_i) = P_n / (P_(n-K) product_i P_(k_i))
G(k_i,a_i) = P_(k_i) / (P_(a_i) P_(u_i)).
```

The P_(k_i) factors cancel. The total sign is (-1)^U. The exponent from
all graph lifts and all Mobius factors is

```text
sum_i s_i k_i + sum_i binom(u_i,2)
 = binom(K,2) - sum_i binom(k_i,2) + sum_i binom(u_i,2)
 = binom(R+U,2) - sum_i binom(a_i,2) - sum_i a_i u_i.
```

Thus all factors except product_i 1/(P_(u_i) q^(a_i u_i)) depend only
on U. The sum of this product over u_i>=0 with sum u_i=U is c_U.
Grouping the prior finite sum by U proves the formula for every stated
n, q and nullity vector. For t=0, C=1 and the expression is q^(n*n).
For m=0, it reduces to P_n q^[binom(n,2)-sum_i binom(a_i,2)] /
product_i P_(a_i), as required for a direct sum of full eigenspaces.

## Algorithm and cost

Multiply each factor into an array of m+1 coefficients and discard
higher degrees after each factor. This does not change any retained
coefficient. The implementation performs exactly t(m+1)(m+2)/2 rational
coefficient products. Product construction and the final sum add O(n+tm)
arithmetic operations. The complete bound is O(n+t(m+1)^2) arithmetic
operations. It keeps O(m) live coefficients and O(n) factorial values.

These are arithmetic counts, not bit-complexity bounds. Rational values,
integer exponents and the result can have many bits. Prime-power input
validation also has its own cost. The implementation accepts distinct
shift counts through t<=q; it does not accept a list with repeated shifts.

The direct sum has binom(m+t,t) feasible terms. The benchmark visits only
these feasible terms; it does not compare against a wasteful Cartesian
product. A measured speedup applies only to its stated host and fixture.

## Research boundary

This is an exact evaluation algorithm for a known distribution. A Schur
weight must depend only on these joint nullities before this reduction
can replace its matrix sum. The actual ensemble, weight, paid selector,
header emission, reads, dirty restoration and complete supplier bill are
not supplied here. No complete multiplication exponent changes.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
