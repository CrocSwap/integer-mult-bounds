# Coordination claim

Claim posted in the authorized mechanism-coordination thread:
[Discussion #1167, comment 18920760](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18920760).

- Track: `complex-mechanisms`; accepted seed: `95da2249593d8218c4c1e30f471d675f`.
- Card: `complex-rank-shape-decoder`, priority revision 3; refined scope `selected-gauge44-diagonal-batch/contiguous-rank1-runs`.
- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Object: size-16 diagonal block children from uninterrupted rank-one climbs on distinct output columns in the selected gauge44 provider.
- Method: source-pinned census in both orientations, exact diagonal multiplication identity, and favorable ceiling screen with all additional interface costs set to zero.
- Bounded domain: non-overlapping size-16 groups wholly contained in rank-one-only event runs; no reordering, buffering, changed word, or other rank.
- Nearest predecessor: open PR #1605 / Discussion #1596 on rank-one reblocking thresholds; this package tests cross-column diagonal batching on the exact selected chronology.
- Expiry: 2026-10-14 10:05 UTC.
- Outcome: eight groups, 128 rank-one calls; best-case ceiling gain 1.7191%, below 5%. No physical admission or κ claim.

## Result and handoff

The claim was updated with the finding and released at the same Discussion link. The source-pinned
package was submitted as [PR #1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779),
head `1e3128bf642bbaf250b7d6b9639b2bb24b98ce5e`. At the last hosted-status check (2026-10-14
14:48 UTC), the PR was open and its 61 checks were queued; local registered replay and metadata
checks passed. Physical input staging and dirty-state restoration remain unimplemented.
