# Exact correction for the PR6529 word

## Source and claim

Freeze PR6529 at `44b0d0e8961201ac1656490b4384a7752e1cd9c5`.
Keep its first 17,924 events and every boundary field. Replace only its final
569 scalar gates by the 74 gates in `RESULT.json`.

The new block has exactly the same rational operator on all 799 fields.
It uses existing public fields 372 and 1 as temporary accumulators. It creates
no owned field or native MOVE. The complete local real scalar allowance falls
from 137,218 to 132,256. This saves 4,962 units per native call, or 89,316 units
across the unchanged eighteen calls. Paid and productive rank profiles stay
fixed. This is an ordinary-cost result, not a new kappa.

## The rank-two identity

Apply the old correction to independent input coordinates. Call its matrix C.
The exact source calculation gives

`C = I + u a + v b`,

where a and b are row forms, and u and v are columns. The complete forms and
all 74 gates are in `RESULT.json`. Each form has twelve nonzero entries. Their
supports are disjoint. There are 28 nonzero rows in `C-I`. The four pairings are

`a u = a v = b u = b v = 0`.

Thus `(C-I)^2=0`. In particular, a and b are invariant under C. This is an
exact equality of rational matrices, not a numerical rank estimate. The
verifier checks every entry of this factorization. Classical low-rank matrix
factorization and elementary row operations are not new methods.

There are seventeen nonzero entries in each of u and v. Six rows use both
forms. Those six rows require only a+b or a-b; the other rows require a or b.
The twelve coefficients of a include `a[372]=1`, and `u[372]=-1/2`.
The form b has `b[1]=1`, while `u[1]=v[1]=0`. Neither chosen pivot lies in the
other form's support.

## Literal program and restoration

Use eleven ADDs to change field 372 into a(x). Use eleven ADDs to change
field 1 into b(x). No SCALE is required. For each nonpivot output that needs
only a or only b, add its required multiple from the corresponding pivot.

Three pivot ADDs visit a-b and a+b and return to a:

1. field372 -= field1;
2. field372 += 2*field1;
3. field372 -= field1.

Between these steps, deliver each required mixed form once to its target.
All 27 changed nonpivot output rows receive exactly one ADD. Then subtract
the eleven nonpivot terms of b from field 1, in reverse source order. Do the
same for a and field 372. The total is `22+27+3+22=74` ADDs.

To prove the last step, write `a(x)=x_p+S(x)` for p=372. After delivery to
all nonpivot rows, the sum in these rows is

`S(x') = S(x) + (a u-u_p)*a(x) + a v*b(x) = S(x)-u_p*a(x)`.

The pivot still holds a(x). Subtracting S(x') leaves
`x_p+u_p*a(x)`, exactly its required output. The b pivot returns to x_1 by
the same equation with `u_1=v_1=0`. Disjoint form supports make the two
restorations independent. Thus these are restored public accumulators, not
unpaid blank scratch.

Every operand has final frame127 in the source word. All new coefficients
are permitted dyadic rationals. The complete retained checker confirms
chronology, coefficient bounds, productive inputs and owned lifetimes.
At any tensor width, scalar matrices in one common frame act on the same
coordinate fibers. Equality of the full scalar block therefore preserves
that common-frame operation under the source native model. This does not
prove the source model's separate physical or rounding assumptions.

## Cost and search scope

Use the exact source ADD/SCALE allowance, including coefficient bit lengths
and signs. The old correction costs 5,658 real scalar units. The new block
costs 696. All other local charges are identical. The new word has 17,998
events, compared with 18,493 before. Its local allowance is
`137218-5658+696=132256`.

The verifier tests every unit-coefficient pivot in each of the two supports,
both orders of the mixed directions, and both signed dyadic scales with
exponents from -4 to 4. These 78,408 literal programs have minimum allowance
696 and, among that allowance, minimum length 74. All 44 minimizers have the
same checked matrix. A prefix-norm tie break chooses the recorded program.
This is a complete finite optimization of that parameter set. It is not a
minimum over arbitrary linear circuits or over unbounded scales.

Any one-target scalar program needs at least 28 target writes, since 28
output rows differ from identity. The gap from 28 to 74 remains open for
unrestricted programs. More general shared intermediate forms or interleaved
synthesis could change it. No global optimality is asserted.

The correction-only maximum row l1 norm rises from 21 to 28. This matters
if a consumer prices that block in isolation. Direct exact replay of both
complete words gives the same global maximum 838 at event15828 and the same
maximum coefficient magnitude17. A source-bound scalar precision analysis
can use these facts. They are not a proof for a rounded native implementation.

## Verification and remaining obligations

Checks include the exact six frozen files, all 799 independent scalar columns
of both correction blocks, complete forward replay for both words and dense
reverse replay of all 638,401 coefficient positions in the new word. Every
single gate omission and doubling changes the correction operator. Three
full-word omissions/frame controls fail. Five invalid parameter/coefficient
controls and six actual source-byte corruptions fail.

The new verifier checks equality of all boundary headers and the entire
MOVE/INIT/CLEAR/COPY subsequence. It does not rerun native phase, physical
caller, price, compiler or outer proofs. Those claims retain the source
package's evidence and assumptions. The unchanged mathematical operator and
lower scalar allowance permit a consumer to test this replacement without
new paid transitions. Independent scientific acceptance remains separate.

The source full word uses formal INIT and CLEAR under its existing erasure
assumption. This work does not remove that assumption, implement a tape
machine, materialize the uniform multiplier, or alter the selected frontier.
