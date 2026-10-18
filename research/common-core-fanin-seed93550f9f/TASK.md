# Cycle I task card

- Track: `recursive-interfaces`.
- Seed: `93550f9f7a77e57c8be488f86df218cc` (OS random; accepted eligible draw).
- Task ID: `connector-alphabet-change`; scope refined to a common-core, low-rank-correction fan-in.
- Catalogue priority revision: 3; catalogue SHA-256: `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`.
- Drawn scope key: `0c9f43f3c7d61edb36fe`.
- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected-result SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Authoritative selected conditional exponent: `836330098538459/500000000000000000` (`0.001672660197076918`).

## Object and question

For three arbitrary dirty sources `x1,x2,x3`, an arbitrary dirty target `z`, and an arbitrary dirty scratch row `t`, can the simultaneous operation

    z += B1*x1 + B2*x2 + B3*x3

be implemented more cheaply when `B_j = B + D_j`, the shared core `B` has rank 48, and each `D_j` has rank one, than three separate rank-49 map calls?

The bounded instance has 49 coordinates, `B = diag(I_48, 0)`, and `D_j = e_49 v_j^T` for three distinct rows `v_j` whose last entry is 1. Thus each `B_j` has rank 49. The exact F2-linear map is also checked over integer-valued rows. All five rows may start dirty.

## Changed premise and method

The ordinary DUO/TRIO operations charge each distinct source map in full. This scope permits one shared rank-48 core plus three rank-one source-specific deviations. The proposed implementation subtracts `B*t` for the arbitrary dirty starting value, gathers the three sources into `t`, adds `B*t`, and then restores the scratch with six charged rank-one additions. It applies each `D_j` once and does not assume a clean vector or discard any source. The rank-48 tariff charges both core orientations at the larger complete-call cost.

## Nearest overlap and distinction

- PR #1531, head `892b28a3358b16c9083036f71e1ef505ccf5d20a`: arbitrary-map DUO, fully charges both source-map traversals.
- PR #1518, head `0c6a58aaf22e0fc1b34497f8f6f80db6212b4621`: atomic TRIO, charges every source map.
- PR #1524, head `5c1f39788a0fc669b7e37e27785c63e85788c350`, and Discussion #1579: common-B tariff where source maps are identical; this task permits distinct rank-one deviations.
- PR #1739, head `e33645b34521460bce61f9fb913f98f506d34d4d`: a rank-one map transition between consecutive calls after a source update; this task combines three maps simultaneously.
- Recent claims on Discussion #1163 cover C5 restoration and a heterogeneous two-type boundary, not this shared-core fan-in.

The initial overlap scan used complete PR pagination and a complete 478-record Discussion snapshot from 11:37 UTC; its Discussion refresh had a GitHub GraphQL transport warning. Before handoff, the live PR list was filtered through REST for common-core, simultaneous-source, low-rank, and rank-one-deviation wording; only unrelated PR #148 matched. Discussion #1163 was fetched through REST through 12:07 UTC, and the common-B claim in #1579 plus the connector thread #1504 were rechecked. No exact shared-core/rank-one simultaneous-source claim appeared. A later full `find_overlap --refresh` fetched PRs but its global Discussion scan hung in the GraphQL client for 90 seconds, so the final global Discussion snapshot remains the complete 11:37 UTC cache plus these direct thread checks.

## Optimistic complete-cost screen

Write `q = 1 - a`, with `a` the selected exponent. The direct plan pays three rank-49 calls plus one unit of root dispatch per call: `3*49^q + 3`.

The factored plan pays two rank-48 core calls, three rank-one deviations, six rank-one source gather/restore operations, and one dispatch unit for each of its eleven calls: `2*48^q + 9 + 11`.

The optimistic saving before any additional interface overhead is therefore

    3*49^q - 2*48^q - 17.

The selected exponent satisfies `a < 1/100`; the exact integer inequality `49^99 > 47^100` gives `49^q > 47`, while `q < 1` gives `48^q < 48`. The saving is consequently greater than 28 rank-one-equivalent units. All additional root program, scratch hosting, and integer-lift precision cost must be charged inside this remaining 28-unit budget. The implementation requires one 49-coordinate dirty row; the integer lift needs at most two extra guard bits for summing three source rows. If these costs cannot be placed within the budget and the supplier's available row stock, the construction does not transfer to the selected bound.

No frame changes or source/target copies are omitted. The six scratch toggles and all three deviations are included above; scratch restoration is exact. The screen is local to this rank-class interface and does not claim supplier realization, a new paid profile, or a new `kappa`.

## Domain, stop rule, deliverable

- Domain: exactly three source maps, one rank-48 shared core, three rank-one deviations, 49 coordinates, arbitrary dirty sources/target/scratch.
- Method: explicit factorized construction plus exact matrix/rank replay; no unbounded search.
- Stop: retain the construction only if the dirty-state identity, map ranks, negative controls, and the strict cost inequality all pass. Do not expand to more sources or other ranks in this cycle.
- Expected artifact: this task card, exact verifier, literal maps and cost certificate, reproducible from the repository root. Local result only unless the physical row/precision overhead can be matched to a live supplier interface.
- Predecessors retain attribution. This work uses no predecessor implementation code. Prepared with substantial OpenAI Codex assistance.

## Handoff

- Focused PR: https://github.com/CrocSwap/integer-mult-bounds/pull/1863, head `53e716e640d998c81886aed7bae3c71e20985c36`.
- Original claim updated with the result: https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18923560.
- PR was open and mergeable at handoff; all 61 checks were queued at the latest poll.
- Remaining obligations: map the construction to a concrete selected-supplier seam and charge the dirty-row, guard-bit, and remaining interface costs. No selected-profile or `kappa` change is claimed.
