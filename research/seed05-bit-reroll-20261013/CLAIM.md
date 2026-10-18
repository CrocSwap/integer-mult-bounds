# Local sprint claim

- Track and seed: Bit supplier, OS-random seed 5.
- Exact base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Selected source: merged PR589 head `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46` in the selected assembly, `v=111`, 439 helpers, decoder constant 63. The bit c does not bind selected κ.
- Object: exact third-order simultaneous transport interaction on the selected PR589 tuned word: A operation indices 927, 928 and 930, all at frame 282 with common target register 325 and distinct sources 256, 442 and 392.
- Proposed method: build the fixed PR1345 single-move frame/slot option lists from the unchanged word and enumerate the complete `7 × 6 × 5 = 210` assignments in their Cartesian product for this triple (not all jointly enabled frames or commutation-dependent options), then compare the exact full-chain price at the inherited bit c. PR1345 covers singles and same-section shared-register pairs but explicitly excludes triples in its large component. PR1382 covers A/B cross-section pairs, not triples.
- Seed diversification: after excluding triples whose legal alternatives all preserve their original frames, there are 200 eligible A triples in the large component, ordered by option product and operation indices. Seed `5 mod 200` selects index 5, `(927,928,930)`.
- Evidence-based pivot: the first triple selected from the broader set, `(9,854,1951)`, had only slot changes and held all three frames fixed, so it could not change the paid profile. The final claim tests frame-sensitive triples.
- Candidate screen: eight-total decoder reduction is covered by PR1084/PR968/PR1077; later-cut rank-seven retirement of helper 468 is actively claimed in Discussion #1362.
- Expected deliverable: source-pinned exact census for the fixed Cartesian product of three individually legal transport option lists for one shared-register triple; result may be a scoped negative, without assuming global triple-placement completeness. Any putative improvement must also survive exact word replay. No assumption that improvement exists; no new κ claim.
- Coordination: no pinned sprint coordination issue found; claim recorded locally. Refresh overlap before handoff.
- Expected finish: 2026-10-14 00:57:05 UTC.
