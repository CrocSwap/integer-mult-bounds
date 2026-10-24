# One degree-5 sign on the negative quarter reaches 187/128

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4838 recorded `(1, -1/4, -1/16, -1/16, -1/16, 1/16, 1/16, 1/16)` and left the
sign `(1, -1/4, -1/16, -1/16, -1/16, -1/16, 1/16, 1/16)` open. The linear
coefficient `-1/4` is outside the 128-symbol claim
[discussioncomment-19132735](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735),
whose linear coefficient is `±1/8`. This package records this one sign. It is
not the degree-5 sign of that claimed family.

## Record

The symbol is `(1, -1/4, -1/16, -1/16, -1/16, -1/16, 1/16, 1/16)`. The tail
`l1` is `1/4 + 6/16 = 5/8`. The schedule is the same nested order: right
shear, even child, Schur child, left shear, repeated inside every child.
There are 22 factors in the top even/odd basis and 21 proper prefixes.

The flipped coefficient has odd degree, so the even child is unchanged from
#4838. It is `(1, -1/16, -1/16, 1/16)`, with split

```text
(1, -1/16), (-1/16, 15/256), (1, -17/256).
```

The quotient is

```text
k = (-1/4, -5/64, -85/1024, 1115/16384).
```

The right shear uses `z k` and drops the last entry. Its bottom absolute row
sum is

```text
1 + 1/4 + 5/64 + 85/1024 = 1445/1024.
```

The entries on that shear are `-1/4` at `(1, 4)`, `(2, 5)`, and `(3, 6)`,
`-5/64` at `(2, 4)` and `(3, 5)`, and `-85/1024` at `(3, 4)`. This opening is
strictly above `11/8` and strictly above #4833's `1435/1024`. It is strictly
below `23/16`. The even child's right shear still has entry `-1/16` and does
not lift the running norm, so the first five proper prefixes stay
`1445/1024`. On the lower opening in #4838, that same shear did lift the
norm to `11/8`.

The even grandchild stays `(1, -1/16)`. Its left shear still has entry
`-1/16` and lifts the next four proper prefixes to `23/16`. The even child's
Schur left shear still has entry `-17/256`, with factor norm `273/256`. On
this opening it lifts `23/16` to `187/128`. That value is one step above
`93/64` and strictly below `3/2`. The same factor lifted the lower opening
in #4838 only to `93/64`.

The even child's left shear then carries

```text
(1, 0) = -1/16, (3, 0) = 15/256, (3, 2) = -1/16,
```

with infinity norm `287/256`. It lifts the running product from `187/128` to
`25/16`. The value `25/16` is strictly above `3/2`. The remaining eleven
proper prefixes, including that step, equal `25/16`. No proper prefix exceeds
`25/16`. The largest proper prefix is `25/16`. Eleven proper prefixes exceed
`3/2`.

The Schur child is

```text
(1, -1/8, -25/256, 87/4096),
```

with split `(1, -25/256)`, `(-1/8, 37/4096)`, `(1, -29/256)`. The quadratic
Schur coefficient matches #4838. The degree-3 coefficient does not: there it
was `343/4096`. The Schur right shear carries `-1/8` and has factor norm
`9/8`. The running norm is already `25/16` before that shear, and it stays
`25/16`. The later shears carry `-25/256`, `-29/256`, and the pair `-1/8`,
`37/4096`. That last proper-prefix factor has infinity norm `4645/4096` and
still leaves the running norm at `25/16`. Ten factors differ from `I`. The
top left shear is the last of them and carries `1115/16384` at `(7, 0)`, so
nine nontrivial factors sit in the proper prefixes. The completed product of
the 22 factors equals the even/odd reordering of the Toeplitz matrix. Its
infinity norm is `13/8`, because the tail absolute sum is `5/8`.

`1403/1024 < 11/8 < 1435/1024 < 1445/1024 < 23/16 < 93/64 < 187/128 < 3/2 < 25/16 < 13/8 < 9/4`.

## Not covered

- The degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`, and the
  other 127 symbols in the claimed sign family.
- The symbol `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)`.
- A bound for every tail of any fixed `l1`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-degree-five-sign --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-degree-five-sign
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T22:23:32Z and again at
2026-10-22T22:25:47Z. Both fetches were that commit. The selection is κ =
`60403/20000000`. The pinned blobs of `certificates/selected-result.json`,
`GAUSSIAN.md`, and `vendor/SHALLOW-TOEPLITZ.md` are unchanged from #4838.

Overlap snapshot: open PRs fetched 2026-10-22T22:24:57Z (388 records) and
discussions fetched 2026-10-22T22:25:43Z (3870 records). Terms
`triangular-parity-quarter-degree-five-sign`, `1445/1024`, `1115/16384`,
`4645/4096`, `187/128`, and
`-1/4, -1/16, -1/16, -1/16, -1/16, 1/16, 1/16` returned this README, this
TASK, and the #4838 DONE note that poses this question. Predecessor
READMEs are absent from this checkout because the branch starts at fetched
main. No matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)`
   keep every proper prefix at most `25/16`?** Flipping the degree-5
   sixteenth keeps the even child of #4838 and raises the opening from
   `1403/1024` to `1445/1024`, above `11/8`. The even-child right shear no
   longer lifts it. One proper prefix is `187/128`, above `93/64` and below
   `3/2`. The largest proper prefix stays `25/16`. The next sixteenth is
   even, so the even child changes. The linear coefficient stays `-1/4`,
   outside the claimed family of `±1/8`. Do not treat `p^100` as already
   spent.

## Credit

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
