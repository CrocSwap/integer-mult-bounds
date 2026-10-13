# Exactness of the modular full-rank fast path

This note justifies a verifier optimization, not a new multiplication bound.
The underlying finite obligation is the historical
[`audit_joint_frames.certificate()`](../../scripts/audit_joint_frames.py),
with the unchanged rational-rank routine in
[`audit_fused_block.py`](../../scripts/audit_fused_block.py). Source bytes and
Git blobs are pinned in `SOURCE.json`.

## Domain and statement

Let A be a finite rectangular matrix with entries in Q, represented exactly
as Python `int` or `Fraction` values. Assume `fallback(A)` returns its exact
rational rank. Then `screened_rank(A, fallback)` returns the same rank.
Empty and zero-width matrices have rank zero. Malformed and nonexact inputs
are explicitly rejected; the claim does not extend to the reference
routine's broader input-coercion behavior, such as floating-point input.

The modulus is the fixed prime 101. Its primality follows by testing the
primes 2, 3, 5 and 7, the primes at most sqrt(101). There is no probabilistic
rank estimate and no assumption that 101 preserves a deficient rank.

## Reduction and lower bound

If a reduced entry denominator is divisible by 101, the algorithm returns
`fallback(A)` immediately. Otherwise every denominator is invertible
modulo 101. The map a/b -> a b^(-1) modulo 101 is a ring homomorphism on
the subring of rationals whose denominators are coprime to 101. In
particular, it commutes with the determinant polynomial of every minor.

Gaussian elimination on the reduced matrix uses only row swaps and row
addition/scaling by nonzero residues. It therefore computes its rank over
F_101 exactly. The implementation scans columns from left to right, moves
a nonzero pivot into the next row, and eliminates below it. All earlier
pivot columns are zero in the remaining rows. Normalizing a temporary copy
of the pivot row, rather than storing it, does not affect elimination below
that row or the count of pivots.

If the modular rank reaches r = min(number of rows, number of columns),
some r by r minor is nonzero modulo 101. Its rational determinant cannot
be zero, since zero reduces to zero. Hence rank_Q(A) >= r; the shape bound
gives rank_Q(A) <= r. Returning r is exact for square, tall and wide matrices.

If the modular rank is smaller than r, it is only a lower bound. The
implementation discards that value and calls the unchanged exact fallback
on the original, unmodified matrix. This proves equivalence on the stated
domain for every matrix, independently of the finite test campaign.
The reference fallback is ordinary rational Gaussian elimination: its
invertible row operations preserve rank and its final nonzero echelon rows
count the rank. This is a written algebraic argument, not a Lean proof.

## Failure modes that the controls must distinguish

* `diag(101, 1)` has rational rank 2 and modular rank 1. Returning a
  deficient modular rank would be incorrect; the fallback is essential.
* `[[1/101, 1], [1, 101]]` has rational rank 1. Replacing an undefined
  modular denominator by 1 would create a false full-rank result.
* `[[1/2, 1/3], [3, 2]]` has rational rank 1. Reducing only numerators
  would falsely return rank 2.
* The all-ones 2 by 2 matrix has rank 1. Omitting elimination below the
  pivot would falsely return rank 2.

`test_kernel.py` deliberately implements each of these four wrong variants
and detects its wrong answer against a separate Leibniz-minor oracle.
Other controls cover row swaps, late pivots in rectangular matrices,
zero rows/width, large integers, fraction cancellation, exact input
validation, input preservation and source/expected-certificate corruption.

## What the replay establishes

The adapter changes only the underlying `rational_rank` called by the
historical audit's existing `rank` cache. It retains that cache, the
physical graph, every edge, every control matrix, exact source admission,
and the complete output comparison. Its extra modular work has no effect
on the mathematical control domain.

All 2,644 uncached rank calls in one complete certificate are individually
compared with the original routine. 752 reach full rank over F_101; 1,892
use the exact fallback. The complete certificate is also compared byte
for byte in every benchmark process. The unchanged eight-test historical
suite runs with each engine in a separate process. Neither test enumeration
nor a matching certificate proves the full multiplication theorem.

The historical fixed-boundary obstruction remains scoped to its original
active-factor matrices, external boundaries, side-role count and four
grouped central gates. This work does not reopen that search or extend its
domain. The selected #626/#543 suppliers, conditional kappa and all-size,
realization, hosting, residual, precision, tape and analytic assumptions
remain outside this optimization's verification scope.
