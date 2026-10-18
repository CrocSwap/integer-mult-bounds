# Borrowed same-family inactive spectators

## Sufficient local identity

Let a complete normalized dirty-helper invocation have exact helper endpoint C_A tensor I_Z tensor I_rest, where A is an orthonormal active-eight block and Z is a one-dimensional orthogonal spectator, all in one actual owner array. The exact E510 construction provides such an endpoint by wrapping its complete nine-axis invocation. No clean value of Z is assumed and no independent helper array is synthesized from it.

Let S be a pending idle child's orthogonal coordinate set. It suffices that A is a subset of S. Z may lie OUTSIDE S. The two-sided wrappers act on A+Z during the invocation, but their complete endpoint is identity on Z. If the owner family is untouched by data gates during the entire invocation and between that invocation and the pending child, the invocation contributes C_A on that family. Replacing the pending child by C_(S minus A) gives

    C_(S minus A) * (C_A tensor I_Z tensor I_rest) = C_S.

This is equality of operators on the SAME array family, on arbitrary inputs. No residual is split between families and no9-dimensional function space is represented as an eight-dimensional one. Both monomial wrappers retain the full physical nine-axis footprint and their complete primitive costs.

The proof is the exact E510 normalization followed by the inherited same-family coordinate-factor product. For a nonstandard orthonormal idle basis, map the eight standard active coordinates to the chosen eight axes and the ninth to an explicit orthogonal complement axis. Extend the map to an orthonormal basis of the ambient coordinate space. The address permutation/isometry used by the cover routing must be explicit and charged under the existing interface.

For an ambient m=89 array and a rank r<=88 coordinate child, such a spectator is available among the listed orthogonal complement axes. This is a constructive statement only when that complete orthonormal basis is actually supplied or reconstructed; rank counts alone do not certify the route.

## Multiple invocations and real storage

The active blocks assigned to one replaced idle child must be pairwise disjoint. Their union is the only set removed from the paid remainder. The inactive spectator axes are not removed from any child solely because they were borrowed.

Different sequential complete invocations may use the SAME spectator axis. Each entire invocation has identity endpoint on that axis, so it can be reused without cleaning or restoring an unknown value by an extra oracle. Spectator axes may also coincide with another invocation's active axes, provided the factorized endpoint and chronological idle window are preserved. Multiplying complete endpoint identities justifies this; commuting individual interior wrapper gates would not.

Within ONE invocation, every logical helper must still have a distinct physical owner including its cover-class route. A sufficient conservative check is disjoint full nine-axis footprints for helpers in the same owner family in that invocation; more permissive overlap requires an explicit injective cover-class map. Neither a shared spectator nor disjoint active axes alone is a proof of physical register injectivity. Source and target owners must remain disjoint from all helpers.

The family must be inactive in the local data invocation. The complete local scalar matrix has zero helper/data cross-blocks and identity helper block, which makes the wrapper argument valid for arbitrary dirty and correlated contents. The actual helper entrance adapter must NOT insert an extra T_E: the virtual starting frame merely defines logical coordinates. Explicit helper old_to_new markers should therefore be absent from the new emitted physical stream; data adapters are retained.

## Improvement gate and distinction

A rank-eight pending child cannot contain a full nine-axis footprint internally, but can host C8 using an exterior borrowed spectator. Relative to the conservative E510 admission, this can avoid extending a paid rank-7 remainder to rank-8. This is a distinct storage admission theorem, not a new response relation or a new scalar kernel. Its numerical benefit still requires a concrete injective owner assignment, legal windows and a reconstructed paid profile. The existing frozen E510 witness must remain unchanged until such a positive candidate passes.

No numerical gain is claimed in this note. It supplies a sufficient implementable operator mechanism, with exact physical checks listed above rather than an assumed new algebraic gadget.

## Concrete positive pairing on the frozen E510 witness

A read-only exact scan of E510-HOSTING.json.gz found 56 active-eight helpers at stage0 and 56 at stage1 assigned to idlechild0, and 56 each at stages9/10 assigned to idlechild11. Each participating owner copy currently contains exactly one helper. The first-stage and second-stage owner-copy sets are disjoint. Both idlechildren have rank-16.

For each idlechild, sort the 56 first-stage and 56 second-stage slots by owner-copy index and pair them. Keep the first helper's owner family; map its activeblock onto pending coordinates0..7. Move the second helper to that SAME owner family, mapping its activeblock onto pending coordinates8..15. Give each its full ninth coordinate from the owner's orthogonal complement outside this rank-16 child. Use the same external spectator for the two sequential calls if desired.

The old destination and source children had paid rank-8 complements. The new destination has paid rank0 and the now-empty source has paid rank-16. Thus the exact profile change for 112 pairs is

    delta profile = {8:-224, 16:+112}.
    delta rank mass = -224*8 +112*16 =0.

For every alpha in (0,1), 16^alpha <2*8^alpha. Hence this modification STRICTLY decreases the paid moment at every relevant exponent. This is an exact early improvement gate, independent of floating-point estimates.

Within each call, the new owner is unused by other helpers of that call: the original frozen construction used it only in the paired OTHER stage. Therefore this reassignment introduces no same-call register alias. The moved helper stays in the same admitted idle window. Its original owner becomes unused. The two activeblocks are disjoint; only the cancelled spectator is shared across sequential calls.

The resulting intended profile is {1:149176,2:60704,3:15960,4:17248,5:33544,7:3136,8:8568,16:112,64:1520}. The actual nine-axis coordinate permutations, changed owner table, paid-complement replay and full invoice must still be emitted and checked. This note does not assign a final kappa before those checks.

Source-motivation boundary: `Mathproof/Meta/Problem18ActualPrimaryBlock20261001.lean`, theorem `actual_primary_projector` (line20), explicitly splits an operator into its action on a primary block and its complementary kernel. Source SHA256 fc8f60dbad9855de8e6e1f3f12811824e5d632c899276c89ef8f253b820d6c0f. This was inspected as a structural analogue; that Lean theorem is not a borrowed-ancilla or Fourier-cost theorem. The same-family spectator identity above is proved directly. This document claims a new sufficient route within this project, not worldwide priority over all circuit-synthesis literature.


## Delivered kernel79 construction

The delivered construction uses all 79 rank-one response-kernel entrances in each of 77 complete local calls. Each canonical entrance frame has its own source-bound exact full-nine-axis normalization. The theorem above applies separately to each; no common choice of entrance line is assumed. The E510 pairing example is an independently positive ablation, not the final packing. The final physical witness contains 6083 active-eight occurrences and 37037 active-nine occurrences, with 43,120 whole-helper footprints. Its active-coordinate partition and complete orthogonal route matrices are independently reconstructed by `code/independent_routes.py`. Exact prices and the final bit/complex assembly are reported separately by the package.
