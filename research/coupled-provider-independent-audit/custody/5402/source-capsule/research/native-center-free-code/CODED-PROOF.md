# An exact center-free native offer with an invertible eight-mode code

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

Building on Cinna Davis's center-free cache kernel in PR #4694, this gives an explicit free ground-chart helper pre-compensation and an invertible eight-mode main code: all eight rank-eight center Gaussian calls disappear, all 408 independent helper jobs remain, and the main cross-transfer is an explicitly known invertible constant code. It is not the old uncoded main ABI and does not by itself prove a new κ.

## The exact offer

Freeze the native source payload with SHA-256 `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`. Its persistent logical rows are 112 X, 112 Y and 408 independent helpers H. The original normalized endpoint is `(X,Y,H) -> (X,Y+X,H)`. Physical entrance and exit charts remain exactly those of the frozen source.

There is a completely emitted constant dyadic pre-compensation, followed by the source word with every center Gaussian operation replaced by an owned CLEAR, whose exact normalized endpoint is

`X' = X;    Y' = Y + A X;    H' = H`.

All 632 persistent inputs are arbitrary and independent; no helper is initialized, discarded, identified or counted twice. The literal backward construction has exact normalized endpoint

`X' = X - A^T Y;    Y' = Y;    H' = H`,

the raw inverse transpose of the forward endpoint. The paid profile in both directions is

`{1:2201, 2:412, 3:510, 4:127, 5:40}`.

The helper profile stays `{4:28,7:7,8:47,9:326}`. Relative to the source, exactly eight rank-eight children are removed and no Gaussian child is added. The pre-compensation adds 6,596 scalar ADDs with a retained scalar allowance of 32,652 primitives; all numerator magnitudes and denominators are at most 4. These finite scalar operations do not establish a better recursive exponent on their own.

## Constructive proof

Delete all eight center calls by replacing each with CLEAR of the owned center field in the call's destination chart. Zero has every chart, so this is a valid erasure of owned scratch, not a borrowed input overwrite. Retain every other physical instruction and every endpoint chart.

The exact sparse replay over the rational free group algebra on the 72 native symbols gives

`M_0 = I + S + E_X + E_H`.

Here S is the original transfer X to Y. Both error blocks land only in Y. E_X reads X; E_H reads only 106 particular helpers, each with a ground entrance and full-frame exit. Every helper and every X output remains autonomous. All error terms have EMPTY native word: the errors are ordinary constant dyadic matrices, not uncomputed address-operator oracles. The 12,532 nonzero entries split into 5,936 in E_X and 6,596 in E_H.

Every pairwise product of S, E_X and E_H is zero, because all three maps land in Y and none reads Y. Before executing the center-cleared word, apply `I-E_H`. Every required source and target is in the actual ground chart: the targets are Y and the sources are those 106 ground-ended helpers. The operation is the explicit list of 6,596 dyadic ADDs.

Consequently

`M_0 (I-E_H) = I+S+E_X`.

Thus `A=I+E_X` on the 112 main port indices gives the claimed offer, with no helper contamination. Scalar operations in one common address chart have their exact owner-space action, so this is a physical fixed-template pre-compensation and not an abstract change of logical coordinates.

For the backward direction, the separately emitted center-cleared source word is verified to equal `I-S^T-E_X^T-E_H^T`, with the source's distinct inverse-transpose native letters. Prepend `I+E_H^T`, again using only actual ground-chart fields. The product is `I-S^T-E_X^T`. The verifier compares all 632 independent rows in both orientations. The owned center field is empty at termination.

## Explicit code, inverse and conditioning

The same exact entries satisfy

`E_X^T = E_X,    E_X^2 = -14 E_X,    tr(E_X) = -112`.

Set `P=-E_X/14`. It is a real symmetric idempotent of trace 8, hence an orthogonal projection of rank 8. Therefore

`A=I-14P`,

with eigenvalue -13 on the eight-dimensional image of P and eigenvalue +1 on its 104-dimensional kernel. In particular

`A^-1 = I + E_X/13`,

