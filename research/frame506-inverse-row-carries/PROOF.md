# Intermediate carries of one frame-506 inverse elimination

This is a proof for one fixed elimination word, together with three exhaustive
finite censuses. It uses the carry formula of PR #4957, section 3, applied to
each elementary factor. It does not replace the closed-form envelope of PR
#7104, and it does not change the selected frontier.

## Word

The frozen frame 506 of helper 462 has rank 4. With image rows `B` and kernel
rows `A`,

```text
S = [ B^T | A^T ].
```

The same integer matrix is recorded in
`research/bit-completed-backend-api/science/RESULT.json`. Exact elimination,
the algorithm in that package's `science/check.py`, produces 5 swaps, 5 scales
and 14 shears. The published factor list is reproduced exactly, and the right
product is `S`. Reversing the word and inverting each factor produces a word
for `S^{-1}`: the same five swaps, with each scale `c` replaced by `1/c` and
each shear coefficient negated. PR #4957 does not fix this word as the physical
return. It is the inverse of the published elimination, and the count below is
the intermediate quotient of that word.

Every scale or shear coefficient in the inverse word lies in `{1, -1, 1/2, -1/2}`.
`det S = -16`, so every denominator of `S^{-1}` divides 4. The residue used
below is unique for every odd integer `q`, because 2 is invertible modulo `q`.

## One carry digit per scale and per shear

A low row is an 8-tuple with coordinates in `{0, ..., q-1}`. An elementary
right factor acts on that row as follows.

- A swap exchanges two coordinates. Both digits are already reduced, so the
  PR #4957 quotient of the swap is 0.
- A scale multiplies one coordinate by a fixed rational and leaves the other
  seven unchanged. The quotient of each unchanged coordinate is 0, so the
  factor emits one carry digit.
- A shear adds a fixed rational multiple of one coordinate into one other
  coordinate. Again only one coordinate changes, so the factor emits one
  carry digit.

The carry digit is the quotient `(z - h) / q` in `Z[1/2]`, where `z` is the
unreduced value of the updated coordinate and `h` is the unique element of
`{0, ..., q-1}` for which the difference is `q` times an element of `Z[1/2]`.
The digit is nonzero when that quotient is nonzero as a rational.

The inverse word therefore has 19 arithmetic sites on one row. At most 19 of
them are nonzero. In particular the count is strictly less than 48, for every
low row and every odd integer `q`. This is the site bound. It is not a claim
about a longer factorization, and it is not the 48-correction closed form of
`S^{-1}` proved in #7104.

## Named row

PR #7104 attains its return envelope on the low type

```text
u(q) = (q-2, q-2, q-5, q-5, 0, q-1, 0, 0),
```

which is a legal row for every integer `q ≥ 5`. The closed-form correction of
`u(q)` under `S^{-1}` has six nonzero entries. The calculation here follows
the inverse word instead of that closed form.

For every odd integer `q ≥ 7`, each updated coordinate stays inside an affine
formula `A + s q` with `s ∈ {0, 1/2, 1}` and `A ∈ Z[1/2]`. The slope is the
unique value in `{0, 1/4, 1/2, 3/4, 1}` for which `A + s q` is an integer in
`{0, ..., q-1}` for every odd integer `q ≥ 7`. Integrality is checked on a
complete set of odd residues modulo the power-of-two denominator. Along each
residue class the value and the slack `q - value` are nondecreasing, because
the class step adds a nonnegative integer to both. The resulting digits are:

