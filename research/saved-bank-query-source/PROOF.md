# One saved bank autonomizes the query-4 row

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier stays `781451/250000000`.

## What is proved

Three statements, in the group algebra of
[research/coded-active-feedback](../coded-active-feedback/PROOF.md).

1. **Identity.** Save the pair-0 X bank at the `bridge_query2` snapshot.
   Add the one operator `I - C1 Q C1` times that bank into the existing
   final-query argument, and keep the published second operator `C1 Q^2`
   on `response2`. The four-input row after query 4 is the autonomous row
   `[A, 0, X1, 0]`.
2. **Charge.** That operator is the unique algebra element which does
   this for the named bank. It has exactly two monomials. Each monomial
   cancels one term of the y0 coupling and one term of the x1 defect.
   Dropping either monomial leaves both defects nonzero.
3. **Census.** Among the 29 recorded banks that exist before the
   final-query argument and are not `response2`, this is the only bank
   for which any algebra element works. The nine observations recorded
   at or after `response4` are not sources for that argument. The same
   two lemmas reject them as well.

The census is exhaustive for that finite list of recorded banks. It is
not a search over operators: each bank is settled by a zero column or by
the inverse of a one-term column. It is not a proof that every further
physical quotient has the same negative list. The positive identity
descends to every quotient of this algebra.

## The row and the correction

The published feed uses `F1 = I` on the saved first-FULL Y bank and
`F2 = C1 Q^2` on `response2`. After query 4, and before the scalar
suffix, the pair-1 Y bank is

```text
[A, B, X1 + E, 0]
```

with `A = D1 Q^{-1}`, `X1 = Q^{-1} C3 D1 D3`, and

```text
B = Q^{-1} C1 Q D1 - Q^{-1} C1 Q^2 D1
E = -Q^{-1} D1 + Q^{-1} C1 Q C1 D1.
```

`B` and `E` are nonzero. The autonomous row is `[A, 0, X1, 0]`. The
query multiplies its argument by `Q^{-1}` and adds the response into
this Y bank, so an extra summand `P S` in the argument adds
`Q^{-1} P S` to the row. The required correction is therefore

```text
P S = Q [0, -B, -E, 0] = [0, ρ1, ρ2, 0]
ρ1 = -C1 Q D1 + C1 Q^2 D1
ρ2 = D1 - C1 Q C1 D1.
```

`Q` commutes with `D1`. Both `ρ1` and `ρ2` have two monomials. Columns
0 and 3 of the correction are zero, so the published `A` and the zero
y1 coefficient stay in place exactly when `P` contributes nothing there.

## The named bank

Write `S` for the pair-0 X bank. The schedule writes it as follows.

The right boundary starts that bank at `[I, 0, -I, 0]`. Query 0 adds
`C1 Q^{-1}` times this bank into the pair-0 Y bank, whose y0 column is
still `I`. FULL1 then adds `-Q C1` times the Y bank and left-multiplies
by `D1`. The y0 column of that sum is `-Q C1`. Conjugation gives

```text
D1 (Q C1) = C1 Q D1,
```

because `D1` commutes with `Q` and `D1 C1 = Q^{-1} C1 Q D1`, so the
inserted `Q^{-1}` cancels the leading `Q`. The other three columns
cancel, and the pair-0 X bank at FULL1 and at IDLE is

```text
[0, -C1 Q D1, 0, 0].
```

IDLE left-multiplies the pair-1 X bank, which is still the input `x1`,
by `D1`. The following `+1` bridge adds that bank into pair-0 X. Query 2
writes the pair-0 Y bank only. The `bridge_query2` snapshot is therefore

```text
S = [0, -C1 Q D1, D1, 0].
```

`bridge_minus` subtracts the same pair-1 X bank and deletes the `D1`
on `x1`. The copy has to be taken at or before the `bridge_query2`
snapshot. The live pair-0 X bank at the final query has a zero x1
column.

## The operator

`S1 = -C1 Q D1` is a one-term element, so it has a two-sided inverse.
Right multiplication by that unit preserves the number of monomials.
The equation `P S1 = ρ1` has the unique solution

```text
P = ρ1 S1^{-1} = I - C1 Q C1,
```

and that element has exactly two monomials. Direct expansion, using
`C1^2 = I` and `D`-exponent 0 on `P`, gives

```text
P S1 = -C1 Q D1 + C1 Q^2 D1 = ρ1
P S2 = D1 - C1 Q C1 D1 = ρ2
P S0 = P S3 = 0.
```

Hence `P S = ρ`, and the row becomes `[A, 0, X1, 0]`. The chronological
replay adds `P S` beside the published summand `C1 Q^2 response2`. It
does not replace that summand, and it does not rewrite any bank
recorded before the argument.

## Charge of the two monomials

