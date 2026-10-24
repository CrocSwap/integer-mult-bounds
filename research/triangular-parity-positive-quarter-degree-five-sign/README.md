# One degree-5 sign on the positive quarter opens at 1379/1024

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4887 recorded `(1, 1/4, -1/16, -1/16, -1/16, 1/16, 1/16, 1/16)` and left the
next sixteenth open:

```text
(1, 1/4, -1/16, -1/16, -1/16, -1/16, 1/16, 1/16).
```

The linear coefficient `1/4` is outside the 128-symbol claim
[discussioncomment-19132735](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735),
whose linear coefficient is `±1/8`. This package records this one sign.

## Record

The tail `l1` is `1/4 + 6/16 = 5/8`. The schedule is the same nested order:
right shear, even child, Schur child, left shear, repeated inside every
child. There are 22 factors in the top even/odd basis and 21 proper prefixes.

The flipped coefficient has odd degree, so the even child stays. It is

```text
(1, -1/16, -1/16, 1/16),
```

the same even child as #4887 and #4838, with split

```text
(1, -1/16), (-1/16, 15/256), (1, -17/256).
```

The quotient changes. It is

```text
k = (1/4, -3/64, -51/1024, 669/16384).
```

The right shear uses `z k` and drops the last entry. Its bottom absolute row
sum is

```text
1 + 1/4 + 3/64 + 51/1024 = 1379/1024.
```

The entries on that shear are `1/4` at `(1, 4)`, `(2, 5)`, and `(3, 6)`,
`-3/64` at `(2, 4)` and `(3, 5)`, and `-51/1024` at `(3, 4)`. This opening is
strictly above #4886's `1373/1024` and strictly below both #4838's
`1403/1024` and #4887's `1405/1024`. It is strictly below `11/8`. The even
child's right shear has entry `-1/16` and lifts this opening, so the next
four proper prefixes are `11/8`.

The even grandchild stays `(1, -1/16)`. Its left shear has entry `-1/16` and
lifts the next five proper prefixes to `23/16`. The even child's Schur left
shear has entry `-17/256`, with factor norm `273/256`. The running norm is
already `23/16`, and this factor leaves it at `23/16`. There is no `93/64`
prefix, and no `185/128` prefix.

The even child's left shear then carries

```text
(1, 0) = -1/16, (3, 0) = 15/256, (3, 2) = -1/16,
```

with infinity norm `287/256`. It lifts the running product from `23/16` to
`25/16`. The value `25/16` is strictly above `3/2`. The remaining eleven
proper prefixes, including that step, equal `25/16`. No proper prefix exceeds
`25/16`. The largest proper prefix is `25/16`. Eleven proper prefixes exceed
`3/2`.

The Schur child is

```text
(1, -1/8, -9/256, 359/4096).
```

Its first three coefficients match #4887. The degree-3 coefficient changes
from `103/4096` to `359/4096`. The split is `(1, -9/256)`,
`(-1/8, 341/4096)`, `(1, -13/256)`. The right shear still carries `-1/8` and
has factor norm `9/8`. The shears that carry `-9/256` and `-13/256` match
#4887, with factor norms `265/256` and `269/256`. The Schur left shear
changes: it carries the pair `-1/8`, `341/4096`, with infinity norm
`4949/4096`. The running norm is already `25/16` before each of these
shears, and it stays `25/16`. Ten factors differ from `I`. The top left
shear is the last of them and carries `669/16384` at `(7, 0)`, with factor
norm `22733/16384`. That entry is absent from every proper-prefix factor.
Nine nontrivial factors sit in the proper prefixes. The completed product of
the 22 factors equals the even/odd reordering of the Toeplitz matrix. Its
infinity norm is `13/8`, because the tail absolute sum is `5/8`.

`1373/1024 < 1379/1024 < 1403/1024 < 1405/1024 < 11/8 < 1411/1024 < 1413/1024 < 23/16 < 185/128 < 93/64 < 3/2 < 25/16 < 13/8 < 9/4`.

After the opening, the proper-prefix norm list matches #4887: `11/8` four
times, `23/16` five times, and `25/16` eleven times. The opening factor and
the Schur left shear do not match.

## Not covered

- The degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`, and the
  other 127 symbols in the claimed sign family.
- The symbol `(1, 1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)`.
- A bound for every tail of any fixed `l1`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-positive-quarter-degree-five-sign --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-positive-quarter-degree-five-sign
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream fetches at 2026-10-22T23:03:47Z and 2026-10-22T23:06:04Z were that
commit. The pinned input blobs were unchanged. The selection is κ =
`60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T23:05:12Z (411 records) and
discussions fetched 2026-10-22T23:06:00Z (3925 records). Terms
`triangular-parity-positive-quarter-degree-five-sign`, `1379/1024`,
`669/16384`, `22733/16384`, and
`1/4, -1/16, -1/16, -1/16, -1/16, 1/16, 1/16` reported 6 matches: this
README, this TASK, the #4887 DONE that leaves this symbol open, and the
negative-quarter degree-5 sign in #4869 (its phrase
`-1/4, -1/16, -1/16, -1/16, -1/16, 1/16, ...` contains the searched token
as a substring). No other package records this positive leading coefficient.
No matches is not a novelty certificate. Predecessor READMEs for #4869
and #4887 are not in this checkout; this branch starts at fetched main.

## Open next questions

1. **Does the `n = 8` symbol `(1, 1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)`
   keep every proper prefix at most `25/16`?** Flipping the degree-5
   sixteenth leaves the even child at `(1, -1/16, -1/16, 1/16)`. The opening
   falls from `1405/1024` to `1379/1024`, still below `11/8`. The even right
   shear still lifts that opening to `11/8`. The `-17/256` factor still does
   not reach `93/64`. The largest proper prefix stays `25/16`. The next
   sixteenth has even degree, so the even child changes. The linear
   coefficient stays `1/4`, outside the claimed family of `±1/8`. Do not
   treat `p^100` as already spent.

## Credit

- The even sixteenth of the positive quarter is #4887's.
- The odd sixteenth of the positive quarter is #4886's.
- The first sixteenth of the positive quarter is #4884's.
- The last sixteenth of the negative quarter is #4877's.
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
