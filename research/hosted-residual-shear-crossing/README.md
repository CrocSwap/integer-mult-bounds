# The exact correction for moving a hosted residual across a shear

The existing idle-axis-hosting proof moves a helper's residual to a later idle
child through a window with no intervening touch. For a proposed wider window
containing the already-paid two-family shear `T_A:(x,y)->(x,y+Ax)`, merely moving
the residual through the touch can change the data endpoint.

For an invertible source residual `R:x->Rx`, the move is free as an operator
exactly when `A(R-I)=0`. Otherwise the unique correction before the moved
residual is the shear `y+=A(R-I)x`. If placed after the residual it must instead
read the current chart via `y+=A(R-I)R^-1 x`.

For an invertible target residual `R:y->Ry`, moving it after the bridge requires
the post-residual correction `y+=(I-R)Ax`; free crossing is exactly `(R-I)A=0`.
The left and right annihilator conditions are different. These statements hold
for every input, including arbitrary correlated dirty x and y.

## Proof and favorable adapter budget

For the source case the original chronological sequence gives
`(Rx,y+ARx)`. Bridge then residual gives `(Rx,y+Ax)`. Their difference is
`A(R-I)x`, proving both the correction and necessity. At a post-residual cut,
the available source is Rx, so the only source-linear adapter is
`A(R-I)R^-1`. For the target case, the two sequences give `Ry+Ax` and
`Ry+RAx`, whose difference is `(I-R)Ax`. These identities hold over any field;
the finite checker specializes to F2.

Let `E=R-I`. Rank-nullity restricted to im(E) gives

`rank(AE)=rank(E)-dim(im(E) intersect ker(A))`.

In the explicitly declared adapter alphabet of rank-one scalar shears
`y+=u(v^T x)`, any exact adapter D requires at least rank(D) calls by rank
subadditivity, and a rank factorization supplies that many in this abstract
alphabet. If A is square and invertible, both source and target defect ranks
are exactly rank(R-I). A nonidentity residual therefore cannot cross such a
bridge for free. This is an operator-rank cost floor, **not** an identification
of matrix rank with a recursive address-frame rank or a production call price.
Coefficient preparation, source access, charts and routing still require payment.

If a proposed boundary rewrite would remove complete cost c, its favorable
screen must include the correction cost and all changed interface charges.
A zero defect removes this algebraic correction obligation, but does not alone
prove a legal hosting schedule or remove other charges.

## Exact controls and evidence

A singular bridge gives real free-crossing examples. Over F2 take R to swap two
coordinates and `A=[[1,1],[0,0]]`. Then `A(R-I)=0` but `(R-I)A!=0`: the source
residual crosses freely while the target residual does not. Replacing A by the
identity makes either missing correction fail on a nonzero dirty input. An
order-three residual shows that a post-residual adapter must use the current
source chart; reusing the old-chart D fails.

The checker exhausts all96 pairs of2x2 bridge matrices and invertible residuals,
and all86,016 corresponding3x3 pairs. It checks the exact defect rank against
explicit image/kernel intersections and verifies every2Ddirty input or every
3Dinput basis:517,632 input checks. A separate literal source-to-target XOR
engine covers all1,536 two-dimensional dirty states. No random samples,
floating arithmetic or optimization-disabled assertions are used.

```sh
python3 -I -O -B research/hosted-residual-shear-crossing/verify.py
python3.12 scripts/research_package.py --package research/hosted-residual-shear-crossing
```

## Scope and relationship to the selected construction

This audits one explicit replacement premise for the source-bound no-touch
hosting lemma. The selected hosting proof and owner-boundary audit retain their
stricter rules and are not contradicted. No actual selected bridge is asserted
to be T_A, and no helper has been rescheduled. The interface would still need
all pending-axis, endpoint, owner-family, chart, precision and physical-call
checks before adoption. There is no new supplier, selected cold replay or kappa.

## Open next questions

Does an actual selected bridge have a residual subspace in the relevant
annihilator? Extract one bridge matrix and helper chart and check the appropriate
side, then verify pending-axis endpoints and price chart changes. The blocker is
an admitted source-bound bridge model, not the elementary block identity.
TASK.json records this bounded next step.

## Credit

The idle-axis-hosting and exact-owner-reuse proofs supply the residual/window
contract; the owner-boundary audit supplies the distinction between a timing
check and a complete controller. This package adds the explicit shear-crossing
obstruction, orientation distinction and exact scalar adapter budget. Prepared
for woklerx with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review is claimed.
