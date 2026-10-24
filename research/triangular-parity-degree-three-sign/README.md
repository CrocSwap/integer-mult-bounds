# One degree-3 sign on n=8 stays at 23/16

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4820 records the symbol `(1, 1/8, 1/16, 1/16, -1/16, 1/16, 1/16, 1/16)`. Every
proper prefix is at most `3/2`, and the largest proper prefix is `23/16`. The
right shear alone is `2553/2048`, the next four proper prefixes are `5/4`, and
the next five are `21/16`. Its open question asks whether
`(1, 1/8, 1/16, -1/16, 1/16, 1/16, 1/16, 1/16)` keeps that cap. Degree 3 is
the second odd coefficient, so it enters the quotient at the second entry,
which the right shear keeps.

## Record

The tail `l1` is `1/8 + 6/16 = 1/2`. The schedule is the same nested order:
right shear, even child, Schur child, left shear, repeated inside every
child. There are 22 factors in the top even/odd basis and 21 proper prefixes.

The even child stays `(1, 1/16, 1/16, 1/16)`. Its split stays

```text
(1, 1/16), (1/16, 15/256), (1, 15/256).
```

The quotient is

```text
k = (1/8, -9/128, 121/2048, 1815/32768).
```

The positive full-support quotient has second entry `7/128`. This second
entry is `-9/128`. The right shear uses `z k` and keeps it. The bottom row is

```text
1 + 1/8 + 9/128 + 121/2048 = 2569/2048.
```

The first five proper prefixes are `2569/2048`. That value is strictly above
`5/4` and strictly below `21/16`. The positive opening was `2521/2048`, the
degree-4 opening was `2553/2048`, and the degree-5 opening was `2567/2048`.
The even child's right shear still has entry `1/16`, and the running norm
stays `2569/2048` through those five prefixes. The even grandchild stays
`(1, 1/16)`. Its left shear still has entry `1/16` and lifts the next four
proper prefixes to `21/16`.

The even child's Schur left shear still has entry `15/256` and infinity norm
`271/256`. On this symbol it lifts the running product from `21/16` to
`169/128`. That single proper prefix sits strictly between `21/16` and
`23/16`. The even child's left shear then carries

```text
(1, 0) = 1/16, (3, 0) = 15/256, (3, 2) = 1/16,
```

with infinity norm `287/256`, and lifts `169/128` to `23/16`.

The Schur child is

```text
(1, 3/64, 81/1024, 703/16384),
```

with split `(1, 81/1024)`, `(3/64, 2569/65536)`, `(1, 315/4096)`. The integer
`2569` is the opening numerator over `2048` and also this Schur quotient's
last numerator over `65536`. The Schur grandchild's left shear carries
`81/1024`, and the following left shear carries `315/4096`. The Schur child's
left shear carries `2569/65536` and has infinity norm `71177/65536`. Those
three factors sit inside the final plateau, and the running norm stays
`23/16`. The remaining proper prefixes after the even-child left shear are
`23/16`. The largest proper prefix is `23/16`, so every proper prefix is at
most `3/2`.

`5/4 < 2569/2048 < 21/16 < 169/128 < 23/16 < 3/2 < 9/4`. Ten factors differ
from `I`. The top left shear is the last of them and carries `1815/32768`,
so nine nontrivial factors sit in the proper prefixes. The completed product
of the 22 factors equals the even/odd reordering of the Toeplitz matrix. Its
infinity norm is `3/2`, because the tail absolute sum is still `1/2`.

## Not covered

- Any other `n = 8` symbol, including
  `(1, 1/8, -1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-degree-three-sign --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-degree-three-sign
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T21:01:32Z and again at
2026-10-22T21:04:03Z. Both fetches were that commit. The
selection is κ = `60403/20000000`. The pinned blobs of
`certificates/selected-result.json`, `GAUSSIAN.md`, and
`vendor/SHALLOW-TOEPLITZ.md` match the blobs used by #4820.

Overlap snapshot: open PRs fetched 2026-10-22T21:03:11Z (346 records) and
discussions fetched 2026-10-22T21:03:58Z (3777 records). Terms
`triangular-parity-degree-three-sign`, `1815/32768`, `169/128`, and
`1/8, 1/16, -1/16, 1/16, 1/16, 1/16, 1/16` returned this README, this TASK,
and #4820's DONE note, which asks this question. #4820's README is not in
this checkout. No matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/8, -1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`
   keep every proper prefix at most `3/2`?** The degree-3 sign changes the
   second quotient entry from `7/128` to `-9/128`. The right shear keeps that
   entry, so the opening rises to `2569/2048`, above `5/4`. The even child
   stays `(1, 1/16, 1/16, 1/16)`. Its Schur left shear, entry `15/256`, lifts
   `21/16` to `169/128`, and the even-child left shear then lifts `169/128`
   to `23/16`. The largest proper prefix stays `23/16`. Degree 2 is the even
   child's second coefficient. The even-child right shear uses the quotient
   entry that comes from it. Do not treat `p^100` as already spent.

## Credit

- The degree-4 sign, and this question, are #4820's.
- The degree-5 sign is #4816's.
- The degree-6 sign is #4815's.
- The signed full-support record is #4812's.
- The positive full-support record is #4811's.
- The signed six-entry record is #4802's.
- The positive six-entry record is #4800's.
- The signed five-entry record is #4799's.
- The positive five-entry record is #4798's.
- The signed four-entry record is #4796's.
- The positive four-entry record is #4782's.
- The three-entry record is #4706's.
- The signed two-entry record is #4705's.
- The odd-heavy record is #4704's.
- The equal-quarters record is #4702's.
- The one-half `n = 8` record is #4701's.
- The one-split `3/2` cap is #4699's.
- The triangular parity split is #4100's `SHALLOW-TOEPLITZ.md`.
- The shifted-interior citation of that compiler is #4100's `GAUSSIAN.md`.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