and its Euclidean condition number is exactly 13. The complete main shear is I+N_A with N_A^2=0 and ||N_A||_2=13; both it and its inverse have norm at most 14, so its condition number is at most 196. Helpers are an independent identity block, and the physical boundary charts are unitary, so this same bound applies to the complete physical coded offer. Its inverse uses I-N_A and needs no 1/13 arithmetic; 1/13 appears only when separately inverting the main code A. Every diagonal entry of A is zero; its 5,824 nonzero off-diagonal entries are ±1/2. The exact checker verifies the degree-two polynomial entry by entry over rational arithmetic, so the spectrum and inverse are universal consequences of that identity rather than numerical eigenvalue observations.

The coefficient 1/13 is part of the mathematical inverse formula. This deliverable does not call it a free dyadic SCALE, assume a division oracle, or insert A^-1 across different physical address charts without paying for the resulting adapters.

## Arbitrary fiber widths

The replay identities hold over Q[FreeGroup72]. Every consistently shared invertible assignment of the 72 native operators defines an evaluation homomorphism. Hence the logical word identity holds at every positive column multiplicity under the retained source native implementation. It does not rely on one-column matrix testing, erasure of central phases or tensor powers preserving sums.

Every physical frame, native monomial and Gaussian child is retained from the authenticated source, except the eight deleted owned-center calls. The new instructions are only constant dyadic scalar operations at an explicitly common ground chart. No fresh nonmonomial address implementation is introduced.

The exact observed maximum prefix coefficient ℓ1 norms are 457 forward and 258 backward, checked on the fixed free-symbol words. Unitary evaluation bounds intermediate exact states and perturbations at the initial input in the maximum-over-fields Euclidean fiber norm by fixed constants independent of fiber width. For discrepancies inserted at later sites, use a separate suffix bound: assign each scalar ADD or SCALE of coefficient c the bound 1+|c|, and every unitary Gaussian/monomial, owned CLEAR or owned COPY the bound 1. The product of these elementary bounds over the finite word bounds every suffix. Thus the sum of local error magnitudes times this fixed product bounds propagated rounding error; no prefix norm is substituted for a suffix norm. Entrywise infinity-norm statements require the appropriate square-root fiber-volume conversion. There is no precision-dependent epsilon and no recursive border-precision claim.

## Integration boundary

The old source wrapper's port-dependent entrance lines and exit hyperplanes remain. A is a constant matrix in the stated normalized logical coordinates. It must not be silently treated as a constant free recoding in every physical main chart or in a different standardized central-Q ABI. Its nonzero off-diagonal entries connect distinct entrance-line charts. A useful next step is an actual coded caller or a paid simultaneous adapter that exploits the eight-mode structure, together with complete moment, raw-dual, compiler, finite precision and outer recovery budgets. This document supplies the exact producer and its bill, not those missing consumers.

## Predecessor overlap and credit

Cinna Davis's PR #4694, head `2add42d1edf14a263abe90a3bcde67fc1ba30768`, already emits a center-free kernel with paid profile minus eight rank-eight calls, records its coupled cache ABI, constructs its raw dual, and proves that its 106 observed helpers start at the empty chart. The source CACHE.md was read directly. None of center deletion, the cold-helper observation or the abstract block Schur elimination is claimed here as new. PR #4698, scientific head `9079ab66ba9a1717df478a08eb957c20d84d3e61`, already emits a dyadic helper basis of 379 gates in each direction reducing observations to eight helpers, and a conditional consumer. The present deliberately dense 6,596-ADD pre-compensation is easier to audit, not a claim to a better basis count. Its changed sufficient result is the actual fixed-template helper-independent coded offer, explicit A entries, exact eight-mode spectrum/inverse/conditioning, and unchanged independent helper ABI.


Cao Yifan / intqwq supplies the joint-helper/native-map round-three word at canonical `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, commit `624de9dc66858af0945e5f8a0942488d62280d43`. Its predecessor and refreshed public lineage includes PR #4610; the exact source package and bytes, rather than an older PR headline, bind this result. Cinna Davis, the PR #4470 native/helper/controller lineage, Dugongue's exact native and complementary-provider work, DaysSky, Nick Petalas, Ryanson Jonathan, Jacob Alan Sussman, zxv and the retained scalar, Clifford, precision, compiler and outer contributors retain predecessor credit. The common-chart pre-compensation and exact eight-mode code are the present construction. Local MathProof's Schur block elimination and low-rank composition notes motivated the representation; their source-only inspection is not a fresh Lean/kernel audit or a claim of priority for elementary projection algebra.
