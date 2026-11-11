# Sparse supports retain the coefficient-height obstruction

This scoped proof was produced by Nick Petalas. Apache-2.0.

Put pi=2+i, rho=2-i and alpha=pi/rho=(3+4i)/5. These are the
fixed Gaussian primes and generator of zxv's #5436. Nick Petalas's
#5934 determines the coefficient heights for consecutive powers. The
new result allows every strictly increasing integer exponent support,
including arbitrarily high degree and Laurent supports, at the same
minimum term count. Gaussian unique factorization and the Vandermonde
determinant are classical inputs.

## Statement

Let f>=1, n=f+1, and m_0<...<m_n be integers. Set
delta_s=m_(s+1)-m_s for 0<=s<n. There is a unique nonzero relation
line over Q(i)

    sum_(j=0)^n c_j alpha^(k m_j)=0,   k=0,...,n-1.

Its primitive Gaussian-integer coefficient vector c is unique up to a
Gaussian unit. Every c_j is nonzero, and its exact valuations are

    A_j = v_pi(c_j)  = sum_(s=j)^(n-1) (n-1-s) delta_s,
    B_j = v_rho(c_j) = sum_(s=0)^(j-1) s delta_s.

Empty sums are zero. In particular the primitive vector's total
split-prime valuation mass is exactly

    M(m) = sum_j (A_j+B_j)
         = sum_(s=0)^(n-1) [n-1+2s(n-1-s)] delta_s.

Consequently

    M(m) >= 2 binom(n+1,3),

with equality if and only if every delta_s=1. Thus consecutive supports,
up to translation, uniquely minimize this valuation mass. This optimizes
that exact arithmetic quantity, not the actual largest complex modulus.

Every nonzero Gaussian-integer relation on this support, primitive or
otherwise, satisfies

    |c_j|^2 >= 5^(A_j+B_j),
    max_j |c_j| >= 5^(binom(n,2)/2),
    sum_j log_2 |c_j| >= log_2(5) binom(n+1,3).

Here A_j,B_j refer to the primitive vector. For a nonprimitive relation
the actual valuations can only increase. The inequalities therefore
exclude an asymptotic improvement of the quadratic maximum coefficient
bit height or cubic explicit coefficient-list storage merely by choosing
nonconsecutive powers. The consecutive upper bounds are prior #5934.

For D=diag(1,alpha), the eigenvalues of D^tensor f are exactly
alpha^k for k=0,...,f. Since (D^m)^tensor f=(D^tensor f)^m for every
integer m, these are exactly the coefficient relations among the n+1
specified lifted powers. No physical tensor array needs to be stored
to state this implication.

## Vandermonde cofactors and primitive normalization

Write x_j=alpha^m_j. These numbers are distinct: v_pi(alpha)=1, so
alpha^t=1 implies t=0. The matrix with entries x_j^k has n rows
and n+1 columns. Any n-column minor is the nonzero Vandermonde product

    Delta_j = product_(a<b; a,b != j) (alpha^m_b-alpha^m_a).

It therefore has rank n. Its signed minors (-1)^j Delta_j give a
nonzero kernel vector, and all its coordinates are nonzero. A common
denominator gives a Gaussian-integer vector. Divide by its Gaussian
greatest common divisor to obtain a primitive vector. Because Z[i] is
a principal ideal domain, any other integral vector on this rational
line is an integral multiple of the primitive one. One way to see the
last assertion is to take a Gaussian-integer Bezout combination of the
primitive entries equal to 1 and apply it to the proposed multiple.

For a<b,

    alpha^m_b-alpha^m_a
      = alpha^m_a (alpha^(m_b-m_a)-1).

The parenthesized factor has pi valuation zero: its first summand has
positive valuation and its second has valuation zero. At rho, those
summands have distinct valuations -(m_b-m_a) and zero. Hence

    v_pi(alpha^m_b-alpha^m_a)=m_a,
    v_rho(alpha^m_b-alpha^m_a)=-m_b.

This also holds for negative m_a. It follows that

    L_j = v_pi(Delta_j)  = sum_(a<b; a,b != j) m_a,
    -U_j = v_rho(Delta_j) = -sum_(a<b; a,b != j) m_b.

For any prime, primitive normalization subtracts the minimum valuation
over all coordinates. Common factors at other Gaussian primes have
zero valuation at pi and rho and do not change this calculation.

The minimum L_j is L_n, and the maximum U_j is U_0. To compute the
differences, compare sorted exponent lists before and after omitting
one element. In an n-element list, the exponent in slot t contributes
n-1-t times to L and t times to U. Therefore

    L_j-L_n = sum_(s=j)^(n-1) (n-1-s)(m_(s+1)-m_s),
    U_0-U_j = sum_(s=0)^(j-1) s(m_(s+1)-m_s).

These nonnegative formulas also prove the asserted extrema. They are
the claimed A_j and B_j, including the ties A_(n-1)=A_n=0 and
B_0=B_1=0. Translation of the support cancels from both differences.

## Sharp valuation mass and storage consequences

In sum_j A_j, gap delta_s occurs for j=0,...,s, with weight n-1-s.
In sum_j B_j it occurs for j=s+1,...,n, with weight s. Its combined
weight is

    (s+1)(n-1-s)+(n-s)s = n-1+2s(n-1-s).

Every weight is strictly positive because n>=2. Every integer gap is
at least one. Setting every gap to one gives

    A_j=binom(n-j,2),   B_j=binom(j,2),
    sum_j (A_j+B_j)=2 binom(n+1,3).

Thus this is the sharp minimum mass, and equality forces every gap to
one. Any missing power strictly increases the mass by the exact
weighted gap excess

    sum_s [n-1+2s(n-1-s)] (delta_s-1).

A nonzero Gaussian integer with valuations A,B at pi,rho has norm
at least 5^(A+B), since the remaining factor has positive integer norm.
This proves the coefficient bounds. For the maximum bound use
A_0>=binom(n,2) or B_n>=binom(n,2). Summing logarithms gives the
displayed cubic lower bound.

For an explicit binary coordinate encoding put
h(c)=log_2 max(1,|Re c|,|Im c|). Since
max(|Re c|,|Im c|)>=|c|/sqrt(2),

    max_j h(c_j) >= binom(n,2) log_2(5)/2 - 1/2,
    sum_j h(c_j) >= log_2(5) binom(n+1,3) - (n+1)/2.

Thus even a sparse list containing only the n+1 nonzero coefficients
needs Omega(f^3) coefficient bits. Recording exponents adds costs and
cannot remove this lower bound. This is not a lower bound for factored,
compressed or streamed descriptions, nor for approximate cancellation,
other generators or relations with more than f+2 terms. It does not
price a productive native consumer or change the selected frontier.
