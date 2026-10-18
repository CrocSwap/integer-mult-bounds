# Local sprint claim

- Track and seed: Bit supplier, OS seed 10 (`/dev/urandom`).
- Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Object: PR #1351's selected PR589 physical family `(pair=1, copy=0)`, children 0 and 7.
- Method: independently certify the q-perp and coordinate projectors, prove pairwise orthogonality and exact sums, then apply the block identity for D(P). This is distinct from PR #1351's 128-column replay; the audit is conditional on its pinned role map.
- Deliverable: exact rational verifier, source pins, interval certificate, and omitted-helper/wrong-axis/duplicate controls. No new kappa or supplier admission claim.
- Expected finish: 2026-10-14 00:00 UTC.
- Coordination: no pinned sprint coordination issue found, so this claim is recorded locally.

Overlap checked against PR #1345 (fixed-word gate-order transports), #1334
(revision-3 bit levers at a=1/99), #1351 (one-family matrix realization),
#1333 (binary-affine register model), and #1307 (all-family geometric census).
This is an explicitly different-method independent audit of #1351, allowed by
the sprint instruction. The PR #1351 source pin is head
`6060e62e9d42a16eff493aba74c8a617a12d8041`.

## Result and handoff

The rational verifier proves both pinned interval decompositions and rejects
all three mutated controls. It prints
`PASS_BIT_FAMILY_PROJECTOR_ALGEBRA children=0,7 factors=2+4 q_rank=7 controls=3 no_new_kappa`.
One focused pull request is open: [#1371](https://github.com/CrocSwap/integer-mult-bounds/pull/1371).
