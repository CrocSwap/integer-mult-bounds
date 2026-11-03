# Exact multiplicities for two heterogeneous tensor cuts

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and cited premises

Let D = Z[1/2]. For a finite matrix H over D, let r(H) be its rational
rank and c(H) its unit-channel capacity, the largest h for which dyadic
matrices X,Y satisfy XHY = I_h. The cited single-cut theorem of Ali
Romman, [PR5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615),
and tensor formula of Nick Petalas,
[PR5882](https://github.com/CrocSwap/integer-mult-bounds/pull/5882), give

    c(H) = min over odd primes p of rank(H mod p),
    c(tensor_i H_i) = min_p product_i rank(H_i mod p).

These are premises, not new claims or replay targets here. zxv's
[PR6054](https://github.com/CrocSwap/integer-mult-bounds/pull/6054) proves
that exactly factored saturated causal cuts have these complete tensor
modules, including arbitrary linear combinations across tensor coordinates.
That implication is also a cited premise. Applying the present theorem to
physical cuts requires all of its hypotheses and the unpaid physical work.

Define the defect set Delta(H) to consist of odd primes p at which
rank(H mod p) < r(H). This set is finite. Indeed, clear powers of two and
take one nonzero maximal minor; every defective prime divides its nonzero
integer numerator. Matrices may be rectangular.

Fix K,L with

    r(K)=r, c(K)=c, r(L)=s, c(L)=d,
    0 < c < r, 0 < d < s, Delta(K) intersect Delta(L) empty.

The objective is unit-channel density, capacity divided by rational rank,
over every tensor word of a prescribed positive length n using these two
types. No rank budget, per-type charge or productive-target weighting is
included. Optimizing density need not optimize absolute capacity or a
complete supplier invoice.

## Fixed multiplicities

If the word contains a copies of K and b=n-a copies of L, then its capacity
and rational rank are exactly

    C(a,b) = min(c^a s^b, r^a d^b),
    R(a,b) = r^a s^b.

For p in Delta(K), L has full rank s. The minimum prime-rank product in
that set is c^a s^b, since some prime attains c. For p in Delta(L) the
minimum is r^a d^b. At every other prime the product is r^a s^b, which is
at least both displayed quantities. The same formula includes a=0 or b=0,
using x^0=1. This proves the claim from the cited tensor formula.

Order does not matter: swapping tensor factors gives invertible integral
row and column permutation matrices. Every ordered word with the same
multiplicities therefore has the same capacity and rank. This statement
does not give free physical routing between different tensor orders.

Put u=c/r and v=d/s, both strictly between zero and one. The exact density is

    rho(a) = min(u^a, v^(n-a)),       0 <= a <= n.

## The new finite-length optimization theorem

Set A=r/c>1 and B=s/d>1. There is a unique integer k in {0,...,n-1} with

    A^k <= B^(n-k),
    A^(k+1) > B^(n-k-1).

The optimal density and all attaining first-type counts are

    rho_star = max(v^(n-k), u^(k+1)),

    { k     if v^(n-k) = rho_star }
      union
    { k+1   if u^(k+1) = rho_star }.

In particular there are either one or two optimal counts. Every tensor
order with an optimal count attains the optimum; no other count does.

Proof: A^a / B^(n-a) strictly increases with integer a, starts below one at
a=0 and ends above one at a=n. Thus k exists and is unique. For a<=k,
u^a>=v^(n-a), so rho(a)=v^(n-a), a strictly increasing function of a.
For a>=k+1, rho(a)=u^a, a strictly decreasing function of a. Consequently
only k and k+1 can maximize it, and their values are the two displayed
quantities. Strict monotonicity excludes every other count, including
when those two values tie. This proves the theorem for every positive n.

The crossing can be found without logarithms. Test

    r^a d^(n-a) <= c^a s^(n-a)

by integer arithmetic. Binary search maintains a true left endpoint zero
and false right endpoint n. Each iteration at least halves the interval
up to rounding. At most bit_length(n)+1 iterations leave adjacent
endpoints. `schedule.py` implements precisely this predicate and compares
the two surviving densities as exact fractions. Its finite interface
limits ranks and length to 4096; the written theorem has no such bound.

## A strictly sharper heterogeneous catalogue bound

Take the algebraic pairings

    K = diag(1,1,3),      L = diag(1,5).

Their ranks/capacities are (r,c)=(3,2) and (s,d)=(2,1), with defect sets
{3} and {5}. At n=4, k=2 because

    (3/2)^2 <= 2^2,       (3/2)^3 > 2^1.

The unique optimal count is a=3, b=1, with density 8/27, capacity 16 and
rational rank 54. The equal-count choice has density 1/4 and capacity 9
at rank 36. Thus balancing multiplicities fails to maximize density.
The difference in rational ranks is retained explicitly.

PR6054's general two-type bound uses theta=max(2/3,1/2)=2/3 and gives
rho <= theta^ceil(4/2)=4/9. The new sharp bound 8/27 is strictly smaller,
and is attained by every word with three K factors and one L factor.
This is an improvement of a scoped algebraic catalogue bound, with no
claim that either diagonal pairing is a selected productive native cut.

## Hypothesis and verification limits

Disjoint defects cannot be inferred from capacities alone. With
K=L=diag(1,3), both individual capacities are one at rank two. Their
two-factor capacity is one at rank four, whereas the disjoint-defect
formula would give density one half. The actual density is one quarter.
The verifier retains this counterexample as a hypothesis control.

The proof is a written all-length argument conditional on the cited
capacity and module theorems. It is not a proof-kernel formalization.
Finite tests enumerate the stated bounded domains only. No predecessor
theorem is independently audited, reproduced or certified here.

All physical basis preparation and inverses, common native charts,
chronology, carriers, delivery, restoration, precision/growth, stock,
tape, independent productive targets, compiler and outer obligations
remain separate. No complete signed bill, new supplier, new kappa or
complete multiplication theorem follows from this density optimum.
