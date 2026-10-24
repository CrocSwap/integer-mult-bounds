# One signed four-entry n=8 prefix stays at 3/2

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4782 records the symbol `(1, 1/8, 1/8, 1/8, 1/8, 0, 0, 0)`. Every proper prefix
is at most `3/2`. The right shear alone is `647/512`, and the next four proper
prefixes are `11/8`. Its open question asks whether
`(1, 1/8, 1/8, 1/8, -1/8, 0, 0, 0)` keeps that cap.

## Record

The tail `l1` is `1/8 + 1/8 + 1/8 + 1/8 = 1/2`. The schedule is the same
nested order: right shear, even child, Schur child, left shear, repeated
inside every child. There are 22 factors in the top even/odd basis and 21
proper prefixes.

The quotient is

```text
k = (1/8, 7/64, 1/512, 55/4096).
```

The bottom row of the right shear carries the tail of `z k`:

```text
1 + 1/8 + 7/64 + 1/512 = 633/512.
```

That first proper prefix is strictly below the positive four-entry value
`647/512`, and strictly below `3/2`. The next nontrivial factor is the even
child's right shear, with a single entry `1/8`. The following four proper
prefixes have infinity norm `11/8`. The even grandchild's left shear has
entry `-1/8` and lifts the running product to `3/2`. The remaining 16 proper
prefixes stay there. The largest is `3/2`, so every proper prefix is at most
`3/2`.

`633/512 < 11/8 < 3/2 < 9/4`. The sign changes the even child from
`(1, 1/8, 1/8, 0)` to `(1, 1/8, -1/8, 0)` and lowers only the opening shear.
The later proper-prefix values match the positive four-entry path. Ten
factors differ from `I`. The top left shear is the last of them, so nine
nontrivial factors sit in the proper prefixes.

The product of the 22 factors equals the even/odd reordering of the Toeplitz
matrix, whose infinity norm is also `3/2`. The Schur child is
`(1, 7/64, -79/512, -57/4096)`.

## Not covered

- Any other `n = 8` symbol, including `(1, 1/8, 1/8, 1/8, 1/16, 1/16, 0, 0)`.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-signed-four-entry --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-signed-four-entry
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T19:58:09Z and again at
2026-10-22T20:01:45Z. Both fetches were that commit. The
selection is κ = `60403/20000000`. The pinned blobs of
`certificates/selected-result.json`, `GAUSSIAN.md`, and
`vendor/SHALLOW-TOEPLITZ.md` match the blobs used by #4782.

Overlap snapshot: open PRs fetched 2026-10-22T20:00:41Z (317 records) and
discussions fetched 2026-10-22T20:01:29Z (3734 records). Terms
`triangular-parity-signed-four-entry`, `633/512`, and
`1/8, 1/8, 1/8, -1/8` returned this README and this TASK. #4782's README
asks this question and is not in this checkout. No matches is not a novelty
certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/8, 1/8, 1/8, 1/16, 1/16, 0, 0)` keep every
   proper prefix at most `3/2`?** The signed four-entry symbol lowers only
   the opening shear, from `647/512` to `633/512`. The later proper prefixes
   still pass through `11/8` and then stay at `3/2`. A fifth nonzero tail
   entry is a different support. Do not treat `p^100` as already spent.

## Credit

- The positive four-entry record, and this question, are #4782's.
- The three-entry record is #4706's.
- The signed two-entry record is #4705's.
- The odd-heavy record is #4704's.
- The equal-quarters record is #4702's.
- The one-half `n = 8` record is #4701's.
- The one-split `3/2` cap is #4699's.
- The triangular parity split is #4100's `SHALLOW-TOEPLITZ.md`.
- The shifted-interior citation of that compiler is #4100's `GAUSSIAN.md`.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
