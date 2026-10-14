# Finite change and transfer boundary

## Fixed scalar word

Replay the operand pairs and roots of eumemic's PR117 DAG, as vendored by
PR118. Recompute cancellation-free source supports, types, ranks, the
2,024 disjoint outputs, 6,072 pair-star outputs and 24 retained centers.
The center decoder is Σ A_i / 21. The same deterministic maximum matching
has 71,185 links and compiles 28,705 physical roles. Its ordered scalar
operations and coefficients are unchanged.

For intersection size j, twice the resulting source-to-target coefficient
is j−1+[j=0]−[j=2], hence is zero except for j=3, where it is two.
Thus J M V = I over Q. The old readout is the exact signed transpose
propagation C=JM, not a Boolean approximation. The word

    −Cz; Vx; M; Jz; M⁻¹; −Vx

adds x to the target bank and restores arbitrary initial auxiliary data.
The inherited center dependency cut permits delayed negative readouts on
untouched roles that do not influence any center. Positive center reads
are copied at the zero target frame; their rank-23 transforms remain paid.

## Frames of physical operations

Work in F₂²⁴ with the standard symmetric bilinear form. Input injections
keep the original nondegenerate line spanned by the source triple.
Root frames remain the target triple's orthogonal hyperplane or the
retained center's coordinate hyperplane. Inverse cleanup reaches the full
space. Assign every scalar operation a common frame on both ports.

Initially, work backward from the root frames. Intersect the already
chosen future frames of the two physical ports. This cap contains the
operation's inherited orthonormal envelope. Orthogonally split off that
envelope, then apply PR115's norm-one/hyperbolic-pair elimination to its
orthogonal remainder. Discard only the radical. The resulting frame is
nondegenerate, contains the inherited envelope and lies in both future
frames. Different copies of a logical node may now use different frames.

Local optimization preserves the actual preceding and following frames
on both ports. If their preceding span L is degenerate, it can be
completed inside the current nondegenerate frame C: choose a nonzero
radical vector r and a vector y∈C with <r,y>=1, and adjoin y. Such a y
exists because C is nondegenerate. This increases the Gram rank by two,
decreases the radical dimension by one, and terminates in a nondegenerate
space of dimension dim L + dim rad L. A larger candidate is obtained by
the same orthogonal splitting inside the following cap. Every accepted
candidate is explicitly checked to contain both preceding frames and to
lie in both following frames.

These local substitutions preserve the common-frame scalar word and its
endpoint frames; they introduce no new scalar map. Each residual is the
orthogonal difference of nested nondegenerate frames. Alternating blocks
use the same general one-child Gauss interface already assumed in
PR104/117. Frame choices are optimization witnesses, not claims of global
optimality. Integer approximations to r log r are search weights only;
the claimed saving is checked by the exact rational moment enclosure.

## Partial deferred readouts and accounting

For an eligible untouched role with first frame A, intersect A with the
latest selected frame at every incident target and with its target
hyperplanes. Retain a nondegenerate summand σ. Execute selected readouts
in reverse selection order, giving ascending target chains. Selection
accounts for the changed first residual, exterior and each target front.
The audit checks actual subspaces, not just their dimensions.

A first residual of rank r becomes r−dim σ, and the corresponding
exterior width becomes m−h+dim σ. Every other literal transition, the
copied centers, data macros and endpoint copies are counted. With

    h=24, v=2024, m=576, N=4096576, R=28705,
    W=124390992, L=2234496,

the complete child rank mass is Wm−N+L = 71647349312. Both directions
are audited: reverse operation order, negate shears, exchange data banks,
and complement every frame. The independent incidence scan reconstructs
the full histogram and exact expanded scalar charge.

The unchanged bit profile and new complex profile are assembled with
PR118's stopped parameters. Rational moment enclosures prove contraction
at a_c=111216930/10^12 and reject the next grid point. The resulting
κ=111192082577/10^15 satisfies all 47 strict constraints and seven margins;
the next κ grid point is rejected too.

## Assumptions retained

This proves the stated finite local substitution and conditional numerical
witness. It retains the original analytic and fixed-tape framework,
simultaneous rational bases, routing/recovery, opposite-bank one-child
factorization, atom streaming and ordinary conversion, copied-center
implementation, exact odd-denominator grid, translated endpoints and
residual-to-child/all-size transfer. It is not a formalization of the full
integer multiplication algorithm. The bit word's previously established
frame proof is inherited; this package regenerates its SHA-bound ledger.

## Exact readout coefficient decomposition and paid scalar work

An exact transpose expansion of the PR117/118 scalar DAG yields coefficients
with numerators as large as 55 over the common denominator 42. The inherited
old audit's assertion that every coefficient has magnitude <= 1 is therefore
false for this DAG; modular replay alone does not prove unit-shear execution.

For each integer numerator n, write abs(n) = 42q + r, with 0 <= r < 42,
and implement the readout as q shears with signed numerator 42, followed
by one signed remainder shear if r is nonzero. The audit requires at most
two pieces per coefficient, each of magnitude <= 1, and verifies their
exact sum equals n/42. In particular 55/42 = 1 + 13/42.
The pieces operate at the same source, target, and binary frame:
their elementary shear E satisfies E^2 = 0, so they compose exactly
without any new frame transition or recursive child. Their inverse
negates the pieces in reverse order, with complementary reflected frames.

The forward and reflected scalar ledgers charge the actual number of
unit shears rather than only counting nonzero coefficients. The local
conservative scalar guard is doubled to
2*8*(c + 2R + (R+q)*v*(h+1) + h*h + h + 1).
The finite assembly certificate must be regenerated under this guard;
the recursive child histogram is unchanged. The unit-shear method and
control tests follow Rohan Arun's PR #118 correction (Apache-2.0).
