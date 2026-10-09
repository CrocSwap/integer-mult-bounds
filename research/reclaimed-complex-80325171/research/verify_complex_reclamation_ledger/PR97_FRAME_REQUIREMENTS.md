# PR97 h24 signed-frame requirements for a reclaimed supplier

2026-10-08. Independent source-level mathematical review. Exact PR97 head:
`f5f9c56e637463cac1e300d1589ccf42838f688a`.

## Verdict and evidence boundary

The generic common-frame reclamation/dirty-echo proof is compatible with the
PR97 h24 interface, provided a new literal supplier establishes the obligations
below. The existing accepted h28 witness is not an h24 witness. The current
h24 port is only a source/frame aggregate screen: R=40,011,
W=170,157,680, rank=98,008,965,648 and reported formal root
8.680840399e-5. No new event/GL witness or accepted physical supplier follows
from those numbers.

PR97 plus its separately identified local packaging overlay remains a
conditional frontier. This review neither replays PR97 nor reports its
published CI as passing. The overlay did not repair published CI or recover
the missing historical logs.

All code was read as mathematical text, never imported or executed. Local
byte hashes of the six specified scientific sources match `BASELINE_DELTA.json`.
The supplementary label source, `pr97_port/sources/frames.py`, matches its
recorded SHA256 `8629850bd465250cdf298b47b86504f2ac507d5fa044f8c0d2a20b451d19aa0f`.
No producer, replay, install, external write, Mac, Lean or Covering work was
performed. The comparison is with `FRAME_LIFT_REVIEW.md` and
`TWO_TERM_REVIEW.md`, not with the rejected reversed-transpose interface.

## 1. Exact signed word and h24 readout

Write L for the complete invertible original-role mixer, V for source
injection, and A for the signed side plus retained-center scatter. Chronological
forward operations are

    L, -A, L^-1, V, L, +A, L^-1, -V.

For arbitrary dirty z, the scatters contribute
`-ALz + AL(z+Vx) = ALVx`, and every original role returns to z. Thus `ALV=I`
gives `y += x`. After bank exchange the exact inverse is

    V, L, -A, L^-1, -V, L, +A, L^-1,

giving `x -= y` and restoring arbitrary z. This is the same valid inverse
echo as the reviewed h28 construction. It reverses chronological order and
inverts gates; it never transposes their directions. For elementary shears,
inversion negates the coefficient. Any newly introduced scale must instead
use its reciprocal, and swaps invert as swaps.

The h24 producer's retained centers are exactly 24, not 25:

- `E_i = sum_(t avoiding i) x_t`, for i=0,...,22;
- `T = sum_t x_t`.

For a target triple S, the complete readout is

    (1/2) sum_(pieces for S) cf(piece) z_piece + center(S),

where

    center(S) = T - (1/2) sum_(i in S) E_i,                 if 23 not in S;
    center(S) = -(19/2)T + (1/2) sum_(i<23, i not in S) E_i, if 23 in S.

Each side occurrence uses its own actual terminal association and signed
coefficient. `producer.emit` recursively splits a piece when its cover together
with S is full. Those split pieces cannot be replaced by the h28 terminal
list, or fused merely because their fresh signals agree. The source identity
checker encodes all 2,024 source coordinates exactly and checks every
2,024-by-2,024 readout coefficient; its existence is not a check of a newly
reclaimed physical terminal map.

Source anchors: `round6_complex_interface_controls.py:word`,
`check_complex_identity.py:main`, and `producer.py:NStar3.__init__, emit,
star_pieces, compile_roles`.

## 2. Exact data frames, connectors and auxiliary endpoints

Let P and Q be the odd triple lines in two 24-dimensional binary factors.
Use full ambient F, and define

    U = P tensor Q,
    T1 = F_24 tensor Q,
    B = P-perp tensor F_24,
    D_K = B orthogonal-sum (P tensor K),
    Kconn = P-perp tensor Q-perp.

Here rank(U)=1, rank(B)=552, and rank(Kconn)=529. The full data trajectory is

    initial:          (X,Y) = (U, 0);
    after forward:    (X,Y) = (T1, P-perp tensor Q);
    after connectors: (X,Y) = (D_Q, B);
    after inverse:    (X,Y) = (F, U-perp).

