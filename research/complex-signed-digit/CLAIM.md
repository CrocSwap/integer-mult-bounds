# Sprint claim

- Track: complex supplier. OS assignment seed: **36**, drawn with
  `secrets.randbelow(100)` on 2026-10-13.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Selected result: #626 with #543, conditional
  `kappa = 51110230636731/31250000000000000`.
- Object: signed-digit preparation of non-unit dyadic additions in the selected
  JP8 emitted scalar programs. Seed 36 selects JP8, index `36 % 2` in the ordered
  candidate list `[jp8, ck]`; both orientations of that provider are in scope.
- Method: exact non-adjacent signed digits, explicit source copies, doublings,
  signed source accumulation, halvings, target accumulation and scratch clear.
  Compare complete cost and actual intermediate coefficients with the pinned
  binary-Horner invoice. Accept only strictly cheaper numerator circuits.
- Deliverable: bounded finite circuit improvement or scoped negative result,
  executable exact checker, source pins, negative controls, and a cost receipt.
- Expected finish: 2026-10-13 05:16 UTC. Final quarter reserved for verification
  and submission.

Three candidates were inspected: coordinate-total factory resynthesis, single
K-triangle read relocation, and signed-digit coefficient preparation. #681
already resynthesizes a factory; #687 exhausts a read-relocation neighborhood.
The third is chosen. #696 improves copy and unit-coefficient handling while
retaining binary Horner for non-unit numerators; this claim concerns numerator
recoding and will measure its incremental effect separately. #411 introduced
paid dyadic lowering in the earlier supplier lineage. None of these pending
PRs is an implementation dependency.

No pinned coordination issue exists. This local claim substitutes for an issue
comment. Live PR metadata was checked immediately before creating this file.
No selected certificate, source construction, global invoice, or `upstream/`
file will be changed. New kappa, full theorem formalization, and runtime
performance are outside the claim.

## Completed result

Submitted [PR #723](https://github.com/CrocSwap/integer-mult-bounds/pull/723).
The exact finite recipe saves 3,276 real-component primitives per JP8
orientation, with 250 changed additions each. Both 716-column scalar
projections and nine negative controls pass. The recomputed forward envelope
increases slightly, while the 64/101-bit local bounds remain unchanged.
The selected-record check passes. No new kappa is claimed. See EXPECTED.json
and VALIDATION.md for the exact evidence, final overlap check and limits.
