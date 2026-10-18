# Seed 16 task selection

- OS-random assignment seed: `16` (0–59).
- Track: bit supplier (seed range 00–19).
- Exact base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Selection rule: list three narrow candidates in order, choose zero-based `seed mod 3`; `16 mod 3 = 1` selects candidate 2.

## Three candidates

1. **Boundary-adaptive cross-section options.** For one A and one B transport, allow the paired move to enlarge the other's frame set through the changed A→B boundary. This is a focused follow-up to PR #1345's stated boundary coupling, but requires deriving joint option feasibility.
2. **Fixed-option cross-section A/B pairs.** For every pair of independently legal A/B transports sharing a register, enumerate every pair of exact slot/frame choices and score the combined register chains. This is the selected candidate.
3. **Within-section shared-register triples.** Extend PR #1345's pair census to triples on a single section. Its review notes a 1,924-operation A component and several large B components; a full product is much larger than the priced cross-section pair class.

The seed selected candidate 2. Candidate 1 remains an explicit boundary-adaptive limitation of this result; candidate 3 is a different interaction order.

## Overlap and predecessor checks

- The current selected certificate at this base remains the conditional complex-limited frontier; this task does not modify it.
- PR #1345 was open at head `b54a856aa79857d91cd5d65f8f7144e26c8c084f`. Its exact atlas covers singles and within-section shared-register pairs and expressly says cross-section A/B transports are not enumerated. This work reuses its pinned word, moment engine and option generation, and extends the score to combined A→B chains.
- The fresh overlap scan at 2026-10-13 23:51 UTC covered 852 open PRs and 100 discussions. The narrow fixed-option query returned no possible matches; its report warns that overlap results are leads, not a novelty certificate. A prior broader query matched PR #1345, the direct predecessor described above.
- PR #1345 was rechecked at the same head immediately before submission. The latest coordination comments also showed a different-track candidate explicitly deferred because seed 16 had claimed the shared-register subset. No competing claim covers this result. Seed-16 claim: [discussion comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911411).
- PR #1344's frame-509 matrix/splice replay and PR #1351's physical-family realization concern different objects. PR #1127 searches 3→2 z-program substitutions, a separate structural move class.

## Declared limit

This contribution exhausts the product of the predecessor's per-section option lists with the other stage's boundary held at its base value during option generation. It rescored each resulting combined assignment against the full A→B chain, so any invalid resulting boundary chain would be rejected. It does not generate new slot/frame choices that become feasible only because the paired move changes that external boundary. It also does not cover triples, disjoint cross-section pairs, other gate orders or structural changes.
