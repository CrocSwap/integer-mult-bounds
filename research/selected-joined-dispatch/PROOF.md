# Completed children on the same high packet

We connect full-ring preparation, generated weight evaluation and sequential
payload operations through an explicit child dispatcher. The retained physical
fallback code used a dense address-permutation oracle at this boundary.
Our child executes digit interchanges, controlled ADDs and signs, or a smaller
complete generic caller. We keep dense address maps in the checker only.

We prove the descriptor interpretation below for arbitrary complete fields.
The executable caller uses two complementary projectors in dimension two.
It provides a closed test of this interface, not an implementation of the
selected GL64 family/owner/hosting schedule or a new multiplication saving.

## 1. The embedded-child interpretation

Consider a packet whose order is

    [C] x [U] x [B]^n x [G] x [B]^n x [S],  B=q^w.

C indexes the complete frozen-control prefix. U is unused stock; G and S
are complete intervening and suffix fields. Every record has the same
payload width. Payload values may have arbitrary correlations.

Choose two ordered k-atom chunks, beginning at atom indices i and j, with
`0<=i`, `i+k<=j`, and `j+k<=2n`. Neither chunk may cross the old gap.
Let a and b be their positions in the radix list
`r=([B]^n,[G],[B]^n)`. Define

    U' = U product_(t<a) r_t,
    G' = product_(a+k<=t<b) r_t,
    S' = S product_(t>=b+k) r_t.

