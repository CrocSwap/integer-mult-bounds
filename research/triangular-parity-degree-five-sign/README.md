# One degree-5 sign on n=8 stays at 23/16

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4815 records the symbol `(1, 1/8, 1/16, 1/16, 1/16, 1/16, -1/16, 1/16)`. Every
proper prefix is at most `3/2`, and the largest proper prefix is `23/16`. The
right shear alone is `2521/2048`, the next four proper prefixes are `5/4`, and
the next five are `21/16`. Its open question asks whether
`(1, 1/8, 1/16, 1/16, 1/16, -1/16, 1/16, 1/16)` keeps that cap. Degree 5 is
the third odd coefficient, so it enters the quotient before the entry the
right shear drops.

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
k = (1/8, 7/128, -151/2048, 1831/32768).
```

The positive full-support quotient has third entry `105/2048` and ends at
`1575/32768`. This third entry is `-151/2048`, and the quotient ends at
`1831/32768`. The right shear uses `z k` and keeps the third entry. Its
bottom row is

```text
1 + 1/8 + 7/128 + 151/2048 = 2567/2048.
```

The first five proper prefixes are `2567/2048`. That value is strictly above
`5/4`. The even child's right shear still has entry `1/16`, and the running
norm stays `2567/2048` through those five prefixes. The even grandchild stays
`(1, 1/16)`. Its left shear still has entry `1/16` and lifts the next five
proper prefixes to `21/16`.

The even child's left shear then carries

```text
(1, 0) = 1/16, (3, 0) = 15/256, (3, 2) = 1/16.
```

Its own infinity norm is `287/256`. It lifts the running product from
`21/16` to `23/16`. The Schur child is

```text
(1, 3/64, 49/1024, 1247/16384),
```

with split `(1, 49/1024)`, `(3/64, 4841/65536)`, `(1, 187/4096)`. The Schur
child's left shear carries `4841/65536` and has infinity norm `73449/65536`.
That factor is the last proper prefix, and the running norm stays `23/16`.
The remaining proper prefixes after the even-child left shear are `23/16`.
The largest proper prefix is `23/16`, so every proper prefix is at most `3/2`.

`5/4 < 2567/2048 < 21/16 < 23/16 < 3/2 < 9/4`. Ten factors differ from `I`.
The top left shear is the last of them and carries `1831/32768`, so nine
nontrivial factors sit in the proper prefixes. The completed product of the
22 factors equals the even/odd reordering of the Toeplitz matrix. Its
infinity norm is `3/2`, because the tail absolute sum is still `1/2`.

## Not covered

- Any other `n = 8` symbol, including
  `(1, 1/8, 1/16, 1/16, -1/16, 1/16, 1/16, 1/16)`.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-degree-five-sign --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-degree-five-sign
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T20:41:14Z and again at
2026-10-22T20:43:58Z. Both fetches were that commit. The
selection is κ = `60403/20000000`. The pinned blobs of
`certificates/selected-result.json`, `GAUSSIAN.md`, and
`vendor/SHALLOW-TOEPLITZ.md` match the blobs used by #4815.

Overlap snapshot: open PRs fetched 2026-10-22T20:43:03Z (341 records) and
discussions fetched 2026-10-22T20:43:52Z (3774 records). Terms
`triangular-parity-degree-five-sign`, `2567/2048`, `-151/2048`, and
`1/8, 1/16, 1/16, 1/16, -1/16, 1/16, 1/16` returned this README, this TASK,
and #4815's DONE note, which asks this question. #4815's README is not in
this checkout. No matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/8, 1/16, 1/16, -1/16, 1/16, 1/16, 1/16)`
   keep every proper prefix at most `3/2`?** The degree-5 sign changes the
   third quotient entry from `105/2048` to `-151/2048`. The right shear keeps
   that entry, so the opening rises from `2521/2048` to `2567/2048`, already
   above `5/4`. The even child stays `(1, 1/16, 1/16, 1/16)` and still
   supplies the later lifts to `21/16` and `23/16`. The largest proper prefix
   stays `23/16`. Degree 4 is that even child's middle coefficient. Do not
   treat `p^100` as already spent.

## Credit

- The degree-6 sign, and this question, are #4815's.
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
