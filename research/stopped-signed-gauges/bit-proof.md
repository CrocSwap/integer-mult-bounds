# Whole-rank stopped recursion on the frozen h25 rational-frame word

This is a new composition of existing finite words with icekylinx's PR104
opposite-bank factorization and stopped atom interface. It retains the analytic,
streaming, ordinary-leaf, exact-grid, and all-size machine hypotheses of that
interface. It does not change a published word. The original scalar/frame
compiler, arbitrary-dirty replay, deferred storage, coordinate relabeling and
attributions remain in the durable `merged-span-frames` dependency closure.

## Every residual is a proper projector

For the selected dimension h = 25, let H = 9I − J. Its eigenvalues are 9 and 9−h, so H
is nonsingular. The frozen words use the following rational subspaces E(C,U):

- If C = U is a triple, E is spanned by its incidence vector, of H-norm 18.
- If |C| = k ∈ {1,2}, E has basis
  `v_i = 1_C + (3−k)e_i`, for i ∈ U\C.

For r = |U\C|, the Gram matrix is

`G = 9[(3−k)^2 I_r + (k−1)J_r]`.

Both its eigenvalues are positive. The exact inverse used in
`bit_profile.py` is

`G^-1 = I/[9(3−k)^2] − (k−1)J/[9(3−k)^2((3−k)^2+(k−1)r)]`.

Thus `P_E = V G^-1 V^t H` is an H-selfadjoint idempotent of rank r. The checker
verifies this Gram identity and inverse for every frame class occurring in the
actual word, with no modular rank inference.

The finite containment conditions C_new ⊆ C_old and U_old ⊆ U_new imply
E_old ⊆ E_new. Indeed vectors have a common coordinate λ on C, vanish outside U,
and satisfy `sum_{i∈U\C} x_i = (3−|C|)λ`; shrinking the core moves equal λ
coordinates into the left-hand sum. The triple-line case satisfies the same
condition. Every serialized incidence is checked against these inclusions.

For nested nondegenerate subspaces, their orthogonal projectors satisfy
`P_new P_old = P_old P_new = P_old`. Consequently
`(P_new−P_old)^2 = P_new−P_old`, with rank equal to the dimension increase.
Retirement uses the projector I−P_E. For a side target triple T, its indicator
has H-norm 18. Each side output lies in the nondegenerate hyperplane T^⊥:
every basis vector `e_c+2e_i` has coordinate sum 3 and intersects T in 1, hence
its H-pairing with 1_T is `9−9=0`. The growth
`I−P_T−P_output` is therefore a projector of rank 2. The remaining target-line
projector has rank 1. These two calls are kept separate. Copied centers use the
same E projector and its rank-one complement; the copy remains paid.

Each local residual is tensored with the opposite-axis rank-one projector, so
its ambient rank is at most h < m = h². Auxiliary exteriors
`I_m−I_h⊗B` have rank m−h. Data residuals `(I−P)⊗(I−Q)` have rank (h−1)².
The copied first-output correction has rank 1. Every nonzero residual is proper;
zero residuals incur no recursive child. Reversing an edge and complementing
its endpoints gives the same difference projector. Both orientations' boundary
families are included as well.

## Common rational basis and opposite banks

PR104's stated factorization applies to every finite family of proper rational
projectors, without requiring a positive ambient metric. For each rank-r
projector, each leading principal minor through order r is a nonzero polynomial
on a rational similarity orbit: a basis placing r image coordinates first
witnesses this. The finite product of these polynomials is nonzero on GL_m.
Choose one rational basis satisfying the complete family, including both
orientations, all data pairs, exteriors, local differences, centers and cleanup.
Choose the fixed odd address prime away from every denominator and pivot factor.

Any frozen coordinate relabeling or fixed I+J similarity is absorbed into this
common similarity. The whole physical network is globally conjugated, so frame incidences,
source/scatter identities and arbitrary auxiliary restoration persist. The
opposite-bank convention then supplies exactly one reversed recursive child
of width r for each rank-r residual, under PR104's retained factorization and
atom-streaming interface. The dense basis is fixed address-label preparation,
not a free executed data transform. The stopped wrapper is applied once outside
the recursion, with the ordinary-leaf interface and adapter toll paid.

