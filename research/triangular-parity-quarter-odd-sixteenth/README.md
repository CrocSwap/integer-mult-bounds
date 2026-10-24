# One odd sixteenth on the negative quarter returns to 185/128

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4836 recorded `(1, -1/4, -1/16, 1/16, 1/16, 1/16, 1/16, 1/16)` and left the
sign `(1, -1/4, -1/16, -1/16, 1/16, 1/16, 1/16, 1/16)` open. The linear
coefficient `-1/4` is outside the 128-symbol claim
[discussioncomment-19132735](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735),
whose linear coefficient is `±1/8`. This package records this one sign.

## Record

The symbol is `(1, -1/4, -1/16, -1/16, 1/16, 1/16, 1/16, 1/16)`. The tail
`l1` is `1/4 + 6/16 = 5/8`. The schedule is the same nested order: right
shear, even child, Schur child, left shear, repeated inside every child.
There are 22 factors in the top even/odd basis and 21 proper prefixes.

The flipped coefficient has odd degree, so the even child is unchanged from
#4836. It is `(1, -1/16, 1/16, 1/16)`, with split

```text
(1, 1/16), (-1/16, 17/256), (1, 15/256).
```

The quotient is

```text
k = (-1/4, -5/64, 75/1024, 1435/16384).
```

The right shear uses `z k` and drops the last entry. Its bottom absolute row
sum is

```text
1 + 1/4 + 5/64 + 75/1024 = 1435/1024.
```

The entries on that shear are `-1/4` at `(1, 4)`, `(2, 5)`, and `(3, 6)`,
`-5/64` at `(2, 4)` and `(3, 5)`, and `75/1024` at `(3, 4)`. The absolute
opening matches #4833, while the signed `5/64` entries do not: there they
were positive. This opening is strictly above #4836's `1411/1024` and
strictly above `11/8`. It is strictly below `23/16`. The even child's right
shear still has entry `-1/16` and does not lift the running norm, so the
first five proper prefixes stay `1435/1024`.

The even grandchild stays `(1, 1/16)`. Its left shear still has entry `1/16`
and lifts the next four proper prefixes to `23/16`. The even child's Schur
left shear still has entry `15/256`, with factor norm `271/256`. On this
opening it lifts `23/16` to `185/128`. That value sits strictly between
`23/16` and `3/2`. The same factor left the running norm at `23/16` on the
`1411/1024` opening in #4836.

The even child's left shear then carries

```text
(1, 0) = -1/16, (3, 0) = 17/256, (3, 2) = -1/16,
```

with infinity norm `289/256`. It lifts the running product from `185/128` to
`25/16`. The value `25/16` is strictly above `3/2`. The remaining eleven
proper prefixes, including that step, equal `25/16`. No proper prefix exceeds
`25/16`. The largest proper prefix is `25/16`. Eleven proper prefixes exceed
`3/2`. The proper-prefix norms are `1435/1024` five times, `23/16` four
times, `185/128` once, and `25/16` eleven times. That is the same list as
#4833. The factors are not the same list.

The Schur child is

```text
(1, -1/8, 7/256, 375/4096),
```

with split `(1, 7/256)`, `(-1/8, 389/4096)`, `(1, 3/256)`. Its right shear
carries `-1/8` and has factor norm `9/8`. The running norm is already
`25/16` before that shear, and it stays `25/16`. The later shears carry
`7/256`, `3/256`, and the pair `-1/8`, `389/4096`. That last proper-prefix
factor has infinity norm `4997/4096` and still leaves the running norm at
`25/16`. Ten factors differ from `I`. The top left shear is the last of them
and carries `1435/16384` at `(7, 0)`, so nine nontrivial factors sit in the
proper prefixes. The completed product of the 22 factors equals the even/odd
reordering of the Toeplitz matrix. Its infinity norm is `13/8`, because the
tail absolute sum is `5/8`.

`11/8 < 1411/1024 < 1435/1024 < 23/16 < 185/128 < 3/2 < 25/16 < 13/8 < 9/4`.

## Not covered

- The degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`, and the
  other 127 symbols in the claimed sign family.
- The symbol `(1, -1/4, -1/16, -1/16, -1/16, 1/16, 1/16, 1/16)`.
- A bound for every tail of any fixed `l1`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-odd-sixteenth --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-odd-sixteenth
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T21:29:35Z and again at
2026-10-22T21:32:11Z. Both fetches were that commit. The selection is κ =
`60403/20000000`. The pinned blobs of `certificates/selected-result.json`,
`GAUSSIAN.md`, and `vendor/SHALLOW-TOEPLITZ.md` are unchanged from #4836.

Overlap snapshot: open PRs fetched 2026-10-22T21:31:07Z (362 records) and
discussions fetched 2026-10-22T21:32:06Z (3811 records). Terms
`triangular-parity-quarter-odd-sixteenth`, `1435/16384`, `4997/4096`,
`389/4096`, and
`-1/4, -1/16, -1/16, 1/16, 1/16, 1/16, 1/16` returned this README, this
TASK, and the #4836 DONE note that poses this question. The opening
`1435/1024` was left out of that search because #4833 already records it.
Predecessor READMEs are absent from this checkout because the branch starts
at fetched main. No matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, -1/4, -1/16, -1/16, -1/16, 1/16, 1/16, 1/16)`
   keep every proper prefix at most `25/16`?** Flipping the degree-3
   sixteenth restores the proper-prefix path of the negative quarter:
   `1435/1024` five times, `23/16` four times, `185/128` once, then `25/16`.
   The even child still matches the previous sign. The Schur child changes,
   and its right shear is still not the identity. The next sixteenth is
   even, so it changes that even child. The linear coefficient stays `-1/4`,
   outside the claimed family of `±1/8`. Do not treat `p^100` as already
   spent.

## Credit

- The first-sixteenth sign of the negative quarter is #4836's.
- The negative leading quarter is #4833's.
- The positive leading quarter is #4823's.
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
