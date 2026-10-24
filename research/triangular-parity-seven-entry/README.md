# One full-support n=8 prefix stays below 3/2

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4802 records the symbol `(1, 1/8, 1/8, 1/16, 1/16, 1/16, -1/16, 0)`. Every
proper prefix is at most `3/2`. The right shear alone is `625/512`, the next
four proper prefixes are `21/16`, and the next five are `11/8`. Its open
question asks whether `(1, 1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)` keeps
that cap.

## Record

The tail `l1` is `1/8 + 6/16 = 1/2`. The schedule is the same nested order:
right shear, even child, Schur child, left shear, repeated inside every
child. There are 22 factors in the top even/odd basis and 21 proper prefixes.

The quotient is

```text
k = (1/8, 7/128, 105/2048, 1575/32768).
```

The bottom row of the right shear carries the tail of `z k`:

```text
1 + 1/8 + 7/128 + 105/2048 = 2521/2048.
```

That first proper prefix is strictly below `3/2`. The next nontrivial factor
is the even child's right shear, with a single entry `1/16`. The following
four proper prefixes have infinity norm `5/4`. The even grandchild's left
shear has entry `1/16` and lifts the next five proper prefixes to `21/16`.
The even child's left shear then lifts the running product to `23/16`, and
the remaining 10 proper prefixes stay there. The largest proper prefix is
`23/16`, so every proper prefix is at most `3/2`.

`2521/2048 < 5/4 < 21/16 < 23/16 < 3/2 < 9/4`. This is the first symbol in
this chain whose largest proper prefix is strictly below the one-level cap.
The completed product, which includes the final left shear, has infinity norm
`3/2`. Ten factors differ from `I`. The top left shear is the last of them,
so nine nontrivial factors sit in the proper prefixes.

The product of the 22 factors equals the even/odd reordering of the Toeplitz
matrix. The even child is `(1, 1/16, 1/16, 1/16)`. The Schur child is
`(1, 3/64, 49/1024, 735/16384)`.

## Not covered

- Any other `n = 8` symbol, including
  `(1, 1/8, 1/16, 1/16, 1/16, 1/16, 1/16, -1/16)`.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-seven-entry --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-seven-entry
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T20:23:24Z and again at
2026-10-22T20:25:49Z. Both fetches were that commit. The
selection is κ = `60403/20000000`. The pinned blobs of
`certificates/selected-result.json`, `GAUSSIAN.md`, and
`vendor/SHALLOW-TOEPLITZ.md` match the blobs used by #4802.

Overlap snapshot: open PRs fetched 2026-10-22T20:24:52Z (335 records) and
discussions fetched 2026-10-22T20:25:41Z (3761 records). Terms
`triangular-parity-seven-entry`, `2521/2048`, and
`1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16` returned this README and this TASK.
#4802's README asks this question and is not in this checkout. No matches is
not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/8, 1/16, 1/16, 1/16, 1/16, 1/16, -1/16)`
   keep every proper prefix at most `3/2`?** The positive full-support symbol
   has largest proper prefix `23/16`, strictly below the completed norm
   `3/2`. The degree-7 entry is the last odd coefficient. A negative sign
   changes the final left shear. Do not treat `p^100` as already spent.

## Credit

- The signed six-entry record, and this question, are #4802's.
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
