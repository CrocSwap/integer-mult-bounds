# One degree-6 sign on the negative quarter keeps the 187/128 path

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4869 recorded `(1, -1/4, -1/16, -1/16, -1/16, -1/16, 1/16, 1/16)` and left the
sign `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)` open. The linear
coefficient `-1/4` is outside the 128-symbol claim
[discussioncomment-19132735](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735),
whose linear coefficient is `±1/8`. This package records this one sign. It is
not the degree-6 sign of that claimed family.

## Record

The symbol is `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)`. The tail
`l1` is `1/4 + 6/16 = 5/8`. The schedule is the same nested order: right
shear, even child, Schur child, left shear, repeated inside every child.
There are 22 factors in the top even/odd basis and 21 proper prefixes.

The flipped coefficient has even degree, so the even child changes. It is

```text
(1, -1/16, -1/16, -1/16),
```

with split `(1, -1/16)`, `(-1/16, -17/256)`, `(1, -17/256)`.

The quotient is

```text
k = (-1/4, -5/64, -85/1024, 603/16384).
```

The first three entries match #4869. The last entry there was `1115/16384`.
The right shear uses `z k` and drops that last entry, so the shear itself
matches #4869. Its bottom absolute row sum is

```text
1 + 1/4 + 5/64 + 85/1024 = 1445/1024.
```

The entries on that shear are `-1/4` at `(1, 4)`, `(2, 5)`, and `(3, 6)`,
`-5/64` at `(2, 4)` and `(3, 5)`, and `-85/1024` at `(3, 4)`. This opening is
strictly above `11/8` and strictly below `23/16`. The even child's right
shear has entry `-1/16` and does not lift the running norm, so the first
five proper prefixes stay `1445/1024`.

The even grandchild stays `(1, -1/16)`. Its left shear still has entry
`-1/16` and lifts the next four proper prefixes to `23/16`. The even child's
Schur complement is still `(1, -17/256)`. Its left shear has entry
`-17/256`, with factor norm `273/256`, and lifts `23/16` to `187/128`. That
value is one step above `93/64` and strictly below `3/2`.

The even child's left shear then carries

```text
(1, 0) = -1/16, (3, 0) = -17/256, (3, 2) = -1/16,
```

with infinity norm `289/256`. In #4869 the `(3, 0)` entry was `15/256` and
the factor norm was `287/256`. This shear still lifts the running product
from `187/128` to `25/16`. The value `25/16` is strictly above `3/2`. The
remaining eleven proper prefixes, including that step, equal `25/16`. No
proper prefix exceeds `25/16`. The largest proper prefix is `25/16`. Eleven
proper prefixes exceed `3/2`. The proper-prefix norms are `1445/1024` five
times, `23/16` four times, `187/128` once, and `25/16` eleven times. That is
the same list as #4869. The factors are not the same list.

The Schur child is

```text
(1, -1/8, -25/256, -425/4096),
```

with split `(1, -25/256)`, `(-1/8, -475/4096)`, `(1, -29/256)`. The quadratic
Schur coefficient matches #4869. The degree-3 coefficient does not: there it
was `87/4096`. The Schur right shear carries `-1/8` and has factor norm
`9/8`. The running norm is already `25/16` before that shear, and it stays
`25/16`. The later shears carry `-25/256`, `-29/256`, and the pair `-1/8`,
`-475/4096`. That last proper-prefix factor has infinity norm `5083/4096`
and still leaves the running norm at `25/16`. Ten factors differ from `I`.
The top left shear is the last of them and carries `603/16384` at `(7, 0)`,
so nine nontrivial factors sit in the proper prefixes. The completed product
of the 22 factors equals the even/odd reordering of the Toeplitz matrix. Its
infinity norm is `13/8`, because the tail absolute sum is `5/8`.

`1403/1024 < 11/8 < 1445/1024 < 23/16 < 93/64 < 187/128 < 3/2 < 25/16 < 13/8 < 9/4`.

## Not covered

- The degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`, and the
  other 127 symbols in the claimed sign family.
- The symbol `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16)`.
- A bound for every tail of any fixed `l1`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-degree-six-sign --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-quarter-degree-six-sign
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream was fetched at 2026-10-22T22:33:25Z and again at
2026-10-22T22:35:40Z. Both fetches were that commit. The selection is κ =
`60403/20000000`. The pinned blobs of `certificates/selected-result.json`,
`GAUSSIAN.md`, and `vendor/SHALLOW-TOEPLITZ.md` are unchanged from #4869.

Overlap snapshot: open PRs fetched 2026-10-22T22:34:48Z (394 records) and
discussions fetched 2026-10-22T22:35:37Z (3884 records). Terms
`triangular-parity-quarter-degree-six-sign`, `603/16384`, `5083/4096`,
`475/4096`, and
`-1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16` returned this README, this
TASK, and the #4869 DONE note that poses this question. The opening
`1445/1024` was left out of that search because #4869 already records it.
Predecessor READMEs are absent from this checkout because the branch starts
at fetched main. No matches is not a novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, -1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16)`
   keep every proper prefix at most `25/16`?** Flipping the degree-6
   sixteenth changes the even child and still leaves the proper-prefix norms
   at `1445/1024` five times, `23/16` four times, `187/128` once, and
   `25/16` eleven times. The right shear matches #4869 because it drops the
   changed quotient entry. The even-child left shear changes from `15/256`
   to `-17/256` and still crosses `3/2`. The last sixteenth is odd, so the
   even child of this symbol stays. The linear coefficient stays `-1/4`,
   outside the claimed family of `±1/8`. Do not treat `p^100` as already
   spent.

## Credit

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
