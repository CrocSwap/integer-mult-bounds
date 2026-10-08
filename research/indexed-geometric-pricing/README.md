# Coordinate-aware pricing of the indexed compiler

Conditional **κ = 52275423755251/10^18 = 5.2275423755251e-5**, with bit saving **52278156618199/10^18**. This is approximately **0.00618% above PR85** and improves PR84's construction. All inherited all-size and analytic hypotheses remain assumed.

Price each proposed frame transition in the coordinate system in which its final profile will actually be decomposed. PR84 optimized using original-coordinate oracle prices and relabeled afterwards. Here only the oracle's core/cover masks are conjugated by the final permutation during discovery; the physical compiler still works in its original labels and is relabeled once at the end. Every selected physical profile is rebuilt independently.

The h23 compiler also performs up to three bounded passes of two- or three-carrier exchanges after PR84's existing single/two exchanges. Each accepted move strictly lowers the integer proposal score and preserves cardinality, distinct future uses and independence modulo each affected output span. The third-step frontier is limited to 16 proposals; this is a search heuristic, not a proof of weighted optimality.

| Quantity | New witness |
|---|---:|
| h23 roles | 26834 |
| h25 roles | 35345 |
| Width W | 132460795 |
| Total recursive rank | 76163110225 |
| Rank deficit | 1846900 |

All eight cloud proposals passed full ordinary/dirty physical replay and fresh CRT profiles. The selected h23/h25 pair and the baseline give 25 complete pairings checked with exact moment bounds. An independent local regeneration is required and supplied by the command below. Full repository verification is pending at initial publication.

```sh
python3 research/indexed-geometric-pricing/verify.py --regenerate
python3 research/indexed-geometric-pricing/test_controls.py
make verify
```

Seven control tests include four small adversarial exchange cases, invalid permutations, inverse relabeling, omitted profile multiplicities, stale bridge/exponent, disabled assertions and a byte-level check that the portable derived engines match the independently executed discovery sources. The verifier checks actual transition profiles, both grid exclusions, independent rational bounds, all 47 inequalities/seven margins, and PR85's complete paid child list at the new saving. No inherited checks or paid corrections are removed.

Credit: Chafik Boukhalfa's PR84 construction and indexes; Thomas DiFiore's PR74 node order and coordinate relabeling; Rohan Arun's PR78 flags, PR82 coordinate-aware proposal pricing and PR85 refinement; Alejandro Zarzuelo Urdiales's PR70 exchanges; eumemic, Rohan Garg, Avi Eisenberg, Dominik Scholz, OpenAI and all prior contributors. Original archives, licenses and assistance disclosures remain unchanged. Prepared by Rohan Arun with OpenAI Codex assistance.
