# Exact determinant-prefix reuse

## Claim and contract

`PrefixDeterminant(reference_det)` returns the exact determinant of a square integer matrix.
The claim assumes that `reference_det` returns an exact determinant when the fallback calls it.
The selected reference is `det` in the pinned `prime_witnesses.py` source.
The kernel accepts built-in Python integers and rejects other scalar types.
The empty matrix has determinant 1.

This result concerns determinant evaluation only.
It does not prove the surrounding mathematical theorem or change its parameters.
It does not independently verify the selected word, frame generation, or prime range.

## Identity over the integers

Let `A` be an `n` by `n` integer matrix.
Let `D_r` denote its leading principal determinant of order `r`, with `D_0 = 1`.
For indices `i,j >= k`, define the bordered minor:

```text
P_k(i,j) = det A[(0,...,k-1,i), (0,...,k-1,j)].
P_0(i,j) = A[i,j].
P_k(k,k) = D_(k+1).
```

The determinant identity of Sylvester gives:

```text
D_k P_(k+1)(i,j)
    = D_(k+1) P_k(i,j) - P_k(i,k) P_k(k,j),
    for i,j > k.
```

One proof first assumes that the leading block of order `k` is invertible over the rationals.
Expand the bordered minors through the Schur complement of that block.
The displayed identity becomes the formula for a determinant of order 2.
Both sides are polynomials in the entries of `A`.
The polynomial identity therefore holds for every integer matrix, including singular matrices.
For `k=0`, it is directly the same formula with the empty determinant equal to 1.

## Elimination invariant

Before elimination step `k`, each active entry `work[i][j]` equals `P_k(i,j)`.
The variable `previous` equals `D_k`.
The initialization satisfies these statements at `k=0`.
The pivot equals `D_(k+1)`.

When the pivot is nonzero, the kernel applies the displayed identity to each trailing entry.
The divisor `D_k` is nonzero because each earlier pivot is nonzero.
The identity proves that each division has zero remainder and preserves the invariant.
The kernel checks divisibility with `divmod` and raises `ArithmeticError` for a nonzero remainder.
It also explicitly rejects a zero divisor.
These checks remain active under `python -O`.

The kernel records each pivot as the corresponding leading principal determinant.
After the final elimination, `work[n-1][n-1]` equals `D_n`.
The kernel records this value as well.
For `n=1`, the only entry directly equals the determinant.
This argument does not require symmetry, positive definiteness, or positive entries.
Negative pivots and negative determinants cause no change to the identity.

## Zero pivots and singular matrices

A zero elimination pivot remains a valid value of its leading principal determinant.
However, subsequent elimination can require division by that zero value.
The kernel stops before this can occur.
It calls the supplied reference on a separate copy of the full requested matrix.
It retains only the leading minors already proved by the invariant and the returned full determinant.
It does not infer any later leading minor from the interrupted pass.

The fallback covers nonsingular matrices with a singular leading block, including matrices that require row swaps.
It also covers singular matrices with an early zero pivot.
A zero final entry needs no further elimination or division and directly gives determinant zero.

## Cache validity and bounds

Each key is an immutable tuple of rows containing every entry of one matrix.
Python dictionary lookup checks full key equality, even when hashes collide.
Thus, a hit identifies precisely the matrix whose determinant the kernel records.
The kernel does not use mutable object identities as keys.
Later mutation of the caller's matrix cannot create a stale hit.
The kernel also leaves the caller's matrix unchanged.

A miss discards the previous cache and creates one cache for the requested matrix.
A hit retains this cache, so requests for successive prefixes reuse the same elimination.
The cache stores at most `n` determinants after a miss of dimension `n`.
The empty matrix creates no cache entries.
An interrupted pass stores fewer prefixes plus the full determinant, still at most `n` entries.

The bound counts entries, not bytes.
The complete prefix keys contain at most a constant times `n^3` scalar references in total.
Integer bit lengths and arithmetic costs depend on the input.
The uncached elimination uses at most a constant times `n^3` exact arithmetic operations.
This statement is not a constant-time or unit-bit-cost claim.

## Scope of equivalence

For each supported input, a cache hit returns a previously established exact determinant.
On a miss, the invariant proves the result unless the reference handles a zero pivot.
Under the reference contract, that fallback also returns the exact determinant.
These cases establish equivalence to the reference for square integer inputs.

The optimization helps when the caller requests a full matrix before its leading prefixes.
The selected Gram checker uses this order with its positivity option.
The kernel does not change rank, annihilator, factor, residual, or positivity checks.
Correct determinant values alone do not establish the correctness of those surrounding checks.
The cache and counters support sequential calls; the implementation makes no thread-safety claim.
