# Concrete false certificates

For rank profile n={1:N}, m=9 and W>0, let lambda=0 without surcharge and
lambda=32*m^2/10^16 with surcharge. The claimed root equation simplifies exactly
to

```text
F(a) = N(1+lambda)9^a - 9W = 0.
```

F is continuous and strictly increasing. Write A=1+lambda=p/q in lowest terms,
B=9W, u=3^(1/10)=9^(1/20), and

```text
N = floor(B/(A*u)) = floor( ((B*q)^10/(3*p^10))^(1/10) ).
```

The code computes this floor using integers. Strictness is verified, not assumed:

```text
3*(N*p)^10 < (B*q)^10 < 3*((N+1)*p)^10.
```

Consequently N*A*u<B<(N+1)*A*u. The N profile's root lies strictly above a0=1/20,
and the N+1 profile's root strictly below. A separate degree5 integer inequality
proves F(1/10)>0 for both counts; F(0)<0 is a direct rational comparison. Thus
these roots satisfy the original advertised initial domain and uniqueness.

Let delta=10^-24. Since e<3<9, log9>1 and `9^delta>1+delta` for delta>0. The
floor inequalities yield

```text
N*A*u*9^delta > B*N/(N+1)*(1+delta) > B,
(N+1)*A*u/9^delta < B*(N+1)/N/(1+delta) < B,
```

where both last strict comparisons are equivalent to N*delta>1. That integer
condition is checked. This proves the two exact neighboring root intervals
without evaluating a transcendental function numerically. The independent
checker obtains N by Newton integer-root iteration, while the main constructor
uses binary search, and verifies all the inequalities above.

On both profiles with count N, the original function returns
`[a0-delta,a0]`. Its upper endpoint lies strictly below the root, so this is a
false bracket, not merely an unproved certificate. On count N+1 it returns the
same bracket, which happens to contain that different root. EXPECTED records
all four complete source executions at the original default34/24 settings.

# Which decision loses the invariant

The original bisection promotes mid to the lower endpoint only when the interval
upper bound for the fee is strictly below D. Every other outcome sets the upper
endpoint to mid. That includes an interval whose lower bound is below D and
upper bound above D: no side of the root is established.

For all four fixtures, the exact rational source enclosure at a0 with34 terms
crosses D. EXPECTED stores a small outward enclosure of `(fee-D)/(mW)`, and
regeneration checks the underlying full Fractions. The original floating
nomination encloses both neighboring true root intervals and is explicitly
recorded. Its initial upper endpoint is strictly above a0+delta. Therefore the
final upper endpoint a0 arose during bisection; its assignment was not justified
by a positive lower sign. The failure is isolated from float nomination coverage.

The existing maintainer review already observed this logical problem. The new
result is a pair of actual false returned brackets at default settings, with
independent exact root separation and a tested endpoint-certified alternative.

# Repair invariant and arithmetic assumptions

The standalone replacement accepts an interval oracle for a strictly increasing
continuous function. At every successful stage it maintains

```text
F(low)<0<F(high).
```

An interval wholly below zero may replace low. One wholly above zero may replace
high. An interval containing zero changes neither endpoint. Increasing the
interval order may decide the sign; a finite cap instead returns an explicit
unresolved status with the still-certified wider bracket. If initial signs are
not certified, no bracket is returned. A `CERTIFIED` result has adjacent grid
endpoints and both strict signs established. This invariant proves enclosure by
monotonicity, independent of how close the root is to a grid point.

Exact grid equality can remain undecided at every finite order; the algorithm
does not claim universal termination with a one-tick answer. A finite term budget
is a resource limit, never evidence for an upper sign. There is no floating
nomination in the repair, and all control comparisons use integers/Fractions.

The concrete profile oracle uses the original log/exp bounds. Their positive
atanh series has a geometric upper remainder; the supplied code even doubles
that upper remainder again, which is conservative. Its exponential Taylor tail
uses a geometric upper ratio at most y/(terms+1). The repair explicitly enforces
0<=a<=1/10 and every `a*ln_upper<=1`, the original exp routine's stated envelope.
Positive integer rank counts, ranks1..m, positive deficit and strict increase are
also explicit checks. Assertions disappearing under `-O` cannot broaden those
predicates. The selected fixtures satisfy them with assertions enabled as well.

# Audit boundary

The very large profiles are finite inputs to the generic arithmetic API. No
construction or legal frame schedule realizing them is supplied. This finding
does not establish an error in a selected supplier certificate, and the repair
does not validate PR1048's floating search comparisons, fixed-exponent ordering,
first-move nomination coverage or exhaustive-neighborhood conclusion. The
maintainer's deferred status and the selected conditional result remain intact.
