# Sharp carry envelope for the frame-506 matcher

This is a proof for one fixed integer matrix, plus one exhaustive census at
the prime 3. It uses the carry formula already stated in PR #4957. It does
not discharge the native compiler, change κ, or replace that paper's
conditional API implication.

## Source

The frozen bank
`research/bit-completed-backend-api/independent/inputs/frames.json` has
SHA-256 `d006b3bfe0c04afecfea7aecfa59dfe4298b99501c70da3938e40289bc2f5010`.
Frame 506 has rank 4. Its image rows `B` and kernel rows `A` are the source
blocks. Define

```text
S = [ B^T | A^T ].
```

The same package's word, SHA-256
`69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b`, records
helper 462 as starting at frame 0 and ending at frame 506. Reading that frame
gives the integer matrix

```text
S = [
  [0, 0, 0, 0, 1, 0, 0, 0],
  [0, 0, 1, 1, 0,-1, 0, 0],
  [0, 0, 1, 1, 0, 1, 0, 0],
  [0, 0, 0, 0, 0, 0, 1, 0],
  [0, 0, 1, 0, 0, 0, 0, 1],
  [2, 0, 0, 1, 0, 0, 0, 0],
  [0, 2, 0, 1, 0, 0, 0, 0],
  [0, 0,-1, 0, 0, 0, 0, 1]
].
```

Exact elimination gives `det S = -16` and

```text
S^{-1} = (1/4) * [
  [0,-1,-1, 0, 1, 2, 0,-1],
  [0,-1,-1, 0, 1, 0, 2,-1],
  [0, 0, 0, 0, 2, 0, 0,-2],
  [0, 2, 2, 0,-2, 0, 0, 2],
  [4, 0, 0, 0, 0, 0, 0, 0],
  [0,-2, 2, 0, 0, 0, 0, 0],
  [0, 0, 0, 4, 0, 0, 0, 0],
  [0, 0, 0, 0, 2, 0, 0, 2]
].
```

Every denominator divides 4, so `S` and `S^{-1}` are invertible at every odd
prime. Columns of `S`, indexed from 0, include `e0` in column 4 and `e3` in
column 6. Columns of `S^{-1}` include `e4` in column 0 and `e6` in column 3.

## Carry model

PR #4957, section 3, writes `g = g0 + q G1` and, for a fixed matcher `A`,

```text
h0 = (g0 A) mod q,
G1 |-> G1 A + (g0 A - h0) / q.
```

The second summand is the carry correction. A matrix position is counted when
that correction is nonzero. The published route envelope is 64 because an
8 by 8 matrix has 64 positions, and the same conservative number is copied to
the inverse. The pair envelope is 128. Both are upper bounds, not sharp counts.

For an integer dot `z` and an odd prime `q`, the representative `h0` is the
remainder of `z` in `{0,...,q-1}`, and the correction is the integer quotient.
For a dot in `Z[1/2]`, the same formula applies: `h0` is the unique integer in
`{0,...,q-1}` for which the difference is `q` times an element of `Z[1/2]`.
Uniqueness uses that `q` is odd. If two residues differed, their difference
would be a nonzero multiple of `q` inside `(-q, q)` and also an element of
`Z[1/2]`, which is impossible.

The quotient of `4 S^{-1}` is not this correction. Multiplying that integer
quotient by the unit `4^{-1}` still mixes the residue of the cleared
denominator with the carry. One finite row at `q = 5`,

```text
(4, 1, 0, 4, 2, 4, 4, 4),
```

has eight nonzero floors against `4 S^{-1}` and only five nonzero inverse
corrections. The two counts are different functions. This note uses the
formula above.

An implementation that expands `S` or `S^{-1}` as an elimination word can
tally intermediate carries differently. That comparison is open. The count
here is the closed-form correction, one entry per output coordinate.

## Structural zeros

Let `r` be any row with coordinates in `{0,...,q-1}`. Then `(r S)_4 = r_0`
and `(r S)_6 = r_3`, both already reduced, so those two forward corrections
are 0. Every forward row has at most six nonzero corrections, and an 8-row
low type has at most 48.

