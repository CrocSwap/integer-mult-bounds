# Adjacent swaps miss mask (4)

The alphabet and the pair predicate are unchanged. A floor word on six
sources in characteristic 7 has length 42 and uses each source seven times.
`q_t` is the count vector of the first `t` letters. A pair `0 ≤ s ≤ t ≤ 41`
reads as a binary mask when every coordinate of `q_s + q_t` lies in
`{0, 1, 7, 8, 14}` and the two readings, that allowed set and reduction
modulo 7, agree. The mask bit is 1 exactly on `{1, 8}`. Mask `(4)` is the
weight-1 mask whose only 1 is source 4.

The block word is

```text
350122222224444444000000111111333333555555
```

with blocks `3, 5, 0, 1, 2^7, 4^7, 0^6, 1^6, 3^6, 5^6`. String indices are
0-based. Indices `11..17` are the seven `4`s and indices `18..23` are the
six following `0`s, so index 17 is the last `4` and index 18 is the
following `0`.

## One prefix moves

Let `w` be the word and let `w'` be `w` with indices `i` and `i+1`
exchanged, `0 ≤ i ≤ 40`. Write `a = w_i` and `b = w_{i+1}`. The prefix
`q_t` counts letters `w_0, ..., w_{t-1}`.

- If `t ≤ i`, those letters do not include index `i` or `i+1`.
- If `t ≥ i+2`, those letters include both indices.
- If `t = i+1`, the counted letters include index `i` and exclude `i+1`.

Thus `q'_t = q_t` for every `t ≠ i+1`. When `a ≠ b`,

```text
q'_{i+1} = q_{i+1} - e_a + e_b.
```

When `a = b`, the word is unchanged. There are 32 such indices and 9
indices where the letters differ. The nine are the block boundaries
`0, 1, 2, 3, 10, 17, 23, 29, 35`.

A pair whose endpoints both avoid `i+1` therefore has the same sum on `w`
and on `w'`. A pair that uses the endpoint `i+1` has the other endpoint
anywhere in `0..41`, so there are 42 such pairs. The domain of adjacent
transpositions is exactly the 41 index pairs. This count is the
completeness statement for the census.

## The unswapped word

`verify.py` evaluates all `42 · 43 / 2 = 903` pairs of `w`. None reads as
mask `(4)`. Every pair that avoids the moved prefix inherits that miss.

## The named boundary

Take `i = 17`, so `a = 4` and `b = 0`. The only moved prefix is `q_18`.
Direct count gives

```text
q_18  = (1, 1, 7, 1, 7, 1),
q'_18 = (2, 1, 7, 1, 6, 1) = q_18 - e_4 + e_0.
```

Suppose `q'_18 + r` reads as mask `(4)`. Coordinate 4 of the sum is
`6 + r_4`. It lies in `{1, 8}` and `r_4 ≥ 0`, so `r_4 = 2` and the sum is
8. The other five coordinates lie in `{0, 7, 14}`:

| source | `q'_18` | admissible `r` |
|---:|---:|---|
| 0 | 2 | 5 |
| 1 | 1 | 6 |
| 2 | 7 | 0 or 7 |
| 3 | 1 | 6 |
| 4 | 6 | 2 |
| 5 | 1 | 6 |

No other value in `0..7` works. The two admissible vectors are

```text
(5, 6, 0, 6, 2, 6),    sum 25,
(5, 6, 7, 6, 2, 6),    sum 32.
```

The coordinate sum of `q_u` is `u`, so the other endpoint would have to be
25 or 32. Both differ from 18, hence those prefixes are the original
prefixes. At `t = 25` and `t = 32` the original word already has source 0
and source 4 equal to 7, not 5 and 2. The doubled prefix `2 q'_18 =
(4, 2, 14, 2, 12, 2)` has coordinate 4 equal to 12, so the pair `(18, 18)`
is not mask `(4)` either.

Both admissible sums do read as mask `(4)`:

```text
q'_18 + (5, 6, 0, 6, 2, 6) = (7, 7, 7, 7, 8, 7),
q'_18 + (5, 6, 7, 6, 2, 6) = (7, 7, 14, 7, 8, 7).
```

The obstruction is that those prefixes do not occur, not that the predicate
rejects the shape. The same checker evaluates the 42 incident pairs and
finds none. It also records that exactly two readings change, both from a
nonzero mask to a non-reading: `(0, 18)` leaves `(0, 1, 3, 5)`, and
`(18, 41)` leaves `(0, 1, 3)`.

## The other eight boundaries

For each of the other eight indices the same one-prefix identity holds, and
the 42 incident pairs are evaluated with the same predicate. None reads as
mask `(4)`. The recorded changed prefixes are checked against
`q_{i+1} - e_a + e_b`. Equal-letter swaps are checked to be the original
word. Together with the 903-pair census of `w`, every adjacent transposition
misses mask `(4)`.

## What this does not say

The census does not range over non-adjacent transpositions, over other
floor words, or over the seventeen missed weight-3 masks. A depth-two block
needs every nonzero mask. Missing mask `(4)` on these 42 words does not
decide whether some other floor word realizes it, and it does not decide
characteristic 7. No supplier, consumer, or selected frontier changes. The
selected conditional κ remains `363005817/100000000000`.
