# Ordinary bill of the witness `F1 = Q`, `F2 = C1 Q`

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier is unchanged. No call is added.

## The pair and the owned bank

The published feed in
[research/coded-active-feedback](../coded-active-feedback/PROOF.md) saves the
first FULL output `h`, adds `I · h` into query 2, and adds `C1 Q^2` times
that response into query 4. One extra owned 112-field bank holds `h` and is
later reset and reused for the response. The witness uses that same bank
and the same two insertion points. It replaces the two operators by
`F1 = Q` and `F2 = C1 Q`. Both lie outside the 8,281-policy family. First-edge choices are scalars
times alternating `C1`/`C3` words, and `Q` is not one of those words.
Every nonzero second-edge choice ends in `Q^2`, and `C1 Q` does not. This
note does not re-prove the one-edge obstruction. It prices this pair.

Rightmost operators act first. `Q^4 = I`, `C1^2 = C3^2 = I`, and each `D`
commutes with `Q` and with the other `D`, while `D_s` conjugates only `C_s`
by `Q^{-1}`. The verifier checks the four conjugations below.

## While the bank holds `h`

The pinned replay, and the conjugations just named, give the saved bank

```text
h = [Q^{-1} C1 D1, D1, -Q^{-1} C1 D1, 0]
```

and the pair-0 X bank at query 2

```text
X = [0, -C1 Q D1, D1, 0].
```

`I` leaves `h` unchanged. Left multiplication by `Q` cancels the leading
`Q^{-1}` on the two `C1` columns:

```text
Q h = [C1 D1, Q D1, -C1 D1, 0].
```

The two images differ on `x0`, `y0`, and `x1`. The query-2 arguments are
`C1 X + F1 h`.

```text
C1 X + h     = [Q^{-1} C1 D1, D1 - Q D1, C1 D1 - Q^{-1} C1 D1, 0]
C1 X + Q h   = [C1 D1, 0, 0, 0].
```

The two cancelled columns are the identities `C1(-C1 Q D1) + Q D1 = 0` and
`C1 D1 + Q(-Q^{-1} C1 D1) = 0`. The witness argument is one monomial. The
published argument is not. The paid response is `Q^{-1}` times the
argument, so the witness writes

```text
r2 = [Q^{-1} C1 D1, 0, 0, 0]
```

into the reused bank. The published response, on this same bank after
`F1 = I`, is

```text
[Q^2 C1 D1, -D1 + Q^{-1} D1, Q^{-1} C1 D1 - Q^2 C1 D1, 0].
```

## While the bank holds the response

On the witness response,

```text
C1 Q · r2   = [D1, 0, 0, 0]
C1 Q^2 · r2 = [C1 Q C1 D1, 0, 0, 0].
```

Only the witness operator returns `D1`. On the published response the same
two operators differ on `x0`, `y0`, and `x1`. The predecessor identity
`query4:3 = [0, 0, X1, 0] + Q^{-1} F2 r2`, with
`X1 = Q^{-1} C3 D1 D3`, therefore gives the autonomous row

```text
[D1 Q^{-1}, 0, X1, 0]
```

for this pair and not for `C1 Q^2` on the same `r2`. The query adds that
response into bank 1. Bank 1 still holds `h`, whose `x0` column equals
`r2`, so the sum is

```text
[2 Q^{-1} C1 D1, D1, -Q^{-1} C1 D1, 0].
```

The coefficient `2` is that sum. It is not a second addition and not a
second owned bank.

## Ordinary bill

The ledger uses the predecessor's published units: one F-transpose is
896 scalar ADDs, 224 monomial passes and 16 mode CLEARs; one 112-field
addition is 112 ADDs; one capture is 112 COPYs; one reset of the saved
bank is 112 field resets; one uniform power of `Q` or `Q^2` is 112
monomial passes. `Q` overwrites the saved copy of `h` before that copy is
added. The schedule does not read the unmultiplied copy again, so no third
capture is charged. Zero columns are not discounted. Maps are not fused.

| Added operation | Published `I`, `C1 Q^2` | Witness `Q`, `C1 Q` |
| --- | ---: | ---: |
| Two feedback additions | 224 ADDs | 224 ADDs |
| One F-transpose, the `C1` in `F2` | 896 ADDs, 224 monomials, 16 CLEARs | same |
| Monomial on saved `h` | none (`I`) | `Q`: 112 monomials |
| Monomial on the saved response | `Q^2`: 112 monomials | `Q`: 112 monomials |
| Captures of `h` and `r2` | 224 COPYs | 224 COPYs |
| Initial, intermediate and final reset | 336 resets | 336 resets |
| Extra owned capacity | 112 fields and 8 modes | same |
| Gaussian children | 0 | 0 under this unit |

