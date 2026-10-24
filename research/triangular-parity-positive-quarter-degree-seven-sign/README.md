# The last positive-quarter sixteenth changes only the final shear

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4890 recorded `(1, 1/4, -1/16, -1/16, -1/16, -1/16, -1/16, 1/16)` and left the
last sixteenth open:

```text
(1, 1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16).
```

The linear coefficient `1/4` is outside the 128-symbol claim
[discussioncomment-19132735](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132735),
whose linear coefficient is `±1/8`. This package records this one sign. It
completes the successive sixteenth walk on the leading coefficient `1/4`.

## Record

The tail `l1` is `1/4 + 6/16 = 5/8`. The schedule is the same nested order:
right shear, even child, Schur child, left shear, repeated inside every
child. There are 22 factors in the top even/odd basis and 21 proper prefixes.

The flipped coefficient has odd degree, so the even child stays. It is

```text
(1, -1/16, -1/16, -1/16),
```

the same even child as #4890 and #4872. The Schur child also stays. It is

```text
(1, -1/8, -9/256, -153/4096).
```

The quotient's first three coefficients match #4890. The last coefficient
changes from `1181/16384` to `-867/16384`:

```text
k = (1/4, -3/64, -51/1024, -867/16384).
```

The right shear uses `z k` and drops that last entry, so every proper-prefix
factor matches the degree-6 sign. The only changed matrix entry in the whole
schedule is `(7, 0)` of the final left shear. That entry is `-867/16384`, and
the factor norm falls from `23245/16384` to `22931/16384`. The value
`-867/16384` is absent from every proper-prefix factor.

The proper-prefix norms therefore match #4890. The opening is `1379/1024`.
The next four proper prefixes are `11/8`. The next five are `23/16`. Eleven
proper prefixes equal `25/16`. The largest proper prefix is `25/16`, strictly
above `3/2`. Eleven proper prefixes exceed `3/2`. None exceed `25/16`. The
completed product equals the even/odd reordering of the Toeplitz matrix and
has infinity norm `13/8`.

`1373/1024 < 1379/1024 < 1403/1024 < 1405/1024 < 11/8 < 23/16 < 3/2 < 25/16 < 13/8 < 9/4`.

## Not covered

- The degree-1 sign `(1, -1/8, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)`, and the
  other 127 symbols in the claimed sign family.
- Any other sign pattern of the six sixteenths.
- A `1/32` tail, or any new tail slot.
- A bound for every tail of any fixed `l1`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-positive-quarter-degree-seven-sign --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-positive-quarter-degree-seven-sign
```

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
Upstream fetches at 2026-10-22T23:13:34Z and 2026-10-22T23:15:48Z were that
commit. The pinned input blobs were unchanged. The selection is κ =
`60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T23:14:54Z (423 records) and
discussions fetched 2026-10-22T23:15:44Z (3939 records). Terms
`triangular-parity-positive-quarter-degree-seven-sign`, `867/16384`,
`22931/16384`, and
`1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16` reported 6 matches: this
README, this TASK, the #4890 DONE that leaves this symbol open, and the
negative-quarter degree-7 sign in #4877 (its phrase
`-1/4, -1/16, -1/16, -1/16, -1/16, -1/16, -1/16` contains the searched
token as a substring). No other package records this positive leading
coefficient. No matches is not a novelty certificate. Predecessor READMEs
for #4877 and #4890 are not in this checkout; this branch starts at fetched
main.

## Open next questions

No further successive sixteenth remains on either leading quarter. This
symbol is the last sign on the walk that starts from
`(1, 1/4, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16)` and flips one sixteenth at a
time through degree 7. The same walk on the leading coefficient `-1/4` ended
at #4877. Another sign pattern, a `1/32` tail, and the claimed family of
linear coefficient `±1/8` are different questions. This package does not open
them.

## Credit

- The degree-6 sign of the positive quarter is #4890's.
- The degree-5 sign of the positive quarter is #4889's.
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
