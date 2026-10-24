# One signed six-entry n=8 prefix stays at 3/2

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4800 records the symbol `(1, 1/8, 1/8, 1/16, 1/16, 1/16, 1/16, 0)`. Every
proper prefix is at most `3/2`. The right shear alone is `625/512`, the next
four proper prefixes are `21/16`, and the next five are `11/8`. Its open
question asks whether `(1, 1/8, 1/8, 1/16, 1/16, 1/16, -1/16, 0)` keeps that
cap.

## Record

The tail `l1` is `1/8 + 1/8 + 1/16 + 1/16 + 1/16 + 1/16 = 1/2`. The schedule
is the same nested order: right shear, even child, Schur child, left shear,
repeated inside every child. There are 22 factors in the top even/odd basis
and 21 proper prefixes.

The quotient is

```text
k = (1/8, 3/64, 25/512, -5/4096).
```

The right shear uses `z k` and drops the last quotient entry. Its bottom row
is therefore

```text
1 + 1/8 + 3/64 + 25/512 = 625/512,
```

the same opening value as the positive six-entry symbol. The next nontrivial
factor is the even child's right shear, with a single entry `1/8`. The
following four proper prefixes have infinity norm `21/16`. The even
grandchild's left shear has entry `1/16` and lifts the next five proper
prefixes to `11/8`. The even child's left shear carries the flipped
coefficient as the entry `-9/128` and lifts the running product to `3/2`.
The remaining 10 proper prefixes stay there. The largest is `3/2`, so every
proper prefix is at most `3/2`.

`625/512 < 21/16 < 11/8 < 3/2 < 9/4`. The sign changes the even child from
`(1, 1/8, 1/16, 1/16)` to `(1, 1/8, 1/16, -1/16)` and changes the last
quotient entry from `-69/4096` to `-5/4096`. Every proper-prefix infinity
norm matches the positive six-entry path. Ten factors differ from `I`. The
top left shear is the last of them, so nine nontrivial factors sit in the
proper prefixes.

The product of the 22 factors equals the even/odd reordering of the Toeplitz
matrix, whose infinity norm is also `3/2`. The Schur child is
`(1, 7/64, 25/512, -325/4096)`.

## Not covered

- Any other `n = 8` symbol, including
  `(1, 1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-signed-six-entry --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-signed-six-entry
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T20:18:04Z and again at
2026-10-22T20:20:29Z. Both fetches were that commit. The
selection is κ = `60403/20000000`. The pinned blobs of
`certificates/selected-result.json`, `GAUSSIAN.md`, and
`vendor/SHALLOW-TOEPLITZ.md` match the blobs used by #4800.

Overlap snapshot: open PRs fetched 2026-10-22T20:19:27Z (326 records) and
discussions fetched 2026-10-22T20:20:18Z (3754 records). Terms
`triangular-parity-signed-six-entry`, `-5/4096`, and
`1/8, 1/8, 1/16, 1/16, 1/16, -1/16` returned this README and this TASK.
#4800's README asks this question and is not in this checkout. No matches is
not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`
   keep every proper prefix at most `3/2`?** The signed degree-6 entry
   changes the even child's last coefficient, but every proper-prefix norm
   matches the positive six-entry path. The last coefficient is still zero.
   A nonzero degree-7 entry is a different support. Do not treat `p^100` as
   already spent.

## Credit

- The positive six-entry record, and this question, are #4800's.
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
