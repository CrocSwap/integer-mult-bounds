# One leading quarter on n=8 reaches 25/16

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4822 left the degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`
open. That symbol is one of the 128 patterns in the active claim
[discussioncomment-19132735](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735),
so this package does not record it. The claim leaves other magnitudes outside
its scope. This package records one such magnitude: replace the leading `1/8`
by `1/4` and keep the six positive sixteenths.

## Record

The symbol is `(1, 1/4, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`. The tail `l1`
is `1/4 + 6/16 = 5/8`. The schedule is the same nested order: right shear,
even child, Schur child, left shear, repeated inside every child. There are
22 factors in the top even/odd basis and 21 proper prefixes.

The even child stays `(1, 1/16, 1/16, 1/16)`. Its split stays

```text
(1, 1/16), (1/16, 15/256), (1, 15/256).
```

The quotient is

```text
k = (1/4, 3/64, 45/1024, 675/16384).
```

The right shear uses `z k` and drops the last entry. Its bottom row is

```text
1 + 1/4 + 3/64 + 45/1024 = 1373/1024.
```

That opening is strictly below `11/8`. The even child's right shear still has
entry `1/16` and lifts the next four proper prefixes to `11/8`. The even
grandchild stays `(1, 1/16)`. Its left shear still has entry `1/16` and lifts
the next five proper prefixes to `23/16`. The even child's Schur left shear
still has entry `15/256`, and the running norm stays `23/16` there. Those
first ten proper prefixes are at most `23/16`, which is strictly below `3/2`.

The even child's left shear then carries

```text
(1, 0) = 1/16, (3, 0) = 15/256, (3, 2) = 1/16,
```

with infinity norm `287/256`. It lifts the running product from `23/16` to
`25/16`. The value `25/16` is strictly above `3/2`. The remaining eleven
proper prefixes, including that step, equal `25/16`. The largest proper
prefix is `25/16`.

The Schur child is

```text
(1, 0, 9/256, 135/4096),
```

with split `(1, 9/256)`, `(0, 135/4096)`, `(1, 9/256)`. Its right shear is
the identity because the quotient starts at `0`. The later left shears carry
`9/256`, `9/256`, and `135/4096`, and the running norm stays `25/16`. Nine
factors differ from `I`. The top left shear is the last of them and carries
`675/16384`, so eight nontrivial factors sit in the proper prefixes. The
completed product of the 22 factors equals the even/odd reordering of the
Toeplitz matrix. Its infinity norm is `13/8`, because the tail absolute sum
is `5/8`.

`1373/1024 < 11/8 < 23/16 < 3/2 < 25/16 < 13/8 < 9/4`.

## Not covered

- The degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`, and the
  other 127 symbols in the claimed sign family.
- The symbol `(1, -1/4, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`.
- A bound for every tail of any fixed `l1`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-leading-quarter --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-leading-quarter
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T21:10:09Z and again at
2026-10-22T21:14:25Z. Both fetches were that commit. The
selection is κ = `60403/20000000`. The pinned blobs of
`certificates/selected-result.json`, `GAUSSIAN.md`, and
`vendor/SHALLOW-TOEPLITZ.md` are unchanged from #4822.

Overlap snapshot: open PRs fetched 2026-10-22T21:13:29Z (348 records) and
discussions fetched 2026-10-22T21:14:19Z (3787 records). Terms
`triangular-parity-leading-quarter`, `1373/1024`, `675/16384`, and
`1/4, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16` returned this README and this
TASK. No matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, -1/4, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`
   keep every proper prefix at most `25/16`?** The positive leading quarter
   has tail `l1 = 5/8`. Its largest proper prefix is `25/16`, strictly above
   `3/2`, and eleven proper prefixes equal `25/16`. The even-child left shear
   is the step that crosses `3/2`. The coefficient `-1/4` is outside the
   claimed sign family of coefficients `±1/8` and `±1/16`. Do not treat
   `p^100` as already spent.

## Credit

- The degree-2 sign, and the skipped degree-1 question, are #4822's.
- The degree-3 sign is #4821's.
- The degree-4 sign is #4820's.
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
