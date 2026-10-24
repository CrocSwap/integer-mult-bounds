# Independent review of the finite tagged reset

Result: accept the local finite-grid theorem in
`schur-selection/finite-grid/GRID-RESET-PROOF-V2.md`, SHA-256
`40fa4d2cbd2a6cfa3a7ec6facd81e04af727b18d77bed11643b13f19e38428e7`.
The first proof has a parent return-format error. Version 2 corrects
that error and the stated fine-centre margin. The old proof is retained
as review history. It must not be used without the corrections.

The result is a local backward word on finite physical grid inputs.
Its ideal endpoint is the unit backward data map, with all 480 helper
contents restored in their inherited output frames. The word uses one
existing owned private field. It has no new native child. It is not a
complete supplier, a complete recursive invoice, or a new kappa bound.

## Exact local word and arbitrary inputs

The independent checker reads the pinned raw word, matrix, schedule,
and canonical frames. It imports no producer or campaign module.
It replays all 704 independent initial inputs, including every helper
input. It checks every scalar access against its current native frame.
It retains every native event and checks every native input frame and
the final frame list. The accepted raw native phase recipes are an
explicit dependency. This review does not replay those recipes again.

The exact centre inputs at event 12995 are

    u_k + R_k Y/4.

Replacing those inputs by u_k and omitting the eight signs gives

    X_out = X-Y,  Y_out = Y,

with every helper content restored. The finite decoder acts on physical
coefficients in the actual centre frame. It does not move a scalar
map across unequal frames. The independent physical review is
`centre-reset-review/REVIEW-V2.json`; the earlier plain-product phase
argument has been superseded.

The input tag uses a cleared owned field, a power-of-two SCALE, and
an ADD. It does not use SCALE by 1+delta. Each centre decoder uses the
same owned field in the centre's current frame. COPY has a zero target,
and CLEAR restores the owned field before its next use. No arbitrary
helper input is assumed to be zero or is cleared.

The literal schedule tags all 224 data inputs, rounds all 696 other
cut fields, decodes the eight centres, and rounds all 704 outputs.
The independent count is 232 COPY, 240 SCALE, 240 ADD, 233 CLEAR,
and 1416 ROUND field operations: 2361 added passes in total.
These passes have a new finite bit cost. They are not included in the
old scalar coefficient. A complete tape invoice is still required.

## Rounding and the corrected error contract

For h and q on the Delta grid, the literal decoder first obtains h+q
by a coarse snap. It then subtracts that value, divides by delta, and
snaps again to obtain q. Its final subtraction gives h. The stated
strict margins keep both snaps away from a rounding boundary.
The checker executes 11025 exact signed cases through the actual
eight-operation decoder. It also gives a stronger failure control:
an error Delta/32 satisfies the coarse error allowance, but fails the
fine extraction. The first snap is still correct in that control.

Every added arithmetic operation can be exact in the declared format.
The tag denominator is at most 2g+H+G+4, which is no greater than
2t+P. After subtraction of the snapped baseline, multiplication by
delta^-1 reduces the fractional length. The residual is bounded by
the query bound, so it does not require a large baseline intermediate.
Both rounded values are on a grid that the parent format contains.
Their signed difference is exact. The final Gamma grid also fits.

The original proof placed parent return-grid rounding inside the child
relative-error contract. That is not valid for a fixed parent format.
For example, take a native C1 input equal to one parent grid unit.
One output component is half that unit. Rounding to the parent grid
has relative error at least 1/2, even if the child computation is exact.
Version 2 correctly charges this rounding as a separate absolute error.
Only the normalized child computation and input conversion belong to
the child relative-error guarantee.

There are at most 25457+3486+2361=31304 local error insertion sites.
This includes a separate parent return error after every native child
and is less than 2^16. With P=2Be+2H+4G+32, the exact exponent margins
are at least Be+H+2G+10 at the coarse cut, G+6 at a fine centre, and
Be+G+10 at the final output. They are all positive. The checker verifies
the integer identities and format inequalities on 96 parameter cases;
the all-size conclusion follows from those displayed identities and
g<=t+Be, rather than from the finite cases alone.

The finite perturbation argument uses errors on actual native inputs.
Write each approximate child output as its exact action on that input
plus its complete output error vector. Exact suffix maps propagate
these errors. A zero centre response is therefore valid even when the
error depends on earlier approximations. The proof does not assume an
approximate child output remains on a coarse grid. Parent return errors
have the fine absolute allowance even at ordinary-accuracy children.
The norm is the maximum real or imaginary coefficient; it introduces
no factor equal to the number of coefficient records.

The theorem starts after the input is on its declared grid. A finer
caller's coarse entry conversion is not in this fine error budget.
That conversion needs a separate complete-node error proof. Exact
local helper restoration refers to the grid input, not to a finer
record before that conversion.

## Fine native responses and resolution

The independent reverse calculation finds exactly 132 native output
error spaces that reach a centre. The profile is 124 rank-one jobs
and eight rank-four jobs, of total rank 156. Every input has both a
data part and a helper part. The checker compares every source row
and every centre response with the published receipt. It then sends
a separate forward impulse through each of the 132 native output
fields and obtains the same eight-component response.

This validates the sufficient accuracy assignment under arbitrary
independent relative child errors. It is not a lower bound for a child
contract that has correlated or lattice-restricted errors. The later
reset-policy enumeration is a separate theorem and is not certified
by this review.

The fixed nonzero carrier witness in version 2 corrects a limitation
of a zero-baseline witness. The actual minor satisfies R_A R_A^T=4I.
With h0=e0/8, v_k=s_k e0, and u_k=h0-v_k, the physical carrier is

    (1/8+delta*s_k) B_k e0.

The nonzero vector B_k e0 cancels in the relative separation. Thus
normalizing a small carrier cannot evade the two-copy accuracy scale
on this family. More precisely, for positive scalar carriers a<b,
the relative error balls meet at radius (b-a)/(a+b). The checker gives
their common observation and checks 27 exact cases. This establishes
the stated order delta*2^-g without a frame eigenvector assumption.
It bounds only a decoder that receives the packed carrier. It does
not assign a cost to a native job or rule out new reads and codes.

## Scope and reproduction

Run:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/paired-package-review/tagged-grid-review/check_tagged_grid.py

Expected status: `PASS_INDEPENDENT_TAGGED_GRID_LOCAL_CONTRACT`.
The checker also accepts `--out` for a separate output path. It writes
only its own receipt and preserves all producer files.

The inherited native rank is 5522. The extra-accuracy rank is 156;
the eight removed rank-eight jobs have mass 64. Thus the all-eight
choice has an adverse local rank change under this width model.
The arithmetic 64*(156-64)=5888 is exact. This review does not re-audit
the historical global deficit or the selected complete call schedule.
The exact global comparison remains with the source and pricing lanes.

Open work includes the complete node endpoint on approximate caller
records, all finite tape and record costs, and any construction with a
favourable complete precision moment. No PR, commit, or push was made.
OpenAI Codex supplied this independent review. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
