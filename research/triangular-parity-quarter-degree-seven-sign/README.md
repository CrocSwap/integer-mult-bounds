# The last negative sixteenth changes only the final shear

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4872 recorded `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)` and left
the sign `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16)` open. The
linear coefficient `-1/4` is outside the 128-symbol claim
[discussioncomment-19132735](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735),
whose linear coefficient is `±1/8`. This package records this one sign.

## Record

The symbol is `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16)`. The tail
`l1` is `1/4 + 6/16 = 5/8`. The schedule is the same nested order: right
shear, even child, Schur child, left shear, repeated inside every child.
There are 22 factors in the top even/odd basis and 21 proper prefixes.

The flipped coefficient has odd degree, so the even child is unchanged from
#4872. It is `(1, -1/16, -1/16, -1/16)`, with split

```text
(1, -1/16), (-1/16, -17/256), (1, -17/256).
```

The quotient is

```text
k = (-1/4, -5/64, -85/1024, -1445/16384).
```

The first three entries match #4872. The last entry there was `603/16384`.
The right shear uses `z k` and drops that last entry, so the shear itself
matches #4872. Its bottom absolute row sum is `1445/1024`, strictly above
`11/8` and strictly below `23/16`. The even child's right shear does not lift
it, so the first five proper prefixes stay `1445/1024`.

The even grandchild, the even-child Schur complement, and the Schur child
also match #4872. The Schur child is

```text
(1, -1/8, -25/256, -425/4096).
```

The next four proper prefixes are `23/16`. The even-child Schur left shear
lifts one proper prefix to `187/128`, above `93/64` and below `3/2`. The
even-child left shear carries `-17/256` and lifts that value to `25/16`. The
remaining prefixes stay at `25/16`. No proper prefix exceeds `25/16`. Eleven
proper prefixes exceed `3/2`. The proper-prefix norm list matches #4872.

The last quotient coefficient does not appear in any proper-prefix factor.
It appears once, at `(7, 0)` of the final left shear, with value
`-1445/16384`. That factor has infinity norm `24565/16384`. Ten factors
differ from `I`, and the final shear is the last of them, so nine nontrivial
factors sit in the proper prefixes. The completed product of the 22 factors
equals the even/odd reordering of the Toeplitz matrix. Its infinity norm is
`13/8`, because the tail absolute sum is `5/8`.

`11/8 < 1445/1024 < 23/16 < 93/64 < 187/128 < 3/2 < 25/16 < 13/8 < 9/4`.

## Not covered

- The degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`, and the
  other 127 symbols in the claimed sign family.
- The symbol `(1, 1/4, -1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`.
- The other sign patterns with leading coefficient `-1/4`.
- A bound for every tail of any fixed `l1`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-degree-seven-sign --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-degree-seven-sign
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T22:42:57Z and again at
2026-10-22T22:45:15Z. Both fetches were that commit. The selection is κ =
`60403/20000000`. The pinned blobs of `certificates/selected-result.json`,
`GAUSSIAN.md`, and `vendor/SHALLOW-TOEPLITZ.md` are unchanged from #4872.

Overlap snapshot: open PRs fetched 2026-10-22T22:44:20Z (397 records) and
discussions fetched 2026-10-22T22:45:12Z (3897 records). Terms
`triangular-parity-quarter-degree-seven-sign`, `1445/16384`,
`24565/16384`, and
`-1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16` returned this README,
this TASK, and the #4872 DONE note that poses this question. The opening
`1445/1024` was left out of that search because #4869 and #4872 already
record it. Predecessor READMEs are absent from this checkout because the
branch starts at fetched main. No matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/4, -1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`
   keep every proper prefix at most `25/16`?** The successive sixteenth walk
   on the leading coefficient `-1/4` is complete. This last sign leaves the
   proper-prefix factors unchanged from #4872 and changes only the final
   left shear, to `-1445/16384`. The largest proper prefix stays `25/16`.
   The positive quarter in #4823 still has only the all-positive sixteenths.
   Its first sixteenth sign has linear coefficient `1/4`, outside the claimed
   family of `±1/8`. Do not treat `p^100` as already spent.

## Credit

- The degree-6 sign of the negative quarter is #4872's.
- The degree-5 sign of the negative quarter is #4869's.
- The degree-4 sixteenth of the negative quarter is #4838's.
- The degree-3 sixteenth of the negative quarter is #4837's.
- The first-sixteenth sign of the negative quarter is #4836's.
- The negative leading quarter is #4833's.
- The positive leading quarter is #4823's.
- The degree-2 sign, and the skipped degree-1 question, are #4822's.
- The degree-3 sign in the claimed family is #4821's.
- The degree-4 sign in the claimed family is #4820's.
- The degree-5 sign in the claimed family is #4816's.
- The degree-6 sign in the claimed family is #4815's.
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