Rightmost factors act first, as in the predecessor. On the row, after
the query's `Q^{-1}`:

| Monomial | y0 contribution | x1 contribution |
| --- | --- | --- |
| `I` | `-Q^{-1} C1 Q D1` | `Q^{-1} D1` |
| `-C1 Q C1` | `Q^{-1} C1 Q^2 D1` | `-Q^{-1} C1 Q C1 D1` |

The first column of the table is `-B`. The second is `-E`. Both
monomials contribute `0` on `x0` and on `y1`, because those columns of
`S` are zero. Either monomial alone leaves one term of `B` and one term
of `E`. Both are charged.

One circuit under the predecessor's published units, keeping the saved
copy and using a second scratch bank:

| Step | Unit | Count |
| --- | --- | ---: |
| Copy `bridge_query2:0` into `U` before `bridge_minus` | 112 COPYs | 1 |
| `V ← C1 U` | one F-transpose | 1 |
| `V ← Q V` | 112 monomial passes | 1 |
| `V ← C1 V` | one F-transpose | 1 |
| `V ← U - V` | 112 scalar ADDs | 1 |
| Add `V` into the final-query argument | 112 scalar ADDs | 1 |

A F-transpose is 896 scalar ADDs, 224 monomial passes and 16 mode
CLEARs. One monomial pass on a 112-owner bank is the predecessor's
`Q^2` unit. The totals are 2016 scalar ADDs, 560 monomial passes,
32 mode CLEARs, 112 COPYs, 224 extra fields, and the inherited 8 mode
fields reused. No Gaussian child is added. This is an upper ledger for
this circuit. It is not a minimum, not a tape proof, and not a κ.

## Census of the other recorded banks

Let `ρ = [0, ρ1, ρ2, 0]` with both middle columns nonzero. For a
recorded bank `T`:

- If `T1 = 0` or `T2 = 0`, then `P T` cannot equal `ρ`.
- If `T0` or `T3` is a one-term element, it is a unit, so `P T` has a
  zero in that column only for `P = 0`. Then `P T ≠ ρ`.
- If `T1` is a one-term element, `P = ρ1 T1^{-1}` is the only candidate.
  It works only when the other three columns match `ρ`.

`search.replay` records 30 observations before it builds the `response4`
argument. Excluding `response2` leaves 29 legal sources. The verifier
checks the ordered label list against the schedule and partitions those
29 by the first applicable lemma:

| Class | Count | Labels |
| --- | ---: | --- |
| Zero on y0 or on x1 | 19 | `right:0` through `right:3`, `response0`, `query0:0`, `query0:2`, `query0:3`, `FULL1:0`, `FULL1:2`, `FULL1:3`, `IDLE:0`, `IDLE:2`, `IDLE:3`, `bridge_query2:2`, `bridge_query2:3`, `bridge_minus:0`, `bridge_minus:2`, `FULL3:0` |
| Unit on x0 or on y1 | 6 | `query0:1`, `FULL1:1`, `IDLE:1`, `bridge_minus:3`, `FULL3:2`, `FULL3:3` |
| Unique candidate spoils x0 | 3 | `bridge_query2:1`, `bridge_minus:1`, `FULL3:1` |
| Works | 1 | `bridge_query2:0` |

The three labels in the third class are the same vector: the pair-0 Y
bank is not rewritten by `bridge_minus` or by FULL3. Its y0 column is
the unit `Q^{-1} D1`, so the only candidate is
`C1 Q^{-1} - C1 Q^2`. That candidate clears y0 and the x1 defect and
writes `-D1 + C1 Q^2 C1 D1` on x0, which is nonzero. The restored
coefficient `A` moves.

The nine later labels are `response4`, `query4:0` through `query4:3`,
and `left:0` through `left:3`. They are the final response or the
scalar suffix, so they are not inputs of this argument. The same
partition rejects all nine.

`response2` is outside the claim because an extra operator on it would
change the coefficient of the published second edge. Its x0 column is
nevertheless a unit, so the only algebra element that preserves `A` is
zero, and zero does not clear `B`.

## What the suffix does not do

The scalar suffix is the published bridge, the signed swap, and the two
final additions. With this insertion, none of the four final banks
equals the corresponding uncoded target. The autonomous statement is the
pre-suffix row `query4:3` only. It is not a caller.

## What is not proved

No statement is made about a sum of two saved banks, a port-dependent
map, a new call, or an operator inserted anywhere except the existing
final-query argument. The negative census uses this formal algebra,
whose relations are `Q^4 = C1^2 = C3^2 = I`, commuting `D` exponents,
and the inherited conjugation rule. A further physical relation can
kill a nonzero residual and is outside the census. The positive
identity is an equality in this algebra, so it remains an equality in
every quotient. Native tape, precision, compiler, and outer costs are
not priced. The selected conditional κ is not changed.
