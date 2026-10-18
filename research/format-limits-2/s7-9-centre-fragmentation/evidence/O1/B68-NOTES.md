# B68 NOTES: alternative block partition for X faces. VERDICT: KILL at gate, PROVEN (scope below). ship=false

## Gate 1: where the partition comes from
- Source is the E8 line geometry, not a free choice. Hamming/Construction A form: 112 non-centre lines = 14 extended-Hamming octads x 8 sign patterns (mod +-); 8 centres = +-2e_i.
  Blocks c = lines supported on octad c (research/punctured112-global/vendor/pr514/code/construct_partial.py: `blocks`, `tetrads`, `block_totals[c,i]`, centre frames hyper(P[frame[i]])).
- Given the 8-centre frame (the 8 coordinate ports deleted by build_port112.py, indices 0,13,22,35,40,51,54,119), the partition is UNIQUE: a block is the D4 spanned by 4 centres minus those centres; only octad 4-subsets of the frame span 8 further lines. Other frames (135) are W(E8)-equivalent, so the count is unchanged. Conclusion: construction-fixed (frame + Hamming code), not a SPEC clause.
## Gate 2: counts (faces.c, sa.c; single process <1 s / <100 s)
- Rebuilt: line0 has 59 orthogonal / 52 adjacent lines. Eff-reach census (own-block readers excluded, sign-consistent) reproduces J21-K: eff10 = 2688 faces (all 4 blocks), eff9 = 2688 (2 blocks) + 17920 (4 blocks), eff8 includes the 168 block-local planes.
- Raw reach >= 10 (block-independent): 24192 faces; canonical partition: 24192/24192 span 4 blocks.
- UNCONSTRAINED SA over all 14x8 partitions of the 112 lines (swap moves, 3e6 iters, not required to be legal): best 20681 of 24192 faces still span >= 3 blocks (8739 span 3, 11942 span 4). Needs < 50 to pass; it is ~400x off. The reach-9 SA run did not move (temperature schedule too cold for those deltas), so reach-9 is only the canonical census: 21504 span 3, 67200 span 4 (raw).
## Verdict
KILL. PROVEN scope: 14x8 partitions of the 112 lines; faces = 4-sets with raw reach >= 10; SA is a heuristic upper bound on the best partition (not an exhaustive proof), but the legal class is a single partition and the unconstrained one is nowhere near the 50 bar. High-reach faces are spread over the whole line graph (about 864 per line), so no 8-set blocking can contain them.
## Escapes (>= 3)
1. Not a partition: faces whose sources need no block frame because totals come from another supply (B7 escape 1, <= 10 helpers; B10 centre supply dead).
2. Blocks of other sizes/overlapping cover (non-partition cell graph, 6-quad family; B64 escape) - changes the skeleton, the #646 lineage.
3. Different centre set per phase (cut-timing / donor retiming) so the 56 retired-row totals disappear.
4. Reach-9 two-block faces (2688, nb2) as a hybrid tile class: B7 prices hybrids at -0.10% b per block, so not a lever alone.
## Rescue check
Rerun SA with a hotter schedule on reach>=9 and with an exact (CP-SAT) cut on the reach-10 hypergraph; expected still hundreds. Not run (gate is two orders of magnitude off).
Files: cards/B68/faces.c, sa.c
