# Exact unit bounds by splitting orthogonal residuals

This contribution was produced by Nick Petalas. It is a scoped written
proof over Q(i), with a bounded exact implementation and finite
corroboration. It is not a complete multiplication theorem.

## Statement

For every E in Q(i)^(m by n), of rank r, there are s<=2r columns g_j in
Q(i)^m and rows a_j in Q(i)^n such that

    E = sum_j g_j a_j,
    ||g_j||_2 <= 1,
    ||a_j||_2 <= ||E||_2.

In fact, with G having columns g_j and A having rows a_j,

    GG* = P_col(E),       A = G*E.

Zero E has s=0. All nonzero emitted terms are retained. The bound 2r is
an upper bound, not an asserted global minimum. The coefficient row uses
an adjoint exactly once, in G*E. The standard coordinate factorization
uses m terms with the same unit bounds. The present bound depends on r
and is useful for low-rank displacements in a larger ambient space.

## Construction and proof

Use the exact nonzero orthogonal residuals v_1,...,v_r of E's columns,
as in Jose Manuel / jmbarrancoml's [PR4198](https://github.com/CrocSwap/integer-mult-bounds/pull/4198),
`research/rational-stein-generators/PROOF.md`, section 1. Write
n_k=v_k*v_k>0. The inherited projection identity is

    sum_k v_k v_k* / n_k = P_col(E).

For each k, choose z_k1,z_k2 in Q(i) with

    |z_k1|^2 + |z_k2|^2 = n_k.

Such a choice always exists. For example, clear a common positive integer
denominator D from v_k, and write v_k=w/D with Gaussian-integer w.
The positive integer N=w*w is a sum of four integer squares a^2+b^2+c^2+d^2
by Lagrange's theorem. Then z_k1=(a+bi)/D and z_k2=(c+di)/D work.
The classical theorem is not a new claim here; a primary formal source
is [Mathlib's SumFourSquares module](https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/SumFourSquares.html).
No Lean replay of this package is claimed.

Define, omitting each zero z,

    g_kl = v_k z_kl / n_k,       a_kl = g_kl* E.

There are at most two terms per residual, and

    sum_l g_kl g_kl*
      = v_k v_k* (sum_l |z_kl|^2) / n_k^2
      = v_k v_k* / n_k.

Thus GG*=P_col(E), and GA=GG*E=E. Also

    ||g_kl||_2^2 = |z_kl|^2/n_k <= 1,
    ||a_kl||_2 = ||g_kl* E||_2 <= ||g_kl||_2 ||E||_2 <= ||E||_2.

This proves the stated arbitrary-dimensional rational construction.
It also proves the stronger positive-semidefinite inequality

    E*E - a_kl* a_kl = E*(I-g_kl g_kl*)E >= 0.

If N is a sum of two integer squares, the implementation uses one term
for that residual. Its finite search finds such a representation whenever
one exists within the complete range 0..floor(sqrt(N)). Otherwise the
four-square representation gives two nonzero terms. No optimality of the
aggregate count is inferred from this per-residual choice.

## Stein and dirty-state interface

For a square E=T-ZTZ*, with Z the nilpotent lower shift, finite telescoping
gives the credited identity

    T = sum_(h=0)^(m-1) Z^h E (Z*)^h
      = sum_j L(g_j) U(a_j).

The second equality is the coefficient-row convention of PR4198. Each
new term can be passed to its existing compensated dirty-source macro,
with that macro's own legal near-identity normalizer and all four calls
paid. Summing complete macros restores the arbitrary source bank and adds
Tx to the arbitrary target bank. This is a logical exact interface only.
We have not run those child macros or implemented physical coefficient
pages in this package.

PR4198 uses r terms with row norms below 2||E||. Nick Petalas's
[PR6228](https://github.com/CrocSwap/integer-mult-bounds/pull/6228)
already gives r terms below (1+2^-p)||E|| and an exact-factor-one
obstruction in the rank-minimal class. Those results are credited
background, not replay targets. The new step here changes the term-count
contract and attains the exact factor one.

## Encoding and implementation scope

For a residual with rational components of height H, one common
denominator D uses at most 2mH bits. The Gaussian-integer coordinates of w
then use at most (2m+1)H+1 bits. Each four-square coordinate has magnitude
at most sqrt(N), so its bit length is bounded by half the bit length of N,
rounded upward. Forming g and a uses rational products and finite sums.
The construction therefore has finite rational output of polynomial
encoding length, using the inherited rational residual height bound.
This statement does not assert polynomial bit running time for our
exhaustive four-square enumerator.

The implementation first removes the common integer gcd of w. This only
changes D's rational scale and leaves N smaller. It accepts at most eight
rows and eight columns, input component height at most 256, and primitive
N<=65,536 at every residual. Capacity exhaustion rejects explicitly.
The theorem has no such finite limits; the implementation and its finite
checks do.

Every square loop is bounded by floor(sqrt(N))+1, its pair table has
N+1 entries, and its split loop has N+1 iterations. Matrix operations
have at most sixteen term columns and eight data rows or columns. There
is no recursion, external solver or predecessor execution. Managed Python
allocation is a Power of Ten rule 3 deviation, bounded by those capacities.
Warnings are treated as errors in every registered command. The source
and manifest checks are separate from mathematical verification.

## Limits

The construction can double the number of compensated generator macros.
It proves no decrease in total gate count, precision, memory, runtime or
recursive moment. Gaussian-rational coefficients may have odd denominators.
Exact coefficient preparation, rounded children, physical delivery,
restoration under rounding, compiler/native admission, stock/tape costs
and the outer theorem retain their existing obligations. The selected
frontier and all five framework assumptions are unchanged.
