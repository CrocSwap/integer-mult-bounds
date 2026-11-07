# Shrinking only a critical hub projector does not remove the cut

Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
This is an addendum to PROOF.md, with the same native vectors and conventions.

At the last R0 stage allow a projector of the form H_R plus the coordinate
projector on h_(b-1), where H_R acts only on the two-dimensional hub. At the
first L1 stage allow H_L plus the coordinate projector on f_0. Require each
full projector to fix its native image and covector on the appropriate side.

An idempotent hub H fixing a nonzero u on the right and v on the left has
rank at least one. In dimension two, rank two forces H=I. If it has rank
one, its image is span(u), so H=u w^T; the condition vH=v and vu!=0 fixes
w^T=v/(vu). Thus the only new possibilities at these two cuts are

    H_R = B(B*-A*),        H_L = B(A*+B*).

For the R0 prefix use output rows B,h_(b-1), and the same input columns
f_0 from L0 and h_(b-2) from R0. The full cross block P Q_0(I-P) has minor

    [[       *,         2],
     [-4(-1)^(a-1),    0]],

of determinant 8(-1)^(a-1). The second input columns are unaffected by
I-P. For the first, its post-L0 A value is alpha=2(-1)^(a-1). R0 leaves
last-private value -2alpha: in an R chain driven by incoming hub value
alpha, the covector readings alternate alpha,-alpha,...; the preceding
queries give last-coordinate value zero or -4alpha, and the last update
leaves -2alpha in either parity. The penultimate-R0 input finishes with
hub 2B and last-private zero. Applying H_R preserves that B value.

For the L1 suffix use output rows B,f_0 and input columns f_1,last-R1 h.
The cross block has minor

    [[      *,       2],
     [4(-1)^c,       0]],

of determinant -8(-1)^c. Starting from f_1, after the second L1 query
f_0 equals twice the B coordinate. All remaining L1 updates preserve
that relation, yielding f_0=4(-1)^c. R1 does not touch f_0. Starting from
last-R1 h gives hub 2A, which H_L maps to 2B, and f_0 stays zero.

Both cross blocks still have rank at least two. Therefore any hub-only
rank reduction of these critical supports retains the two-plus-two thin
lower bound, provided the same endpoint premise is imposed. This is not
a claim that the two reduced projectors commute with each other; in fact
their hub parts generally do not. Reducing either one alone already fails
to evade its respective cut.

The verifier checks these two additional minors for all admissible length
pairs in 1..8: 56 prefix and 56 suffix cases. Their all-length conclusion
rests on the formulas above. Supports that mix hub and private directions,
different private support incidences, or changed native vectors remain
outside this addendum.