Let `u` be any such row used as the low type of the return. Then
`(u S^{-1})_0 = u_4` and `(u S^{-1})_3 = u_6`, both already reduced, so those
two return corrections are 0. Every return row has at most six nonzero
corrections, and the return matrix has at most 48. The pair has at most 96.

These zeros use the unit-column hypothesis. Replacing either unit column by
twice itself makes the corresponding correction nonzero on a row whose digit
there is `q-1`.

## Witness for every integer q ≥ 5

Let

```text
r(q) = (0, q-1, q-2, 0, q-1, q-1, q-1, 1).
```

Each coordinate lies in `{0,...,q-1}` once `q ≥ 5`. The eight dots against
the columns of `S` are

```text
2q-2, 2q-2, 3q-5, 4q-5, 0, -1, 0, q.
```

Their quotients and remainders are

```text
quotients  1, 1, 2, 3, 0, -1, 0, 1
remainders q-2, q-2, q-5, q-5, 0, q-1, 0, 0.
```

For each dot `a q + b` and claimed quotient `c`, the remainder
`(a-c) q + b` has one of the shapes `t` or `q+t` with `-5 ≤ t ≤ -1` or
`0 ≤ t ≤ 4`. Either shape lies in `{0,...,q-1}` for every integer `q ≥ 5`,
so the quotient is exactly `c`. Six of the eight are nonzero, and the two
zeros are the structural ones. The absolute values are at most 3, so reducing
the quotient modulo `q` does not turn it into zero.

The remainder row is the child low type

```text
u(q) = (q-2, q-2, q-5, q-5, 0, q-1, 0, 0).
```

Its dots against the columns of `S^{-1}` split as `h(q) + q c` with

```text
c = (0, -3/2, -1/2, 0, -1/2, -1/2, -1/2, -1/2)
```

and with `h(q)` equal to `0`, `q-1`, `q-2`, `0`, `q-1`, `q-1`, `q-1`, `1`
in that order. Each constant term of the dot is an integer in `[-5, 4]`, so
this split is forced, and `h(q)` stays inside `{0,...,q-1}`. Thus `c` is the
carry correction for every integer `q ≥ 5`. Six entries are nonzero. Each
nonzero value satisfies `2c ∈ {-3,-1}`, and no odd integer `q ≥ 5` divides 1
or 3, so the correction remains nonzero in the odd-prime coordinate ring.

Repeating `r(q)` on all eight low rows is a legal low type: each row's
correction depends only on that row. The forward matrix then has 48 nonzero
corrections and the return matrix has 48. Both structural ceilings are
attained, and the pair has 96 nonzero corrections.

The same arithmetic holds for every integer `q ≥ 5`, not only for primes.
The odd-prime hypothesis is the one inherited from the source, because the
denominators must be invertible. Every odd prime `q ≥ 5` is included.

## Prime 3

The domain `{0,1,2}^8` has `3^8 = 6561` rows. The base-3 enumeration visits
each row once. The maxima are forward 6, return 6, and joint 11. Repeating a
forward weight-6 row attains 48 forward corrections, and repeating a return
weight-6 row attains 48 return corrections. No row has joint weight 12. Rows
contribute independently, so the 8-row pair maximum at this prime is
`8 * 11 = 88`. The uniform ceiling 96 still holds and is not attained. This
census is exhaustive for that finite domain and for no other prime.

## What the envelope does not change

The 5 swaps, 5 unit scales and 14 shears, and the induced 40/40/112 high-row
counts, are unchanged. Nonzero carry corrections write the existing eight high
coordinates. The four structurally zero columns do not receive a correction
and do not allocate an owner. ROW restoration, tape, precision beyond the
denominator 4, the native compiler, and P1–P3 remain as PR #4957 left them.

PR #4957 already treats a finite carry constant as lower order once its
exponent gaps are positive. Replacing the envelope 128 by 96 does not move
those gaps and does not change the selected frontier `781451/250000000`.

## Controls

The zero low type has no nonzero correction, so 48 is a maximum, not a charge
on every low type. Doubling a structural unit column creates a correction on
a digit-`q-1` probe, so the zero uses that hypothesis. The cleared-denominator
floor model disagrees with the source formula on the finite row displayed
above.
