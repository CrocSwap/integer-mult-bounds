# Independent source, causality and tape review

Prepared for **@CubeJerry** by a separate source-aware OpenAI AI verifier.
This is independent exact arithmetic and interface review, not human review
or proof-assistant verification. **No new κ.**

## A different original-source check

`independent_oracle.check_source` reads the authenticated original
`Reference.entry("narrow",i,j)` values. Pivoted triangular elimination and
back-substitution invert the **full original window Q**; both inverse
identities are checked. Inverting `(Q^-1)_JJ` then reproduces F. This checks
the Schur identity through a different decomposition from the producer's
`D-C A^-1 B`, without using its A inverse or rounded-action function.

The checker reconstructs all original blocks, complete incident set E, J mask
and original coupling N. It verifies all nine products of the three block
masks of N are zero, the exact shear factors, and the F factor product. Its
page oracle separately inverts diagonal blocks and rounds by signed integer
division toward zero, including the **padded** upper reversal. The direct
exact first-window operator is also reconstructed from `(Q^-1)_JJ` and
original C0, acting on the actual current post-dense input.

For `Reference(61,3,2,1,3,32)`, both `[16,20)` with I=(1,2), J=(0,3), E=0..3
and `[16,24)` with I=(1,2,3,4), J=(0,5,6,7), E=(0,1,4,5,6,7) passed. Their
page-bank extents are respectively `16,0,16,0;16,0,16,0` (64 words) and
`32,16,32,16;16,0,16,0` (**128** words). The larger source was also checked
at source precision80; both use payload precision24. Wrong origin,
transposed F, omitted original coupling and reversed E fail specific checks.
These controls test source binding, not an online authentication guarantee.

## Nonlinear chronological oracle

`solve_pages` forms complete integer dot sums before each inherited residual
and diagonal-product truncation. It does not call the author's rounded solve.
`full_grid` executes whole axes in increasing order and reads each line's
current data, including changes made by preceding axes.

This schedule is justified by **flag-class causality**, not rounded
commutation. A complete E_f line has constant membership in every other E_i
and stays wholly inside E_f. The map preserves the flag class of every
address. Within each class, union rounds and increasing-axis execution give
the same increasing list of active axes. Distinct classes and distinct lines
of one axis act on disjoint addresses, so their interleaving is irrelevant
even when the local operation is nonlinear. Full4² and full8² finite observers
visit32 and96 records, including later lines with changed inputs.

A separate two-by-two dyadic control demonstrates noncommutation: coupling1/4
at precision2 gives numerator−1 in ascending-axis order and−2 in reversed
order. Reversed order happened to give the same words in the main source
fixtures; that coincidence is not used in the argument.

## Literal parsing and layout

`independent_transport` independently emits retained-schema big-endian headers
and little-endian two's-complement payloads. Helpers execute with count
decoding disabled and constructors sealed. Two complete E6 lines at prefixes2
and3 exercise a B4 cross-prefix layout and signed minimum−128. Raw headers
are archived exactly. Forward transpose is compared with a direct row/column
permutation; inverse transpose returns the original bits.

Executed rejections cover duplicate and deeply owned ports, moved input
origin, incorrect late ordinal, truncated final payload and a pending return
whose head stands at its blank terminator. Borrowed bodies/heads are checked
after rejection, and all2796 owned roles are erased at their origins.
Source review confirms encoded hot-path counters, fixed roles, a monotone
incoming scan, verbatim header return and logarithmically many lockstep
transpose stages. Global uniqueness, other-axis membership semantics,
catalogue authenticity and global union routing remain source premises.

## Separate physical support and failure controls

`support_control` calls actual unchanged physical `prepare_pages` and the full
owner on E=0..5, J={2}, B2, P2, w8, with
N[2,0]=N[2,3]=N[2,4]=1/4. These entries exercise lower, diagonal and upper
blocks. F is identity. Real input numerators3 at0,3,4 give staged output0 at2;
one completed shear-round would give−2, and the exact real value is−9/16.
Imaginary input is the negative. The complete physical call performs12 matrix
products and84 scalar leaves, preserves raw headers and borrowed pages, and
erases every owned role. This is explicitly a dyadic support control, not an
additional Reference instance.

`partial_control` uses E=(0,1,2), J={0}, B4, P2, w8, N[0,1]=1/4 and identity F.
Three complex lines at prefixes0,1,2 require two batches, the final one carrying
one line with both row and inactive-column padding. Actual page preparation
and the complete owner return the independent expected bits:8 matrix products
and392 scalar leaves. Truncating the final payload then fails after exactly
one completed batch,4 matrix products and196 scalar leaves. The completed
partial output and all2796 owner roles are erased; all borrowed bodies and
entry heads are restored. Thus the failure check occurs after real numerical
work and protected-output production, not just at an entry guard.

Source, transport and support checks passed ordinary and optimized Python.
The earlier E6/J4 online prototype's12 complex returns also match the
independent oracle exactly; its observer-prepared page words do **not** prove
actual retained page generation for that source.

## Executed main source and whole schedule

The final main replay uses the exact `[16,20)` source, cap2, B4, P24, w32.
The unchanged physical preparer completed all eight banks. Their64 scalar
words and all eight raw bit hashes match the independently reconstructed
original-source pages. Retained union steps around the physical window then
execute two rounds: axis0/round0 and axis1/round1, each with four complex lines
and two B4 batches. The whole replay has16 grid points,32 record visits and
784 physical scalar products. A later line consumes changed earlier data.

The returned full-grid hash independently regenerates as
`bf3f728125d578ee31d22da16491c3324877c2e56a606ebd164133c09cb9dff9`.
The original Reference description hash is
`156be0b0199657b95b636597b332b378a1fe82d1a80e8b9cc84eaf90425694c5`.
Actual numerical outputs, raw immutable headers, E-minus-J values, borrowed
restoration and owned erasure pass the integrated checks. This claim keeps
the finite host union harness outside the literal step5 implementation.
It is not a second independent implementation of the physical multiplier.

Review also removed an unstated carrier premise: the producer now checks the
explicit residual bound `Y+(c+b*eta)*4*M*Y+eta`, avoiding reliance on an
inverse-norm lower bound. Scalar carriers, wider exact products, copies,
restoration, cleanup and historical tape backing remain distinct charged
costs. Source rational heights and caches stay in the paid setup invoice.
