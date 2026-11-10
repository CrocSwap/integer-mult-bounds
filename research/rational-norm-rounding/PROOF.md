# Rational orthogonal maps and norm-contracting grid rounding

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and credit

Let U be a rational d-by-d orthogonal matrix, with d any positive finite
integer. Norms are Euclidean. The new result is the quantitative
arbitrary-dimensional obstruction and its existence classification. The
finite-set argument is the cited elementary lemma used in ywz65's
[PR2589](https://github.com/CrocSwap/integer-mult-bounds/pull/2589).
Its stronger two-real-dimensional dyadic-shell obstruction remains
predecessor work. No predecessor kernel is replayed or audited here.

For column j, write U e_j = a/q in lowest common denominator form, with
a in Z^d, q positive, and gcd(q,a_1,...,a_d)=1. Then ||a||^2=q^2.

**Radial error theorem.** If q>1, n is a positive integer not divisible by q,
and y in Z^d satisfies ||y||=n, then

    ||y - n U e_j||^2 = (2n/q) k >= 2n/q,
    k = nq - a dot y in Z_{>=1}.

**Classification.** A total injective F:Z^d -> Z^d satisfying

    ||F(x)|| <= ||x|| for every x,
    sup_x ||F(x)-Ux|| < infinity

exists if and only if U is a signed permutation matrix. F may be nonlinear.

**Finite ball version.** Let S_N={x in Z^d:||x||<=N}, with N>=1 an integer.
For every injective norm-nonincreasing F_N:S_N -> Z^d and every nonintegral
column a/q of U, put n=N if q does not divide N and n=N-1 otherwise. Then

    max_(x in S_N) ||F_N(x)-Ux||^2 >= 2n/q >= 2(N-1)/q.

At N=1 the chosen n is 1, since q>1. After rescaling to the complete h-grid
unit ball, h=1/N, the squared physical error is at least 2n h^2/q, hence at
least 2h(1-h)/q. For every fixed finite C, error <= C h is impossible at
every sufficiently fine dyadic grid. This is an Omega(sqrt(h)) necessary
error bound. Its attainability by a global map is not claimed.

## Proof of the radial error theorem

Since q is the least common denominator, q divides all n a_i if and only if
q divides n. For the nontrivial direction, multiply a Bezout integer
combination of q,a_1,...,a_d equal to 1 by n. Thus n a/q is not integral
for the stated n, so y differs from n a/q.

Expand the square using ||y||^2=n^2 and ||a||^2=q^2:

    ||y-na/q||^2
      = n^2+n^2-2n(a dot y)/q
      = (2n/q)(nq-a dot y).

The last parenthesis is an integer. The left side is strictly positive,
so this integer is at least 1. For q=5, a=(3,4), n=1, y=(0,1), equality is
attained. This shows the positive quantum cannot be increased uniformly
over these inputs, without asserting a sharp asymptotic approximation rate.

## Injection and contraction force exact norms

On a complete finite integer ball S_N, injection and norm nonincrease make
F_N a permutation of S_N. Summing ||x||^2 over this permutation, every
nonnegative difference ||x||^2-||F_N(x)||^2 has zero sum, so each is zero.
This is PR2589's finite-set argument, credited as predecessor work.

The same reasoning applies to the restriction of a total injective
norm-nonincreasing F on Z^d to S_N for every N. Thus F preserves every norm
exactly. For a nonintegral column, take n=1+tq for arbitrarily large integers
t. The radial theorem gives error at least sqrt(2n/q), contradicting a finite
uniform bound. If U has no nonintegral column, it is an integer orthogonal
matrix. Each integral unit column has one entry +/-1 and all others zero;
orthogonality puts these entries in different rows. Hence U is a signed
permutation. Conversely F(x)=Ux is an exact lattice bijection with zero error
and preserved norms for every signed permutation U.

For a finite S_N use the same norm-preservation argument and the stated
n, which is positive, at most N, at least N-1, and not divisible by q.
Evaluate at n e_j and apply the radial theorem. Rescaling proves the physical
bound. Since n tends to infinity with N, 2n/q eventually exceeds C^2. This
excludes squared error <= C^2 h^2 on every sufficiently fine grid.

## Exact restoration and rational complex maps

Fix the complete entrance state H of every other role, independently of x.
An exactly reversible computation with endpoint (x,H)->(F(x),H) makes F
injective on that fiber: equal data outputs would make the complete outputs
equal. Therefore the theorem applies under its complete-ball and same-grid
norm-nonincreasing hypotheses, regardless of helper count, initial dirt,
nonlinear computation, or use of different algorithms at each precision.
This fixed-fiber implication is also credited to PR2589.

A Gaussian-rational unitary matrix becomes rational orthogonal under
realification on real and imaginary coordinates. The result applies when
that complete real grid and Euclidean norm are the actual interface. It
does not exclude reversible rounding with outward norm slack. A real signed
permutation need not be complex linear, so no further complex classification
is asserted.

Retaining the original input, a data-dependent entrance helper, extra output
history, finer output grids, restricted reachable domains, or outward slack
changes a hypothesis. The result supplies no native implementation, physical
cost, precision allocation for an actual selected caller, or complete
multiplication theorem. All five selected framework assumptions remain.

## Executable scope

The verifier uses exact fractions and complete integer spheres for four
named matrices in dimensions two through four. It checks the error quantum
on every output of its declared sphere streams, for every nonintegral column
and allowed radius. It also enumerates every permutation of a seven-point
one-dimensional ball to corroborate the cited finite-set implication.
The 64-precision arithmetic certificates select actual near-boundary inputs;
they do not enumerate high-precision output spheres or execute a hypothetical
rounder. Finite corroboration is distinct from the written universal proof.
Independent human and formal proof-kernel review are unclaimed.