Both connector increments are exactly Kconn, not just arbitrary rank529
operators. Their orthogonal-sum phase differences are `q_Kconn`. In the local
factor the forward source runs line -> full and the target 0 -> line-perp.
The inverse source Y runs 0 -> Q-perp; its target X runs Q -> full. This bank
assignment is essential to the one-child correction.

Every stage-one original auxiliary starts at local 0, finishes at local full
(ambient T1), and then receives a rank552 exterior to reach F. Every stage-two
original auxiliary first receives the actual rank552 entrance `C_B`; its
complemented local trajectory then runs 0 -> full inside D_K, ending at F.
Consequently each auxiliary's total physical map is C_F, although the logical
echo restores its dirty coordinate.

This is a real convention change from the reviewed h28 lift: that review used
stage-two source gauge C_B and sink gauge `C_F C_B`, identity entrance, and a
rank756 exterior C_B. PR97 instead pays rank552 at the entrance and has no
second stage exterior after F. Both conventions can give C_F on the actual
input, but the paid operation cannot simply be omitted or moved by pretending
`C_B^2=I`. A new h24 ledger must specify which convention it realizes and prove
the resulting endpoint quotient.

The nonzero-sigma D-projector identities in `round7_tensor_endpoint_controls.py`
are useful bit/rational connector controls. They are not a replacement for the
complex q-phase proof. Baseline complex auxiliaries have local entrance sigma=0;
any new nonzero local entrance gauge requires its own paid phase/endpoint
accounting.

## 3. Copied-center timing and signs

At h24, E_i has the coordinate hyperplane omitting i, rank23, while T has the
full rank24 label. For each forward center with label S and rank r:

1. Finish its producer and keep the original unchanged at S.
2. Copy the complete stream, apply `C_S^-1` to the copy, and scatter at the
   early target frame 0 using the coefficients above.
3. Discard that copy; the original later advances S -> full, costing 24-r.

Thus each E_i contributes copy23 plus original cleanup1. T contributes copy24
plus cleanup0. There are 24 copies and copied mass `23*23+24=553`.
All center reads must precede the forward target's raise to its hyperplane;
side reads follow that raise. The inverse retains the opposite timing:

1. Early negative side reads occur while X is at D_Q. A side originally at S
   follows active `0 -> Q -> S-perp`, with ranks 1 and 23-r.
2. Raise X by its paid rank23 front to F.
3. Copy each center original at D_(S-perp); apply the positive residual `C_S`
   to the copy to reach F; perform its negative center scatter, then discard.
4. Complete every early read before the middle inverse producer consumes an
   original terminal; reverse and invert the literal producer at complemented
   labels. Raise Y from B to D_(Q-perp) after +V and before -V.
5. Final L,+A,L^-1 runs at full; Y has no further incidence.

For T the inverse original is at active 0 and its copy still pays rank24.
This is read-only reversed copying, not a transposed gather. Complementing an
edge `S subset H` gives `H-perp subset S-perp` with the same residual width.
The independent h24 event file must verify the actual subspaces and common
frames, not merely these rank identities or a sorted list of dimensions.

Complete copies include every control and spectator range, have original-role
volume 1/W, and use the retained sequential copy/read/discard work-stream
contract. Arbitrary dirty restoration applies to original roles; no stronger
reversible clean-ancilla uncompute claim is inferred.

Source anchor: `round6_complex_literal_ledger.py:54-113`, especially the
forward schedule at 82-89 and reflected copies at 103-107.

## 4. Signed data correction, with no characteristic-two cancellation

Put Phi=C_F, C=C_U, u=q_U(z), and w=wt(z) mod4. Starting with physical source
gauges `(C,I)`, the two shears and their stated terminal frames give

    X' = -Phi y,
    Y' = Phi C^-2 x + Phi C^-1 y.