The witness therefore pays 1120 scalar ADDs, 448 monomial passes, 16 mode
CLEARs, 224 COPYs and 336 resets. The published feed pays the same totals
except 336 monomial passes. The difference is one `Q` on `h`. The response
line changes from `Q^2` to `Q` and keeps the count 112.

This is an upper bound for that circuit under those units. It is not a
minimum, not a tape cost, and not a new κ. The same unit was used for `Q`
and `Q^{-1}` in
[research/owner-indexed-y0-clearance](../owner-indexed-y0-clearance/PROOF.md),
which left the primitive open. If one power of `Q` is a Gaussian child, or
must be expanded before it is a monomial pass, the witness line
"Gaussian children: 0" is false and 448 undercounts. That alternative is
not settled here.

## The scalar suffix

After query 4 the schedule executes only the existing scalar suffix:
add bank 0 into bank 2, subtract bank 3 from bank 1, swap banks 0 with 1
and 2 with 3 while negating the outgoing banks, then add bank 2 into bank 0
and subtract bank 1 from bank 3. For arbitrary banks `A, B, C, D` the
composition is

```text
final = (B, -A, D, -C).
```

The bridge terms cancel for every content. The suffix is a signed
permutation of the four query-4 banks. It clears a final bank to a target
only when the corresponding preimage is already that signed target. It
does not multiply by `Q`, `C1`, or `C3`, and it does not cancel a nonzero
column against a different column.

The witness preimages are bank 1 after the response sum, the pure y0 row
`[0, -C1 Q D1, 0, 0]`, the autonomous row, and the FULL3 X bank. None is
the signed uncoded target. The final banks are therefore

```text
bank 0 = [2 Q^{-1} C1 D1, D1, -Q^{-1} C1 D1, 0]
bank 1 = [0, C1 Q D1, 0, 0]
bank 2 = [D1 Q^{-1}, 0, Q^{-1} C3 D1 D3, 0]
bank 3 = [C3 C1 D1 D3, C3 Q D1 D3, -D1 D3, C3 Q D1 D3].
```

Bank 1 is the same pure y0 monomial as in the published feed. Bank 2 is
the autonomous row, so its y0 and y1 are zero and its x0 and x1 are not.
Bank 0 has three nonzero columns, and its x0 coefficient is 2. Bank 3 has
four nonzero columns, with `y0 = y1 = C3 Q D1 D3`. The uncoded targets are
`D1 Q^{-1}`, `D1 Q`, `D1 D3 Q^{-1}`, and `D1 D3 Q` on the diagonal. No
final bank equals its target.

The FULL3 shape of bank 3 is the same conjugation family. Before the left
`D3`, bank 2 is `-Q C3` times the post-bridge bank 3, plus the carried
`D1` on x1. Then

```text
D3 Q C3 D1           = C3 Q D1 D3
D3 Q C3 Q^{-1} C1 D1 = C3 C1 D1 D3,
```

and `D3` commutes with `D1`. Negating that bank is final bank 3.

Halving bank 0 does not produce target 0. Left multiplication of bank 3 by
`C3` turns y1 into `Q D1 D3` and also turns y0 into that same monomial, so
it is not target 3. Neither operation is part of the suffix.

## No word-free combination hits a target

A rational linear combination of the four final banks, with no extra
monomial, is the largest word-free scalar operation on these banks. It
still uses no new call. The target monomials are disjoint from this
support, except for one inseparable pair:

- Target 0 is the single key `Q^{-1}` on x0 at D-exponent `(1, 0)`. That
  key occurs only as bank 2's x0 column. Bank 2's x1 column is
  `Q^{-1} C3 D1 D3`, and that key occurs nowhere else. The coefficient
  that copies target 0 also copies the x1 monomial.
- Target 1 is `Q` on y0 at D-exponent `(1, 0)`. No final column contains
  that key.
- Target 2 is `Q^{-1}` on x1 at D-exponent `(1, 1)`. No final column
  contains that key.
- Target 3 is `Q` on y1 at D-exponent `(1, 1)`. No final column contains
  that key. Bank 3's y1 key is `C3 Q`, not `Q`.

The domain of this statement is these four banks and these four targets.
Every one of the sixteen columns was inspected for each key. This is not
a census of feedback pairs, and it does not forbid a monomial multiplier
or a read of an earlier bank.

## What is not proved

The witness is one pair. The formal algebra is the predecessor's sufficient
identity model. A quotient that collapses one of these words could make the
same banks look cheaper; no such quotient is proved here. Native tape,
precision, compiler, and outer costs are not repriced. The x1 block of the
published feed and a saved-bank source other than this response are not
taken. The selected conditional κ, `781451/250000000`, is not changed.
