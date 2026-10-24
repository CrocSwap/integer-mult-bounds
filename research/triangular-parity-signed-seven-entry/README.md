# One signed full-support n=8 prefix stays at 23/16

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4811 records the symbol `(1, 1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`. Every
proper prefix is at most `3/2`, and the largest proper prefix is `23/16`. The
right shear alone is `2521/2048`, the next four proper prefixes are `5/4`, and
the next five are `21/16`. Its open question asks whether
`(1, 1/8, 1/16, 1/16, 1/16, 1/16, 1/16, -1/16)` keeps that cap.

## Record

The tail `l1` is `1/8 + 6/16 = 1/2`. The schedule is the same nested order:
right shear, even child, Schur child, left shear, repeated inside every
child. There are 22 factors in the top even/odd basis and 21 proper prefixes.

The quotient is

```text
k = (1/8, 7/128, 105/2048, -2521/32768).
```

The right shear uses `z k` and drops the last quotient entry. Its bottom row
is therefore

```text
1 + 1/8 + 7/128 + 105/2048 = 2521/2048,
```

the same opening value as the positive full-support symbol. The next four
proper prefixes are `5/4`. The even grandchild's left shear has entry `1/16`
and lifts the next five proper prefixes to `21/16`. The even child's left
shear then lifts the running product to `23/16`, and the remaining 10 proper
prefixes stay there. The largest proper prefix is `23/16`, so every proper
prefix is at most `3/2`.

`2521/2048 < 5/4 < 21/16 < 23/16 < 3/2 < 9/4`. The sign changes only the last
quotient entry, from the positive value `1575/32768` to `-2521/32768`, and
the final left shear, which carries that entry. The even child stays
`(1, 1/16, 1/16, 1/16)`. The Schur child stays
`(1, 3/64, 49/1024, 735/16384)`. Every proper-prefix infinity norm matches
the positive full-support path. Ten factors differ from `I`. The top left
shear is the last of them, so nine nontrivial factors sit in the proper
prefixes.

The product of the 22 factors equals the even/odd reordering of the Toeplitz
matrix. Its infinity norm is `3/2`, the same completed value as the positive
symbol, because the tail absolute sum is still `1/2`.

## Not covered

- Any other `n = 8` symbol, including
  `(1, 1/8, 1/16, 1/16, 1/16, 1/16, -1/16, 1/16)`.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-signed-seven-entry --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-signed-seven-entry
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T20:29:11Z and again at
2026-10-22T20:31:33Z. Both fetches were that commit. The
selection is κ = `60403/20000000`. The pinned blobs of
`certificates/selected-result.json`, `GAUSSIAN.md`, and
`vendor/SHALLOW-TOEPLITZ.md` match the blobs used by #4811.

Overlap snapshot: open PRs fetched 2026-10-22T20:30:34Z (337 records) and
discussions fetched 2026-10-22T20:31:28Z (3770 records). Terms
`triangular-parity-signed-seven-entry`, `-2521/32768`, and
`1/8, 1/16, 1/16, 1/16, 1/16, 1/16, -1/16` returned this README and this
TASK. #4811's README asks this question and is not in this checkout. No
matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/8, 1/16, 1/16, 1/16, 1/16, -1/16, 1/16)`
   keep every proper prefix at most `3/2`?** The degree-7 sign changes only
   the last quotient entry and the final left shear. Every proper prefix
   matches the positive full-support path, whose largest value is `23/16`.
   The degree-6 entry is the even child's last coefficient. A negative sign
   changes that child. Do not treat `p^100` as already spent.

## Credit

- The positive full-support record, and this question, are #4811's.
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
