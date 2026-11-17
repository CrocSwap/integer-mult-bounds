# Exact helper capacity with prescribed odd denominators

This scoped algebraic result was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let D=Z[1/2]. Let K be any finite m-by-n matrix over D. Fix positive odd
integers a,b. A t-channel boundary is a pair of rational matrices

```text
X in Mat(t,m,Q),  Y in Mat(n,t,Q),  X K Y = I_t,
a X over D,       b Y over D.
```

These are denominator divisibility budgets. They do not bound coefficient
magnitudes, dyadic precision, operation count or native availability.
In particular, a bound on the numerical size of a denominator is a different
contract. The t=0 boundary is allowed.

Choose a normalized dyadic Smith chart

```text
U K V = diag(h_1,...,h_r,0),
U in GL_m(D), V in GL_n(D),
0 < h_1 | h_2 | ... | h_r, all h_i odd.
```

Such a chart exists by the classical integer Smith theorem after clearing a
power-of-two denominator and absorbing powers of two into U. The factors h_i
are the positive odd parts of the ordinary integer Smith factors.

**The maximum t is the number of h_i dividing ab.** By divisibility order
these are an initial segment. Equivalently, for 1 <= t <= r a t-channel
boundary exists exactly when h_t divides ab. For t>r it is impossible.

Consequently, for 1 <= t <= r, the least positive odd q permitting qX and
qY over D is

```text
q_t = product over odd primes p of p^ceil(v_p(h_t)/2).
```

More strongly, every feasible common q is a multiple of q_t. For t=0 use
q_0=1; for t>r no q works. With a dyadic suffix only, b=1, the exact
one-sided denominator requirement is h_t | a. With a=b=1 the theorem
reduces to Ali Romman's #5615 criterion. That case and Smith reduction
are credited predecessors, not new results here.

## Attainment

Let h_t divide ab and take the first t rows and columns of the Smith chart.
Define

```text
X[i,:] = (b/h_i) U[i,:],
Y[:,i] = V[:,i]/b,             1 <= i <= t.
```

Then XKY=I_t entry by entry. Also aX has rows (ab/h_i)U[i,:], hence is
dyadic, and bY consists of columns of V. This constructs all channels
simultaneously. It needs no unproved lifting of a residue-ring solution.
The symmetric denominator formula follows by applying this construction
with a=b=q_t.

## Necessity, including rectangular maps and prime powers

Write A=aX and B=bY. The endpoint implies AKB=ab I_t. Substitute the
Smith chart and absorb its dyadic inverse factors into A and B. It suffices
to consider

```text
A' S B' = ab I_t, S=diag(h_1,...,h_r,0),
A',B' over D.
```

The rational rank of S gives t<=r. Suppose h_t does not divide ab. Choose
an odd prime p with v_p(h_t)>e=v_p(ab), and let k be the number of h_i
with v_p(h_i)<=e. Divisibility order gives k<t. The remaining entries of
S, including its zero entries, are divisible by p^(e+1).

Work in R=Z_(p), the rationals whose reduced denominators are not divisible
by p. The first k rows of B' form a k-by-t matrix. Since k<t, its rational
kernel contains a nonzero vector. Multiply that vector by a rational
scalar so every coordinate has nonnegative p-valuation and at least one
has valuation zero. The resulting vector c belongs to R^t, is primitive
at p, and is killed by those first k rows exactly.

It follows that S B' c belongs to p^(e+1) R^m: the first k coordinates
are zero, and each remaining nonzero diagonal coordinate has that
divisibility. Multiplying by A' preserves the inclusion. But ab c has
at least one coordinate of valuation exactly e. This contradicts
A' S B' c=ab c. Thus h_t must divide ab.

This argument permits arbitrary rectangular A',B' and arbitrary dyadic
mixing. Reduction only modulo p would miss obstructions when p divides
ab. The primitive-kernel step is why the full prime valuations matter.
No determinant-only bound or rational-rank relaxation substitutes for it.

## Example and use

For odd factors (1,27,675), the first, second and third common-denominator
requirements are respectively 1,9,45. A common q=15 admits only one
channel, even though it includes both relevant odd primes. The asymmetric
budgets (a,b)=(9,3) admit two, while (9,75) admit three. In every case
the boundary matrices above attain the count, even after non-diagonal
invertible dyadic basis changes.

The new result quantifies the finite exact-division debt when a helper
cut fails the dyadic unit criterion. It does not imply that either boundary
map is legal in a native word. If the proposed boundary needs dyadic
bases, productive target completions, ownership or physical carriers,
those conditions still require separate proofs. Odd-scalar support in
another package is not an automatic admission of these maps.

## Evidence limits and credit

The proof covers every finite dyadic matrix and every positive odd budget.
The executable accepts supplied, checked Smith charts with at most six
rows/columns, 256-bit input entries, and odd factors/budgets below 2^20.
Its finite witnesses and independent residue-ring oracle corroborate this
new contract. They do not prove the universal quantifiers or replay any
predecessor's scientific suite.

Credit Ali Romman #5615 for the saturated helper-cut pairing interface,
with #5599/#5602 helper splitting, #5609 cut pairings, #5611 completion,
Nick Petalas #5115 row preparation and their retained native/controller/
compiler lineage. Smith normal form, localization and elementary valuation
arithmetic are classical. No literature-wide priority for those methods,
physical supplier, new kappa or complete multiplication theorem is claimed.
