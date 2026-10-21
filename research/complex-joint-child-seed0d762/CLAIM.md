# Local research claim: joint rank-two child interface

- **Track / seed:** `complex-mechanisms` / `0d762194a82c097da60f154a08625527`
- **Catalogue task:** `complex-new-helper-inventory`, scope key `5868e5281a1e63d41a22`, priority revision 3
- **Catalogue SHA256:** `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`
- **Base:** `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
- **Selected record SHA256:** `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
- **Source manifest / certificate SHA256:** `79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b` / `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`
- **Pinned local word:** `research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz`; decompressed SHA256 `c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`; profile `{1:2412,2:418,3:432,4:142,5:82,8:8}`.

## Question and changed interface

Can the retained local word use one rank-two recursive child for two simultaneous rank-one frame transitions, with the two register lanes represented as a tagged direct sum? The bounded instance is the 73-dimensional selected word: pair every A/B or scheduled early-cleanup gate whose two participating registers both climb by one into the same target frame, then pair the rank-one terminal transitions in register order. This changes only the recursive child interface partition; it leaves the scalar word and native frames intact.

The changed assumption is a new joint-child contract: a rank-two call may accept a product of two register-frame quotients of dimension one each. The exact local transition must preserve both full register values and arbitrary dirt. The experiment charges zero additional source copies, helper gates, frame edits, and restoration operations as an optimistic lower-cost screen; it separately reports the unproved cost of creating/hosting the joint boundary. It will not claim a new κ unless that contract and all extra costs are admitted.

## Domain, predecessors, and overlap

The search domain is exact and finite: 3,451 A gates, 1,846 B gates, the 116 scheduled early-cleanup entries, and all 704 terminal register frames of this single pinned word. A candidate gate pair must consist of the two registers in one operation, each with codimension-one growth to the same target. Terminal pairs are restricted to rank-one endings and sorted by register id. The search stops after producing one deterministic pairing and checking its full profile.

Nearest predecessors are PR #987/#1094's selected local word and owner packing; PR #1012/#1240's coverage identity and fixed-word moment ceiling; single-register frame-coalescing work including PR #579/#583; and PR #1348's changed-coverage thresholds. The proposed mechanism groups two register lanes into one child boundary; it does not change coverage, search frame vectors, repack owners, or change the decoder. The 2026-10-14 09:10 UTC overlap refresh fetched all 435 open PRs and 396 Discussions with complete pagination and no warnings. It found one broad expired match, Discussion #1328, and no exact joint-register child match. The original claim remained local while the Discussions API was rate-limited; a handoff will be posted now that access has recovered.

## Expected evidence and expiry

Deliver a deterministic joint-boundary recipe; independently recompute every frame transition, quotient dimension, exact two-lane gate map, rank profile, rank mass, and fixed-word ceiling; include negative controls for a missing/duplicated member and a changed gate coefficient. Record the full optimistic moment/overhead ledger and keep the result scoped to a conditional mechanism. Claim expiry: **2026-10-14 09:20 UTC**.

## Current result

The exact source replay produced 574 shared-gate pairs, 16 early-cleanup pairs, and 163 terminal pairs. The ideal profile clears the fixed-word 5% screen by a guaranteed 5.241623654%, but the exact overhead budget at the threshold permits at most 11 additional rank-one children per local call. The candidate still fails `a=1/99`; no new κ is established. Exact interface admission, copies, hosting, restoration, and phase/precision transfer remain open. The initial claim stayed local during the API rate limit. The handoff is now posted at [Discussion #1765](https://github.com/CrocSwap/integer-mult-bounds/discussions/1765), linking draft [PR #1764](https://github.com/CrocSwap/integer-mult-bounds/pull/1764).
