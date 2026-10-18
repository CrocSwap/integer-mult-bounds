# Sprint claim

- Track: complex supplier; OS-random assignment seed **27** (Python `secrets.randbelow(100)`). Odd seed selects JP8 rather than CK.
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Selected result: #626 with #543, conditional kappa 0.001635527380375392. Larger pending PR titles are not accepted frontiers.
- Start: 2026-10-13 05:22 UTC (October 12, 10:22 p.m. Pacific).
- Finish target: 2026-10-13 06:55 UTC (October 12, 11:55 p.m. Pacific); stop experimentation by 06:32 UTC for verification/handoff.

## Three narrow candidates

1. JP8 B-phase frame reassignment with fixed boundary frames (related to CK #698; risks duplicating an adjacent finite-domain census).
2. CK cleanup dependency-preserving source grouping followed by coefficient reuse (related to #719/#750/#769; more involved dependency and prefix proof).
3. **Chosen:** commute the selected JP8's 8,800 zero-frame compensation additions to batch same-source coefficient preparations. Targets and sources are disjoint, so this is a rectangular additive panel with no source writes. Retain the selected native circuit and price an executable local lowering, including source access, scaling, accumulation and clearing. Check both orientations and exact prefix envelopes. No kappa claim.

## Method and bounded domain

Read the pinned #626 JP8 canonical word and local programs. Validate all compensation gates, target/source disjointness and the exact location/frame of the panel. Group its entire finite domain by source and coefficient magnitude; consider a bounded dyadic coefficient route per source. Prove the commutation/substitution identities, recount both complete local programs, and provide exact scalar checks and negative controls. No search over new helpers, frames, recursive calls, owner allocations or pending record constructions.

Expected deliverable: one isolated research construction package with verifier, exact receipt, source pins, scoped proof/cost note, independent checks and attribution.

## Coordination and overlap

GitHub GraphQL reported no pinned issue; the open issue list contains only #650 (Discussions). Claim recorded locally as instructed. The live queue refresh at selection covered 591 open PRs through #772. Relevant #698, #719, #696, #722, #734, #739, #749, #750, #755 and #769 were inspected. In particular, #739/#769 reuse coefficient work while preserving update order; #755 shares consecutive same-source magnitudes in all scalar phases; #749 changes and restores the target basis. This task explicitly changes the commuting compensation order to enable cross-target batching without a target basis change. No pending code is imported and no additive saving with concurrent work is assumed.

Prepared for @Varun-Mittal-1001 with substantial OpenAI Codex assistance. New work is Apache-2.0. Delegated checks stay within this compensation-batching scope.

## Result update

Completed one finite circuit contribution, submitted as
[draft PR #793](https://github.com/CrocSwap/integer-mult-bounds/pull/793).
Implementation commit: `11926e043b0419cf1534981d89b57cb4ca1ea6b3`.
The source-grouped compensation saves **80,150 forward / 81,464 backward**
real-component primitives; complete local bounds become 177,082 / 175,816.
Exact full scalar maps, all 492 dirty-helper outputs, private clearing and
the recorded 64/101-bit prefix envelopes are preserved. No new kappa is claimed.

Full primitive replay, the separate integer/dyadic checker and the unchanged
native scalar/frame/wrapper replay pass: ten new construction controls,
twelve independent controls and 25 existing native controls reject.
Optimized execution, minimal relocation, different gzip packaging,
source bindings, selected-record verification and lint/whitespace checks pass.
See `VALIDATION.md` for scope and unrun checks.

The final pre-submission refresh covered 607 open PRs through #788 and
confirmed upstream main still equals the base. Newly arrived #786 and #787
were inspected and credited in the README/PR; their center and cleanup
mechanisms differ from this compensation reordering. No pinned issue exists.
At submission the PR is open and draft, with no completed GitHub checks
reported. No merge, frontier edit or modification of others' PRs was made.
