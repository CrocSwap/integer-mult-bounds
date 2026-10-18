# Local sprint claim

- Track and seed: Complex supplier, OS seed 28 (`secrets.randbelow(60)`).
- Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Object: compose the separately optimized dyadic temporal schedules for helpers L348 and L359 on the selected PR1094/PR1263 complex word. They share ADD event 24336.
- Proposed method: seed 28 chooses index `28 mod 2 = 0` from the two zero-static helper pairs whose individual all-integer schedules both improve and are nonzero at a shared ADD. Compose those exact single-coordinate minima, then compare the complete exact invoice against the sum of separate deltas.
- Expected deliverable: source-pinned finite circuit package with exact schedules, shared-ADD correction, both complete invoices, both 712-column replays and negative controls. No joint optimum or new kappa claim.
- Expected finish: 2026-10-13 23:57 UTC.
- Coordination: no pinned sprint coordination issue found; claim recorded locally.

Candidate tasks and overlap details are in `research/seed28-complex-reroll-20261013/ASSIGNMENT.json`.

## Final result and handoff

Result completed on 2026-10-13. For the seed-selected pair L348/L359, both separate exact minima are improving and active together at ADD 24336. Their solo deltas total -403 real; the shared coefficient contributes a +3 real cross correction, leaving -400 real / 800 complex saved per orientation. The complete invoices, all-scale accounting, paid-profile check, 712-column replays and three controls are recorded in `RESULT.json` and `PROOF.md`. No joint optimum or new kappa is claimed.

The final overlap refresh found PR #1380, which addresses the same general shared-ADD mechanism but certifies a disjoint finite pair set: all 16 pairs in its certificate contain L225, and none is L348/L359. This contribution adds the distinct PR1369 zero-static pair and composes its exact one-coordinate minima; it does not claim PR #1380's joint-optimality result. PR #1376's L248/L253 schedules have disjoint ADD supports.

Submitted as [PR #1388](https://github.com/CrocSwap/integer-mult-bounds/pull/1388), an additional-pair finite certificate with no selected-result or kappa change.