The factor C^-2 is generally nontrivial. Pre-translate input x by `P_U 1`:
its Fourier multiplier is `(-1)^u = i^(2u)`, because
`q_U(z) mod2 = z dot P_U 1`. For these two triple lines the tensor generator
has weight9. After this pretranslation, `Y'=Phi x+Phi C^-1 y`.

Now copy X', apply the **inverse** rank-one child C^-1, add to Y', and negate
X'. This cancels the y term and gives `(Phi y,Phi x)`; exchange the banks to
return each original data role with C_F. There is one paid width1 child per
pair. Translation, negation, role exchange and inverse-child unit wrappers
remain actual local work, even though they add no recursive child. The
retained one-axis identity is `C^-1=-i Z C Z`.

Using C rather than C^-1 leaves `Phi(C^-1-C)y`; omitting pretranslation leaves
`Phi C^-2 x`. Neither is justified by F2 geometry. PR97's finite phase control
rejects these mutations, while the displayed algebra proves the general
identity. The h28 proof's generic cancellation can be reused, but its named
normalization cannot be imported without matching these h24 wrappers.

Source anchors: `PROOF.md:131-152` and
`round6_complex_interface_controls.py:phases`.

## 5. Reusable theorem versus fresh witness obligations

Reusable without a new principle: complete-coordinate invertibility of
common-frame elementary GL factors, signed fresh-signal clear/refill,
arbitrary-dirty echo cancellation, terminal-read separation, the corrected
inverse lift, complete-copy semantics, and the retained general nondegenerate
Gauss implementation. They apply to an arbitrary L once their hypotheses are
met. Dependency between incoming fresh-signal rows does not defeat a full
invertible physical block.

Still required for the new h24 supplier:

1. Frozen h24 graph/use/terminal bindings; exact signed source rows; all T/E
   and split side occurrences; exact terminal-derived ALV=I.
2. Literal original-role initialization, common-frame block factors and their
   inverses, clear/refill gates, pending-use ownership, all control raises,
   retirements and cleanup. V must really be the specified injection block
   before the middle L, with disjoint read-only data source and auxiliary
   banks; any rearrangement needs its commutation proof. Signal-zero does not
   mean dirty-zero, allocation, or deletion of an original degree of freedom.
3. Actual binary inclusion and nondegenerate residual proofs for every new
   edge, both orientations, copied centers and the source/target schedule.
   PR97's original checker only accepts nonalternating residuals. If a new
   edge is alternating, explicitly invoke and charge the more general
   inherited compiler and its basis/phase wrappers. The screen reports no
   added alternating residuals; that aggregate report is not a literal check.
4. All auxiliary endpoints above, both rank529 connectors, all four rank23
   data fronts per pair, and the signed inverse rank-one correction.
5. A complete histogram, scalar/coefficient/depth and wrapper counts, followed
   by fresh precision, stock and assembly admission where claimed. Neither
   the old h28 gate count nor PR97's baseline G=1,531,908,928 can be assumed
   for a modified L. Any newly non-dyadic coefficient needs the reviewed
   rational-grid hypotheses; the old h28 unit-coefficient finding is local
   to that witness.

For R remaining original auxiliary roles per invocation, the required
bookkeeping form is

    v=2024, N=v^2=4096576, m=576;
    local auxiliary-plus-copy mass = 24R+553;
    W = 2N+2vR;
    whole children = 2vR at552, 2N at529, 2v copies of the local list,
                     4N at23, N at1.

The local list here excludes the separately stated data fronts. Its total
recursive rank is `576W-1,858,032`; maximum child is552. This bookkeeping is a
necessary consistency check, not a substitute for the literal records.
The reported h24 screen satisfies the proposed aggregate shape, but this
review does not elevate its profile, approximate root, or upstream receipts
to a realized supplier or a new assembled multiplication bound.

## Subsequent frozen-witness acceptance

The source-only requirements above were subsequently bound to a fresh frozen
h24 event witness. `H24_REVIEW.md` and `H24_CHECK_RESULTS.json` record the
independent acceptance:402,941events, exact ALV=I, full paid histogram and the
PR97-specific entrance/terminal/correction conventions. This later result does
not come from the old h28 acceptance or from the original aggregate screen.
