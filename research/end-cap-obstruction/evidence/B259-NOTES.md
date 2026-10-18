# B259 VERDICT: LOCAL-PRICE NO-GO. Dimension room exists on paper (dim ∩u⊥ = 7 pair / 6 triple / 5 quad), but a second encoding must re-frame ~100 mass for one copy deletion (credit ≈ 0.08-0.13%); puncture pairs one coord-pair of a reader triple at most. Nothing built, nothing pushed, no heavy jobs. (Local-price: op-excess is a first-order proxy, not an exact kappa.)
Tools here: an1..an6.py (single process, seconds), on B232/word1018 ports + B253/out/{g_base,g_cf0,g_all16} words.
## (1) dim(∩ u_t^⊥), 112 ports, 14 blocks of 8 (t//8; each block's ports span rank 4)
- Ports are distinct, odd weight. Cross-block pairs (5824): dim 7 always. Triples across 3 blocks (186368): dim 6 always. Quads across 4 blocks (4.1M): dim 5 (4,080,384) or 6 (19,712).
- Union of whole blocks: 2 blocks rank 6 (dim 3), 3 blocks rank 7, 4 blocks rank 8 (924) or 7 (77). So the algebra leaves room; the cap is the frame, not the dimension count.
- Real reader sets (base word, regs read directly by y of >= 2 blocks): 136 regs, 104 with dim I=7, 32 with dim 6. Their FINAL frame exceeds ∩perp by 1 (80), 2 (56): 0/136 fit already.
## (2) Second encoding price (needs every op frame on the shared reg inside I_T and the cascade)
- Op-excess = sum over ops on s of dim F - dim(F∩I_T). Over the 136 multi-block regs: min 1 (32 regs), median 3, max 13; 0 regs with 0 excess. Excess-1 regs are only the 2-block, dim-7 ones.
- The actual deletion (g_cf0, CF=0): packet 283 (readers y12,y37,y59, blocks 1,4,7, dim I=6) op-excess 22; neighbours 1:14, 315:14, 379:16, 171:8, 174:8, 591:4, 598:3, 299:5, others 1-2. Sum ≈ 105 mass for ONE copy (4 y violators). All-16 case: 230-290 mass per 4-y group.
- Rate: helper w9 = +0.15% (0.017%/mass); 1 unit x72 calls = -2.82% (0.039%/72-call mass). So 105 mass ≈ 1.8-4%. Credit per deleted copy = 1.3-2.0%/16 = 0.08-0.13% (B258 break-even 0.044%/copy at all-80). Ratio ≈ 15-50x against us.
- Cheapest legal "second encoding" is the existing one: keep a copy for the late readers (cost ≈ the helper, net ≈ 0). No encoding cheaper than the copy found; the copy is already the minimal-rank second encoding.
## (3) Puncture (merge two of the 9 source lines)
- Merging coords i,j makes ports differing by e_i+e_j coincide: cross-block weight-2 pairs 776 (32 classes, <=28 pairs each; 4 in-block 100). Such a pair gets dim I=8 (= single cap).
- But reader sets are triples (e.g. 12/37/59: pair weights 4,4,2; 59/68/109: 2,4,4; 0/41/62: 4,4,6): one merge fixes at most one pair, triple stays dim 7 vs final frame 9. Also changes h 9->8 (new family; ports collide, Lemma R / distinctness untested). Not priced beyond that: LOCAL.
## Priced bound
Second-encoding sharing for a hub copy costs ≳ 1.8% vs credit ≤ 0.13%/copy; even excess-1 two-block regs (32/136) cost 0.02-0.04% each but are already shared and are not copy candidates (B255: 16 legal-by-value, all killed by B253).
## Escapes (>=3)
1. Reader-set aware decoder: choose u_t so a hub's readers are collinear/low-rank (pairs weight 2 only 776/5824; needs 3-4 reader sets on weight-2 chains) - changes u_t, outside Lemma R scope.
2. Reorder so shared regs' large-frame ops (dim 7-9, late B ops 927-930) move after all reads (B256/B257 drag reordering).
3. Version reconstruction instead of a register (B256), no ∩ constraint on a fresh frame.
4. Puncture/h=8 family redesign with asymmetric pairing (C.6 says none at window<=9).