| site | operation | unreduced value | residue | carry |
| ---: | --- | --- | --- | --- |
| 0 | `x7 += x3` | `q-5` | `q-5` | 0 |
| 1 | `x7 += -x2` | `0` | `0` | 0 |
| 2 | `x7 += -(1/2) x1` | `1 - q/2` | `1` | `-1/2` |
| 3 | `x7 += -(1/2) x0` | `2 - q/2` | `2` | `-1/2` |
| 4 | `x7 *= 1/2` | `1` | `1` | 0 |
| 5 | `x5 += -x3` | `4` | `4` | 0 |
| 6 | `x5 += (1/2) x1` | `3 + q/2` | `3` | `1/2` |
| 7 | `x5 += (1/2) x0` | `2 + q/2` | `2` | `1/2` |
| 8 | `x5 *= -1/2` | `-1` | `q-1` | `-1` |
| 9 | `x3 += -x7` | `q-6` | `q-6` | 0 |
| 10 | `x3 += -x2` | `-1` | `q-1` | `-1` |
| 11 | `x3 += -(1/2) x1` | `q/2` | `0` | `1/2` |
| 12 | `x3 += -(1/2) x0` | `1 - q/2` | `1` | `-1/2` |
| 13 | `x3 *= -1` | `-1` | `q-1` | `-1` |
| 14 | `x2 += x7` | `q-4` | `q-4` | 0 |
| 15 | `x2 += -x6` | `-3` | `q-3` | `-1` |
| 16 | `x2 += -x4` | `-2` | `q-2` | `-1` |
| 17 | `x1 *= 1/2` | `(q-2)/2` | `q-1` | `-1/2` |
| 18 | `x0 *= 1/2` | `(q-2)/2` | `q-1` | `-1/2` |

Swaps sit between these sites and emit no digit: `x5` with `x6`, then `x4`
with `x5`, after site 8; `x3` with `x4` after site 13; `x1` with `x6` after
site 17; `x0` with `x5` after site 18. Thirteen of the nineteen digits are
nonzero. The final low row is

```text
(0, q-1, q-2, 0, q-1, q-1, q-1, 1).
```

Starting from high part 0, the same quotients update the high coordinates.
The final high row is the constant

```text
(0, -3/2, -1/2, 0, -1/2, -1/2, -1/2, -1/2),
```

which is the closed-form return correction of `u(q)` from #7104. The
intermediate word therefore emits 13 nonzero quotients on this row, and those
quotients compose to the 6-nonzero closed form. Dropping the quotients while
retaining the linear action misses that high row.

The odd integer `q = 5` is the one odd integer `≥ 5` at which `q - 6` is
negative, so site 9 is outside the tail formula. Direct evaluation of this
single row gives the same digits, except site 9 is `-1` and site 10 is `0`.
The nonzero count remains 13, and the final low and high rows are the same
`q = 5` specializations. That evaluation visits each of the 19 sites once.

The zero row emits the zero quotient at every site, so 13 is the count on
`u(q)`, and it is a maximum only in the sense of the separate censuses below.

## Censuses

For an odd prime `q`, the domain `{0, ..., q-1}^8` is finite. The base-`q`
code of an integer in `{0, ..., q^8 - 1}` visits each row once. On every
coefficient that occurs, the integer nonzero test agrees with the rational
quotient for every digit the operation reads; that agreement is checked for
`q ∈ {3, 5, 7}` before the scan.

| q | domain | maximum nonzero sites | rows at the maximum |
| ---: | ---: | ---: | ---: |
| 3 | 6561 | 18 | 9 |
| 5 | 390625 | 18 | 575 |
| 7 | 5764801 | 19 | 245 |

The maxima are attained by `(1,1,1,2,0,0,0,1)`, `(1,1,1,4,0,0,0,1)` and
`(5,5,6,3,0,0,0,4)` respectively. Each of those three counts was recomputed
with the rational quotient, independently of the scan. The full histograms
are the constants in `verify.py`.

These are exhaustive censuses of those three domains. They do not by
themselves determine the maximum at any other prime. The site bound of 19
already covers every odd integer `q`. The prime 7 shows that 19 is attained,
so no smaller uniform site bound holds for every odd prime. Every counted row
is still strictly below 48.

## What this does not change

The 5/5/14 word, the owners, ROW restoration, P1–P3, the native compiler and
the exponent gaps stay as PR #4957 left them. The closed-form envelopes 48
per route and 96 for the pair, and the `q = 3` pair maximum 88, stay as
#7104 proved them. Repeating `u(q)` on all eight high rows emits
`8 * 13 = 104` nonzero intermediate quotients. That route total is a
different number from the closed-form 48, and this note does not put either
number into a charged bill.

The selected frontier stays `363005817/100000000000`.

## Controls

The range test rejects residue `q - 6` at `q = 5` and accepts it for every
odd integer `q ≥ 7`. The zero row pays nothing. Omitting the quotients in the
high update misses the closed-form correction on `u(q)`. A scale or shear
coefficient outside `{±1, ±1/2}` is rejected before a census. The published
factor list, the helper-462 endpoints and the selected-frontier string are
read from the pinned inputs.
