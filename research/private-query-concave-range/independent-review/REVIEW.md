# Independent review of the new scalar extension

Result: PASS within the six stated premises. No proof defect was found.
The historical private64 theorem was a premise. This review did not
replay or certify that theorem.

## Scalar inequality

The derivative ratio is correct. It is strictly increasing on the real
line. The first integer comparison gives a positive critical point.
The second comparison gives `log(8)/log(9)<91/96`, so
`8*log(8)/(7*log(9))<13/12`. The third comparison then gives
`a0<7/10`. The fourth comparison gives
`log(8)/log(9)>17/18`, so the coefficient in the critical-point
formula is less than `4/9`. The fifth comparison bounds `8^a0` by
`13/3`. All inequalities are strict and all factors are positive.
Thus `F(a0)>2/27`. The derivative sign proves that this is a bound for
every `0<=a<=1`.

An independent integer and Fraction calculation checked all five
comparisons, the two logarithmic coefficient reductions, the rational
margin, the chord coefficients, and both endpoints. The submitted
verifier was not imported. Decimal calculations were diagnostics only.
They give `a0` about `0.6659342077` and `F(a0)` about `0.2872388751`.
The exact proof uses the weaker bound `2/27`.

The retained calculation is `independent_calculation.py`. It records all
five integer comparisons in `independent-calculation.json`. From the
repository root, run:

```text
python3 work/fresh-research-20261012/private-bound/independent-review/independent_calculation.py
```

## Weighted extension

The dependent-row step is valid for the stated factorization. Select a
basis from the query rows. Express each removed row in this basis and
add its decoder contribution to the retained decoder columns. Keep
the retained source frames. This preserves `G`. Every removed row has
a positive charge, including at both endpoints.

If there are eight retained rows, their span equals the row space of
`G`. The support and capacity premises force every frame rank to be at
least eight. If total rank is 64, the maximum-rank premise gives the
weighted bound. In the remaining case, integer ranks give total rank
at least 65 and the row count is at least nine. These cases cover all
retained profiles.

For `0<=a<=1`, the power function is concave. Its rank-one to rank-nine
chord has slope `(9^a-1)/8` and intercept `(9-9^a)/8`. Both are
nonnegative. Thus separate lower bounds on total rank and row count
can be used, including at `a=0` and `a=1`. The resulting expression
is exactly `7*9^a+2`.

For `0<b<1`, equality requires eight queries, each of rank eight.
At `b=0`, the proof does not exclude other total-64 profiles. At
`b=1`, the bill is the query count. An eight-query factorization has
bill eight, whether its allowed frame ranks are eight or nine. These
endpoint statements are consistent with the proof.

For `b>1`, the sharpness statement is valid if the stated model permits
an enlarged source frame. A rank-nine frame contains the rank-eight
frame. The cost decreases because `1-b<0`. This gives a cost-law
example only. It gives no physical circuit or recurrence claim.

## Verification limit

This review certifies the new scalar argument and its conditional
weighted consequence. It does not certify the fixed Gram code,
capacity bound, total-rank bound, profile classification, coordinate
gathers, or source-label invariance. No integer kappa improvement
follows from this lemma alone. The proof states this limit.

No changes are required for the new argument. A submission must include
or cite reproducible evidence for all six premises.

Prepared with OpenAI Codex assistance. New work is under Apache-2.0.
