# V45 access, consumed directions, and the remaining cost allowance

## Exact model

Let D = Z[1/2]. For each pinned provider let L be its 520 live non-target
registers. The input cut is immediately after the 84-event prelude. Give every
register in L an independent arbitrary entrance value in a D-module W. The
middle M is the non-target part of A after the prelude, then B with its
chronological formal warps, then restore. Formal warp generators act by
arbitrary invertible D-linear maps on W. Target writes, compensation, inverse
cleanup and native/physical realization are separate obligations.

H consists of live helpers with index at least 224, excluding restored
`helper_final` coordinates, `start_extra` coordinates and initial-correction
sources. Its size changes with the construction. In particular P =
{249,251,265,267} is eligible before the PR2942 extraction and protected afterward.
A zero entrance frame does not mean a zero entrance value.

Fix V45 = span_F2(256,128,64,35,16,11,5), and the twelve-register allowance
U = {2,61,62,63,70,71,72,94,249,251,265,267}. Define R(V45) by replaying every
literal frame incident and selecting all live non-target registers with terminal
frame contained in V45. Protected/restored rows remain in R. This is not the
historical solver-lowered support search: U is an explicit algebraic observation
allowance, and its physical availability must be established separately.

As in the pinned source, separate target-add records use the inherited center-cut
convention. The frame replay checks the recorded center frames and the literal
A/B/restore scalar incidents and warp resets. It does not reconstruct additional
native moves for those separate target records.

## What the exact comparison establishes

Both providers give the same dimensions and supports below. The checker uses
all coefficients of each observed free-operator row, rather than specializing
warps to commuting or identity maps.

| Construction | Size of H | Literal R(V45) | Scalar left/right/pairing dimensions on U |
|---|---:|---|---|
| PR2894 | 226 | empty | 4 / 4 / 4 |
| PR2917 | 216 | empty | 4 / 4 / 4 |
| PR2942 | 212 | empty | 0 / 0 / 0 |
| PR2979 stage 1 | 212 | U | 0 / 0 / 0 |
| PR2979 final | 207 | U minus {61,63} | 0 / 0 / 0 |

The complete rows M[U,:] are equal between PR2894 and PR2917 (98 nonzero
coefficients), and equal between PR2942, stage 1 and final (42 coefficients).
The four-dimensional old pairing has determinant -128. Eight selected nuisance
columns B0 have an eight-row minor of determinant -2, and the twelve-column
completion [Y,B0] has determinant 256. All are dyadic units. Thus
PR2917 did not create these four directions on U: they were already available
algebraically in PR2894. Neither old shipped circuit makes U available at V45.
The paid frame and boundary changes are essential to the implemented recovery.

On every later word, M[U,H] is identically zero. This is stronger than a rank-zero
pairing. Moreover the U nuisance rows admit a purely scalar square minor on
protected columns with determinant 2, a unit of D. The final ten-row literal
support has a protected scalar unit minor with determinant 1. If P is returned
to the eligible set solely as a diagnostic, the left/right/pairing dimensions
are again 4 / 4 / 4. The four rows indexed by P are their restored identity rows.
This does not authorize treating those protected helpers as fresh resources.

## The old quotient over every dyadic module

The receipt records four covectors Alpha, four eligible quantities U0=Alpha M,
four eligible columns V, and Y=M V, with Alpha B0=0. Set K=Alpha Y. Both
K and C=[Y,B0] are invertible over D by their unit determinants. Every readout
has unique coordinates Y a+B0 b, and Alpha reads K a. Consequently
ker Alpha=im B0 on W^12 for every D-module W. Since all nuisance columns lie
in ker Alpha and B0 consists of nuisance columns, im B=im B0.

