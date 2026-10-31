# Independent review of the nonunit-row handoff

Prepared for @CubeJerry with substantial OpenAI Codex assistance by worker D,
independently of worker A's circuit construction. Apache-2.0.

## Result and independent method

The candidate's complete scalar word preserves every one of its 736 arbitrary
public inputs, except for the intended 104 main X-to-Y shears. Its eight owned
lifetimes return cleared and have peak simultaneous width one. Independent
integer arithmetic checks all 744 formal endpoint columns (553,536 coefficients), every
scalar chart, and strict binary-subspace nesting at every MOVE. The paid profile
is unchanged. Exactly one rank-nine helper is replaced by independently supplied
rank-five and rank-four helpers. The scalar allowance is 217,708, an increment
of 280 over the source word and 856 less than #6297's Euclidean construction.
The 744-column calculation includes eight initially inaccessible owned slots;
their formal initial columns are erased only by the prescribed INIT operations.
The independent productive-input count is 736, not 744.

`independent.py` imports no predecessor or candidate executable. It uses sparse
integer row vectors with a shared power-of-two denominator, separate from the
primary rational dictionary replay. Binary Gaussian elimination checks frame
containment without enumerating the predecessor's span sets. A separate forward
single-vector suffix evaluation checks the boundary direction. This supplements
the different rank-one surgery proof below. Neither a different random seed nor
a rerun of the original verifier is being described as independent mathematics.

## Rank-one surgery proof

All matrices here describe exact scalar action in their declared charts. Let
P be the prefix through the selected cut and Q the suffix; W=QP is the original
word's public endpoint. Owned values at this cut are absent, as checked from
chronology. W is identity on every helper and has no main/helper cross terms.

Let the cut row and column be v and u, with vu=1. Put a=vP and b=Qu. Assume a
and b are supported in a helper group sharing its source and target charts.
Choose invertible source and cut matrices R and C satisfying

    aR=e_p^T,  Re_p=b,  vC=e_p^T,  Ce_p=u.

All coefficients outside their displayed helper supports are identity. The
decoded state at the cut is D=C^-1 P R. Its pivot row is

    e_p^T D = v P R = aR = e_p^T.

Thus the retired pivot contains exactly its arbitrary original input x_p.
Replace that coordinate by a fresh independent input z, whose chart is the cut
chart. The change to the cut state is e_p(z-x_p). At the final boundary it is

    R^-1 Q C e_p(z-x_p) = R^-1 b(z-x_p) = e_p(z-x_p).

The unchanged part is R^-1 W R x=W x, because R acts only in the helper group
and W is identity there with no cross terms. Hence every other output agrees
with W, the old pivot exits early as x_p, and the new pivot exits finally as z.
Both are independent productive inputs. No public input is initialized to zero,
identified with another input, or replaced by correlated data. No dirty input
is discarded. This proof uses only the displayed row/column identities, so a
different complementary action in R or C is harmless.

For the concrete fixture, the independent prefix calculation gives a=v and the
suffix calculation gives b=-e_188-e_592+e_593+e_594+e_596. Both supports lie in
the 424-helper group with boundaries (3,127). The cut basis at frame 1053 has
rank five; its strict nesting between ranks zero and nine gives 5+4. The public
field previously numbered 596 retires at that cut, and new public field 735
starts there. Old owned roles shift up one and remain nonpublic.

## Column-unit factorization

Here b_p=1 for both source and cut pairs, though a has no unit coordinate. Put
T=I-e_p a_off, C0=I+(b-e_p)e_p^T, where a_off removes the p coordinate. Then

    T e_p=e_p,  C0 e_p=b,
    a C0=a+(1-a_p)e_p^T=e_p^T+a_off,
    a C0 T=e_p^T.

Therefore R=C0 T meets the two boundary equations. T is a product of the
displayed pivot-row additions and C0 a product of the displayed pivot-column
additions. Each block has a nilpotent off-diagonal part, so inversion is exact
by reversing the operations and negating coefficients. No division is needed
and no spare role is used. The same argument applies to the cut pair.

