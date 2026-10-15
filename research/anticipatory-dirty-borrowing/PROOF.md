# Changed-reference borrowing with initial compensation

This is a fixed scalar/operator construction on the selected complex word.
It is not a complete hosted supplier or a new multiplication exponent.

## 1. Exact reference change

Use the Clifford-frame conventions of `notes/general-clifford-frames.tex`.
Let U be the retiring field's current frame. Let E have the same dimension
and lie inside the later helper's first common frame. Choose binary invertible
G with G(U)=E. The inherited exact monomial Clifford K_G has symplectic form

    [ G             0      ]
    [ G + G^(-T)    G^(-T) ].

It fixes L_0 and L_FULL and sends L_U to L_E. Therefore

    R_in  = T_E K_G T_U^(-1),
    R_out = F K_G^(-1) F^(-1)

have Fourier rank zero. R_in replaces logical state z by K_G z in frame E;
it does not equate the two frames. The inverse reference change is performed
at FULL during cleanup. This identity is inherited from the general Clifford
normal form; the package independently checks every column of every instantiated
exact Gaussian product, including scalar phases, for all 80 pairs.

## 2. Zero-response high helpers

The 12 selected rank-four/five block interfaces are pinned from Ali Romman's
`complex-block-rank-optimum` certificate. Each high helper has zero total
response to its incoming value after its helper-only correction. These
corrections commute to the block's first input, because no intervening operation
observes those helper values. This changes their lifetime.

At that boundary, 48 high helpers can use distinct retired fields. The arbitrary
incoming array becomes K_G z rather than the old independent dirty input. Its
zero target response permits this substitution. The full exact free-operator
replay checks this cancellation without assuming that K_G commutes with any
other basis change.

## 3. Initial compensation for low helpers

A low helper's incoming value has nonzero late target response. Reusing it
without compensation corrupts Y. In the fixed witness, its early prefix
operations are eliminated as follows: temporary additions to the low helper
are expanded into direct additions from their unchanged external sources;
the net temporary change is zero. The old low-helper dirty input and its
original compensation are removed. The remaining late target response to the
new K_G z is canceled by explicitly recorded initial compensation.

Each of the 32 low lenders has already been restored by the moved cold tail;
its logical value at handoff is exactly its own initial dirty input. This is
checked explicitly in the fixed replay. The key entrance condition is also
checked: all 64 compensation terms
read one of 32 initial helper inputs whose actual entrance frame is zero.
Each term has the form c K_G z, with dyadic c. K_G is monomial at frame zero,
so it can be applied to that helper, read into the frame-zero target, and
inverted immediately. No copied persistent array or paid transform is needed.
Every source is restored before the original preconditioner begins. No main
X input is used in this compensation; all 112 X inputs enter at rank one.

The non-target computation never reads Y. Its Y-only transfer is linear.
The publication verifier starts with the 64 **fixed** compensation terms and
then runs the entire changed word. It never solves for or subtracts a final
error. It verifies Y_i'=Y_i+X_i on every one of the 624 remaining independent
inputs over a free noncommutative operator algebra. This covers arbitrary dirty
inputs and all ordered basis-change words. Omitting the initial compensation
or changing a sign fails that actual replay.

This permits 32 additional low-helper aliases, for 80 total. The number of
physical helpers falls from 480 to 400; total independent fields fall from
704 to 624. All aliases have equal-dimensional handoffs in this witness;
no paid dimension-drop proposal is included.

## 4. Early cold tail and complete logical cleanup

The 48 original tail gates at rank at most four are moved just after the last
ordinary B use of each operand. Shared-operand order is retained. The separate
witness audit reconstructs those last uses from the source word and checks
every moved gate and its earliest legal boundary.

After B, exact dyadic row operations restore 40 cold inputs at their old frames
and remove their input columns from all other non-target rows. The remaining
non-target map is block diagonal, I on those restored inputs and an invertible
map on the remaining roles. Run the exact inverse non-target word at FULL,
using private zero buffers in place of the restored cold positions. The buffers
return to zero, and the remaining roles return to their input values. No
recursive child executes while those inverse-cleanup buffers are live.
The replay checks the zero buffers, all restored inputs and every inverse
basis change. Leaving out the inverse reference changes is rejected.

These are logical/frame checks. A production implementation must still price
its work, private buffer allocation, precision and tape and bind full native
phases, both orientations and owner lifetimes. A finite inverse replay alone
does not discharge those obligations.

## 5. Complete local rank profile and favorable rejection

The completed proposal has local profile

    {1:2382, 2:445, 3:406, 4:128, 5:42, 8:8},

including the unchanged COPY64 charge. Its paid rank mass is 5276, versus 5586
for the old word. The reduction of 310 local rank units is not a kappa claim.

The retained coverage relaxation puts every remaining rank unit into
fractional idle children of maximum allowed rank R, where 2R^2<m^2. It is
optimistic about hosting and idle packing. The package evaluates only odd
stage counts 7,9,11 from the affine pair-template shape, with
m=8L+1 and (L-1)*112 data families. No eight-stage controller is presumed.

For nine stages, the favorable primitive ceiling is enclosed in

    [0.001754331546940, 0.001754331546941].

At a=177/100000, the lower endpoint of the exact moment interval is greater
than one for every tested template. Thus even this favorable version misses
the campaign planning target. No full controller, owner map, opposite hosted
orientation, precision/tape admission, improved bit rail, 47-constraint outer
assembly or new kappa is supplied. The result is the changed local component
and a fully charged local profile, together with a scoped negative price check.