Two eligible states h,h' can yield a common U readout after choosing independent
nuisance values exactly when U0(h-h')=0. Every exactly recoverable function of h
therefore factors through the four displayed quantities U0 h. Conversely they
are read directly by Alpha. This proves the quotient description over D-modules,
not only a dimension statement over Q. For nonlinear H-only recoding S, replace
U0 h by U0 S(h); no four-scalar information-capacity bound follows for unrestricted
nonlinear encodings. The later zero-block obstruction below remains unchanged.

## No fresh nonlinear recovery on the later words

Write the entrance tuple as (h,z), with h on H and z on L minus H. For every
later word the complete U observation is

    y = M[U,H] h + M[U,L minus H] z = B z.

Fix z and vary h arbitrarily. The observation remains identical. Any function
of h exactly determined by this observation for every independent entrance tuple
must therefore be constant. This argument also permits an arbitrary H-only
entrance recoding S(h), because the coefficient of S(h) is still zero. No
statistical distribution or information-theoretic entropy assumption is needed.
Ancillas may be fixed or jointly independent of the entrance tuple; data-bearing
side observations are outside the contract. The unit minors independently
certify nuisance saturation but are not needed for the stronger zero-block step.

The conclusion holds for every D-module and every allowed representation of the
formal warps, since zero formal coefficients specialize to zero operators. It
does not require freeness of the specialized native operators.

A finite appended computation inherits this conclusion if every data and control
dependency is explicit, frame inclusions are monotone, its output identities and
frames are fixed, and it uses no new warp resets or additional source, target or
earlier-snapshot reads. Every initial register in the causal cone of an output
at V45 must have terminal frame contained in V45. Therefore that output depends
only on R(V45), a subset of U, and independent ancillas. Arbitrary nonlinear
local gates and additional intermediate buffers cannot supply missing h
information. Pooling incomparable endpoints or changing the middle is not covered.

## Paired rank is a separate condition

For a fixed observation set, define the scalar left space by alpha M supported
on H, and the scalar right space by M v supported on that set with v supported
on H. Pair them using alpha M v. The reported dimensions are exact rational
formal-space dimensions with explicit witnesses, not a universal native-cost
claim. A zero pairing alone would not establish the nonlinear result above:
for M(h,z)=(h,h+z), observing the first coordinate recovers h, although
M^{-1} e_1=(1,-1) is not supported on H. Here the complete zero eligible block,
not the absence of a normalized pair by itself, establishes the obstruction.

## Complete-cost decision

The four directions and their V45 endpoint saving already occur in PR2979.
They cannot be counted again. The published frozen-owner audit PR3014 also
shows that the local V45 saving can lose after idle capacity is charged; that
existing result is credited, not presented as a new calculation here.

The accompanying exact cost certificate derives a marginal screen in PR2979's
fixed bin-capacity relaxation. At its rational complex parameter b0, use
H_r(b0)=r(73/r)^b0. One freed width unit raises the optimal fractional idle bill
per call by

    D(b0) = (H_48(b0) - H_3(b0) - 5 H_5(b0))/20.

The checker solves the retained basis with exact rationals, verifies nonnegative
changed counts, and checks every feasible pattern against the dual with rigorous
rational tariff intervals. Thus it proves the marginal at b0 for the specified
single-helper inventory changes; it does not assert that the basis stays optimal
for all parameters.

For a hypothetical new 9-to-7 helper with local difference E - 2 H_1, the best
fractional local-plus-idle difference is E - 2(H_1-D). This leaves approximately
0.0246870954232 tariff units per call for E. The finite literal comparator has a
small additional fractional slack, explicitly certified in the receipt. This is
a necessary screen within the fixed-capacity model; it does not pay new private
buffers, the actual paired residual T_out T_in^-1, physical access, precision,
stock or a changed compiler interface. Those
must be constructed and charged before any positive supplier claim.

The bounded comparison finds no unused direction in U on PR2979. It therefore
does not nominate a new extraction to send through owner/native/outer admission.
A cheaper realization of the four existing directions is not excluded. The
observed-row equality does not provide new compensation identities or a strict
paid advantage for moving extraction earlier through other stages. PR2942
already reports optimization of extraction order within its fixed gate-order,
end-of-restore model; that historical result is not a global optimum for PR2979.

The stopping decision is specific: adding a decoder or an H-only recoding on
this frozen observation contract cannot produce a fresh V45 helper. Changes to
the middle, cut or accessible coordinates remain possible, but require a new
mathematical and cost argument. No improved kappa or global optimality follows.

## Evidence boundary

This is an exact finite comparison plus written proofs for all entrance values
and allowed finite suffixes. Two separately implemented operator propagations
check the observation claims. The cost arithmetic reuses the credited retained
rational interval kernel. No formal proof assistant, independent human review,
new native supplier, complete physical invoice or all-size multiplication theorem
is claimed.
