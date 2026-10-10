# Exact refinement of PR211's operation frames

The initial plateau step below is followed by the seeded cascade refinement described at the end of this file. The final published witness uses both steps.

The input is the frozen PR211 cascade witness at c63e50a5dde96fe1459d6b29e55e47f42f104347. The search joins adjacent operations with equal frames into connected components. A candidate replaces every frame in one component by the intersection of its next frames on both physical chains. Each accepted replacement contains the old frames and hence their value spans, is G-nondegenerate, and stays nested between every fixed boundary and neighboring operation. All scalar additions, sources, root caps, gauges, aliases, partner deliveries and terminal selections remain fixed.

Seven accepted two-operation components change operations 18516/18517, 18920/18921, 19324/19325, 23544/23545, 23591/23592, 23685/23686 and 23873/23874. Before integer moment normalization, the complete child change is:

| Rank | Count change |
|---|---:|
| 2 | +12 |
| 4 | -15 |
| 5 | -18 |
| 6 | +9 |
| 7 | +24 |
| 8 | -12 |
| 9 | -12 |
| 12 | +24 |
| 15 | -12 |

The weighted rank change is zero. The count changes scale by three for the integer moment profile. Terminal cancellation and bank removal are replayed and are unchanged. Both reflected signs and complete source/dirty restoration are checked on the actual scalar word.

The search score uses floating arithmetic only for discovery. The published saving and final κ use exact rational interval bounds with independent enclosure engines. The four finite leaf levels each invoke their predecessor and are independent of input size.

Reproduce discovery after extracting the pinned baseline (or using PR200's exact checkout):

```sh
python3 -B search/plateau_search.py --bit-package /path/to/research/paired-cube-diagonal-bit-168 --frames search/pr211-frames.json --out /tmp/plateau-reproduction
```

The search is not an optimality certificate. The following seeded cascade step contributes additional verified gain. PR211's original notice is preserved byte-for-byte in search/PR211-NOTICE. Apache-2.0; substantial OpenAI Codex assistance.

## Seeded cascade refinement

After the 14-operation plateau witness, deterministic seed 2116205 drives raise/lower proposals and short positive-temperature perturbations, followed by zero-temperature relaxation. A raise propagates joins forward; a lowering propagates intersections backward. Every changed operation retains its exact value span and a nondegenerate frame, and every edge stays nested between fixed source/gauge/root/alias endpoints. The final state is the best discovered exact-admissible state; search optimality is not claimed.

The final witness lists 6,416 bases and changes 274 actual subspaces relative to PR211 (2,124 relative to PR200). Raw frame IDs are not mathematical change counts: registering an equivalent basis can create another ID. The canonical comparison receipt is search/relaxed-diff-count.json.

Compared with the plateau profile, before the factor-three moment normalization, the further child change is {1:+12, 3:+9, 4:-24, 5:-69, 6:+9, 7:+36, 8:+39, 9:+3, 10:+9, 12:-27, 13:-18, 15:+15}. Stock and weighted rank mass are unchanged. The full verifier reconstructs this profile from the final bases and actual scalar word.

```sh
python3 -B search/relaxed_search.py --bit-package /path/to/research/paired-cube-diagonal-bit-168 --frames search/pr211-frames.json --additional-frames search/additional-frames.json --out /tmp/cascade-reproduction
```

Search traces use floating entropy only for proposals. The frozen final bases, exact frame/word replay and rational paid moments determine the public claim.