## Complete ledger

`bit_profile.py` independently reconstructs the positive incidence multiset from
the literal source injections, every emitted XOR and every output, and compares
it with the serialized event list. Repeated zero-rank incidences do not create
children. It then adds every retirement, side growth rank 2, target-line rank 1,
retained-center copy rank h−1, and original-center cleanup rank 1.

The local copied histogram H' satisfies exactly

`sum_r r H'_r = h R + h(h−1)`.

The pre-copy histogram supplied to PR104's unchanged profile function simply
reverses its documented replacement, H_h += h and H_1 -= h. No physical gate is
removed. For the square pair, with v = C(h,3), N = v², B = vR, W = 2N+2B and
L = 2v h(h−1), the complete children are:

- 2B exteriors of width m−h;
- 2N data residuals of width (h−1)²;
- 4N data-front transforms of width h−1;
- 2v H'_r local children of width r;
- N copied first-output corrections of width 1.

The checked total is `Wm−N+L`, strictly below Wm. All widths are below m. The
exact rational upper moment is strict at the selected coarse saving; the next
10^-14 grid point is rejected. With θ = 1/1000 and the retained ordinary saving
384599/10^10, the stopped saving is `(1−θ)a_coarse + θ a_old`, and θ is larger
than that saving, so the adapter term remains subordinate.

The exact selected saving and final three-stock assembly are authoritative in
`certificate.json`; this module does not choose them. The local pre-copy axis
convention is recorded in `bit-axis.json`, while `bit-audit.json` records the
actual copied histogram and each separately paid component. Fields
`literal_shear_operations` and `output_ports` describe the physical word; they
are not precompiled scalar-DAG addition/matching counts.

## Fresh word and independent acceptance

The gate regenerates the frozen h25 word into `WORK/bit/word-25.json.gz` using
the retained producer. `bit_profile.py --work WORK` requires its bytes to match
the frozen source hash and runs a separate Python interpreter importing the
source-pinned `merged-span-frames/check.py`. That child executes `strict_word`
(the exact scatter inventory, nonnegative index checks and literal chronology)
and the full inherited `binary_frame_replay.replay`, including both arbitrary
initial bases. Its result must equal the frozen `replay-25.json`. It does not run
obsolete fixed-basis corner/CRT or merged-exterior pricing experiments.

The new standard-library audit then independently checks the frame classes and
all incidences, reconstructs the complete rank ledger, and compares the fresh
axis and audit receipts to the frozen ones. Its five negative controls reject an
omitted rank-two side call, a rank-preserving replacement of that call by two
singletons, an omitted retained-center copy, an uncopied center cleanup, and a
negative multiplicity. Thus total rank alone is not the acceptance criterion.
Default execution writes only scratch outputs. `--record` deliberately records
the two local evidence files when preparing the package.

This composition uses the physical word held by `merged-span-frames`, but no
PR96 endpoint merge or its profile is used here. Every ordinary auxiliary
exterior remains paid separately. The entire new projector list is transported
by one common rational similarity, including both orientations and all inverse
and boundary residuals. No source-control map, copy, reversal or dense data
basis transformation is silently removed.

## Attribution and scope

The retained word and source closure credit the paired/shared graph,
frame compiler, matching, dirty reconstruction, deferred storage and coordinate
refinements to their original contributors, including Chafik Boukhalfa,
Avi Eisenberg, Rohan Arun, Maxime Fleury, eumemic and the predecessors listed
in the preserved `NOTICE` files. Thomas DiFiore prepared this composition with
OpenAI Codex assistance. The opposite-bank full-involution factorization,
stopped atom interface and rational-center construction are icekylinx's PR104,
with the AI assistance recorded there. Original Apache-2.0 licenses and notices
remain intact. The copied-stream and two-stage topology, semantic/bulk,
ordered-affine, exact-recovery and all-size fixed-tape interfaces retain all
credited hypotheses and dependencies. This is a conditional composition, not
an unconditional integer-multiplication theorem or a practical runtime claim.