The lead supplied one further exact common-basis cancellation. Set
S=I+e_592 e_593^T. Replacing (a,b) by (aS^-1,Sb) removes coordinate 593 from the
row and coordinate 592 from the column: a_592=a_593=5/16 and b_592+b_593=0.
Compile the reduced pair by the formula above, then append S^-1. If that
completion is R', then R=S^-1R' has aR=e_p^T and Re_p=b. The pivot is unchanged.
The source pair now uses two T additions, three C0 additions and one final
S^-1 addition; the cut pair uses two, two and one. Source cost is
42+24+8=74 and cut cost is 42+16+8=66. Each matrix and its inverse occurs once,
so there are 2(6+5)=22 inserted additions with total allowance 2(74+66)=280.

The earlier 26-addition, allowance-368 construction was a superseded intermediate
candidate. Final endpoint/negative-control checks refer to the 22-addition
candidate. Every final operation is included in the independent replay's
allowance. The support argument below proves exact ADD-count minima for the
two separately completed dual pairs; it does not prove a minimum for arbitrary
whole-word rewrites or the weighted scalar allowance.

## Independent support-activation lower bound

The lead proposed the following bound, independently checked here. Starting
from (e_p^T,e_p), realize (a,b) by ADDs and arbitrary nonzero SCALEs. Let N be the
size of the final union of row/column supports and M their intersection size,
including p. Left multiplication by ADD(i,j,c) sends
b_i to b_i+c b_j and a_j to a_j-c a_i; no other support can change. SCALE cannot
create a previously zero coefficient.

Each of the N−1 final nonpivot roles must first become nonzero in at least one
of its two coefficients. One ADD can activate at most one previously blank
role. If it activates i, then a_i=b_i=0 before the gate, so its simultaneous
update to a_j is zero. If it activates j, then a_j=b_j=0, so its simultaneous
update to b_i is zero. Thus an activation introduces only one side of that
role's support and cannot create a second support on another role.

Each of the M−1 final nonpivot roles with both coefficients nonzero must also
undergo a single-support to double-support transition. These occur in gates
disjoint from the activation gates, at most two per ADD. Consequently at least
N−1+ceil((M−1)/2) ADDs are necessary. Cancellations, arbitrary nonzero scaling,
and extra ancillary roles initially blank in this dual pair cannot remove
these required disjoint events. The source pair has (N,M)=(5,4), requiring six
ADDs; the cut pair has (4,4), requiring five. The final circuits attain both.
Reversing a shorter inverse circuit would violate the same forward bound, so
four separately completed boundary maps require exactly 2(6+5)=22 ADDs.

This optimum is restricted to ADD plus nonzero SCALE and four separately
completed boundary maps for the fixed dual pairs. It does not cover interleaving
with the original word, a different handoff, arbitrary primitive gates, or the
weighted allowance. Elementary support counting is not claimed as new general
linear-circuit theory.

## Executed controls and limits

The independent verifier rejects changed/omitted boundary coefficients, an
unavailable chart, attempted zero initialization of the new public input, omitted
owned clearing, a false retired-helper exit, the wrong fresh-input chart,
a dependent frame basis, nonunit SCALE and nondyadic coefficient. Its explicit
conditions remain active under optimized Python.

This establishes the exact local scalar/frame/interface claim. It does not
replay native phase conventions, the complete outer caller, rounded arithmetic,
the finite uniform compiler, or the selected cold replay. Owned clearing remains
an inherited operation, not a newly implemented erasure primitive. Physical
native maps, outer use, precision/storage and the complete supplier budget remain
obligations. No new κ and no full multiplication theorem are claimed. The
selected frontier and all five framework assumptions are unchanged.

Credit unpaidmoon (#6297) for the concrete nonunit-row split and original
Euclidean bill; Ali Romman (#5611/#5602) for the dyadic completion and coupled
handoff; and the retained #5580, David Arias, Cinna Davis and Gareth Davidson
word/caller lineage. Worker A supplied the shortened circuit; this review does
not transfer scientific approval to unrelated predecessor claims.
