# Local sprint claim

- **Track:** bit supplier.
- **OS assignment seed:** 04, sampled with Python `secrets.randbelow(60)`.
- **Base:** `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` (`origin/main`).
- **Object:** PR543's retained R420 phase-B block index 4, frame 546, baseline `B[313:371]`.
- **Method:** bounded randomized LU resynthesis of the fixed 12-by-12 F2 transfer, with the generator's 2,000-draw budgets retained elsewhere and 20,000 draws for block 4. The candidate output assignment and its downstream D6 consumers are included in the regenerated word.
- **Expected deliverable:** exact replacement circuit, complete literal cleanup and frame schedule, local/native/hosted checks, no new κ claim.
- **Three candidate tasks checked:** (1) resynthesize R420 phase-B block 4 (chosen; no matching PR); (2) improve or classify the R420 phase-A quad-4 positive-transfer floor (#1058/#1296 already cover the minimum/cleanup scope); (3) audit selected PR589 hosting and source binding (#1307/#1329 already cover those scopes).
- **Coordination:** GraphQL reports no pinned issues. The live open-PR overlap check also found R420 block work on blocks 3, 5, 7, 8, and 9. No R420 block-4 submission was found.
- **Expected finish:** 2026-10-13, 18:30 America/Chicago.

DONE — 2026-10-13 23:27 UTC. [PR #1363](https://github.com/CrocSwap/integer-mult-bounds/pull/1363) packages the 58-to-51-XOR block-4 circuit and full regenerated R420 word (26,916 to 26,902 scalar ADDs). The deterministic verifier passed all 660 symbolic columns and 9/9 negative plus 1/1 positive controls; the adapted native and hosted R420 pipeline receipts are in `VALIDATION.json`. No new κ is claimed. Upstream push was denied, so the branch and PR use the authenticated personal fork.