Then the very same serialized packet has shape

    [C] x [U'] x [B]^k x [G'] x [B]^k x [S'].

This is equality of lexicographic encodings: expand each collapsed field
back into its factors. The record order and complete volume stay unchanged.
The compiler performs no payload permutation to create this view.

Suppose a completed child applies

    F_A(H,D)=(A C_k D, C_k A^-1 H)

on those chunks, fixes its prefix and spectator coordinates, and clears its
local work. Here C_k reverses the k atom positions, and A is a diagonal unit
vector depending only on frozen controls. The same child, under the displayed
interpretation, implements the desired embedded operation in the parent.
This follows pointwise from the identical encoding and the child's identity
action on U', G', S' and C.

`Shape.child` checks the volume equation and interval conditions.
`ChildRequest.admit` checks the full record count, complete prefix count,
proper width, global field age and entry/return head position. A caller must
pass the entire packet described by that request. A loop that dispatches
one separately declared child per current high matrix is a different
interface, even if a particular endpoint happens to agree.

## 2. Actual full-ring fields and generated weights

Fix an odd prime q and w>=1. For a fixed low class g0 in GL_m(F_q), enumerate
the complete high cube and form `g=g0+qG` in `Z/q^w`, with m<=64. Each g is
invertible because its determinant is a unit modulo q. For a coordinate
projector E_I prepare `P=g E_I g^-1` with modular arithmetic.

The good branch requires its leading rank minors to be units. That property
depends only on g0, but the actual pivots and coefficients require the full
g. We retain the source527/PR2160/2171 normal form: unit-lower head/tail
adapters, the cross ADDs, one weighted child and inverse adapters. The
remaining Schur block vanishes over the full ring, not merely modulo q.
`algebra.good` checks this endpoint when preparing its coefficients.

For fallback, we retain first-unit-pivot, unnormalized elimination of the
full 2m-by-2m residual. We record the original-row permutation at each
reduction and reconstruct in reverse chronology. If the incoming weights
form the head-bank conjugator B_A, the weighted reduction state is
`B_(pi_t) M_t B_A^-1`. Thus a shear uses its own permutation snapshot;
the diagonal-pair child uses the final permutation. We retain zero slots.

The generated control program carries each ancestor's dimension, low/request
specification and global field slot. A child appends its actual parent header,
including its high values, to the frozen history. The iterative evaluator
then uses the full-ring Good or FallbackPair table for that field. Unit and
orientation children start weight one while retaining the global age.
The evaluator accepts no current-fresh-matrix or unused-stock argument.

This generalizes PR2310's prepared-table interpreter to dimension-aware,
actual full-ring inputs. The host implementation memoizes immutable matrix
preparations by their complete headers. Its keys include high values. The
control-cost argument may instead recompute these bounded-dimensional tables
with the local-control discipline of PR2310; we claim no host-cache access
bound as a Turing-machine primitive.

## 3. A completed base without a permutation oracle

For each pair `(H_i,D_(k-1-i))` with unit a, execute the retained chronological
word

    J, L(a), J, L(-a^-1), J, L(a), J, D<- -D.

Here J exchanges the two atoms and L(c) sends the later atom to D+cH.
Multiplication gives `(H,D)<-(aD,a^-1H)` for arbitrary input digits.

Implement J by exchanging its w corresponding radix-q digits. For one
digit pair, split the complete stream into q^2 sequential buckets indexed
by the two digits, then merge them in exchanged order. Every intervening
field and suffix travels as an opaque block. Reset and erase the buckets
before the next digit. This is a completed ordinary base, with no recursive
or address-map oracle.

For L(c), retain the full control prefix and all unused rows. Compute c from
the permitted frozen fields, hold the current source digit x, and rotate
the complete later B-block fibre by c*x. Split and merge sequentially.
Recompute the coefficients in the same order during merging. A sign pass
keeps block zero and reverses the other block positions while preserving
the records inside each block.

These operations prove the base for any fixed finite leaf cutoff. `leaf`
applies them to all k pairs and returns the same complete record count with
head zero. It allocates no child oracle. Payload records remain opaque.

## 4. A generic caller with real internal children

Let C reverse n atom positions, J be the two-bank reversed swap, and

    Q=diag(P,CPC),  R(P)=I-Q+JQ.

For a projector P, Q is idempotent and commutes with J. Since J^2=I,
expansion gives `R(P) R(I-P)=J`. Conjugating both residuals by
`diag(A,I)` gives the complete weighted endpoint F_A.

We use this identity with m=2, rank-one complementary projectors and
n=2f. Each good child has f atoms. Each fallback weighted/unit child has
f atoms; orientation reversals use floor(f/2) atoms. The dispatcher brackets
same-orientation field swaps by the required reversal of the later field.
Every positive child is smaller than n.

For dyadic n, choose the elementary leaf or the same complementary-residual
caller at a smaller width. Strong induction on n proves the full endpoint
and restoration contract. A finite experiment may send a designated unit
child through the internal caller while using completed leaves for other
small children; both alternatives implement the same F_A. This permits a
direct test of unit reset followed by another actual preparation/dispatch.

For internal calls let

    N=|GL2(F_q)| q^(4(w-1)).

Provide unused stock divisible by N^D, where D bounds remaining internal
depth. Decode one N factor as the current full-ring matrix field. Process
one low class at a time, retaining all its high lifts and all older controls
together. Select that whole packet by sequential scans, apply both residuals,
and replace it before the next low class. The remaining stock fits each
proper child. Preceding complete body fields may join the child's collapsed
unused prefix, but the reserved divisor remains available.

The completed operator fixes the current matrix field and unused stock and
acts as F_A on the body. The incoming A reads only older frozen fields, so
every current matrix row receives the same completed endpoint. Siblings
reuse the restored stock. We obtain a genuine generic complete caller.
Even the two ideal rank-one children have linear rank mass one; fallback
calls add further work. We claim no exponent saving for this generic caller.

## 5. Sequential payload parking and the measurement boundary

When an internal caller selects one low-class packet, it parks the inactive
complete source before running that packet. `Parking` appends one marker and
the source records to a single stack, erases the source work tape, and restores
only the top frame after return. Nested frames lie above that marker.
Restoration visits the frame's own suffix and removes its marker; it does not
scan an older payload frame. The checker retains a nonzero outer frame while
the nested child executes and verifies its exact return.

The interpreter uses 32-bit opaque payload records. A block copy is a macro
for sequential copies of those bits; all copied bits and head distances
remain charged. The stack uses 64-bit slots to distinguish markers from
payload values, a constant-factor representation change. Scalar and matrix
arithmetic uses host integers. Immutable control objects and return metadata
remain host data in this implementation; their fixed-tape encoding and cost
are the separate control/parking proof obligations. We do not call this a
complete binary transition-table compiler or infer an asymptotic running
time from Python timing.

## 6. Exact finite domains and limits

The width-two high tests use m=2, q=3, w=2, n=2, one fixed low class and all
3^4=81 high matrices. Each packet has all 9^4 body addresses, for 531,441
distinct opaque records. One low class is good and one is bad. In the good
class the pivot takes values 2,5,8, each on 27 lifts; the bad class has
P00=0,3,6, each on 27 lifts. Each child receives all 81 high rows together.

The nested test uses an actual 64-dimensional rank-four preparation to give
incoming weights `(2,1,1,1)`. A two-dimensional, width-one parent retains a
complete GL2(F_3) stock of 48 rows. One unit-reset width-two child executes the
generic internal caller and then completed width-one leaves. Other small
children use completed leaves. This tests global field age after reset,
fresh-stock restoration, same-orientation reversals and a buried parking
frame. The width-one nested experiment tests endpoint algebra; it is not an
instance of the production root-coupled asymptotic parameter choice.

The checker compares the first residual and the complete weighted endpoint
against independent direct formulas. It checks every record in the stated
packets, including unused, gap and suffix coordinates. Negative controls
target low-only generated coefficients, missing reversal, lost field age,
incomplete packet admission and insufficient fresh stock.

These are generic normalizer/dispatcher experiments. They do not enumerate
the selected GL64 family/owner/hosting payload, establish its full compiler
cost, replace native source certificates, or prove a multiplication exponent.
We credit source527, PR2160/2159/2171/2188/2207, the completed leaf in PR2234,
and PR2310's control continuation. Jose Manuel (`jmbarrancoml`) prepared this
work with substantial OpenAI Codex assistance. Independent review remains open.
