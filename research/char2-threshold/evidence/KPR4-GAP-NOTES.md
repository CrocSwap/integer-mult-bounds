# KPR4-GAP notes (partial; stopped early for report)
Tools: kgap.c (T blocks; `ex` exhaustive Gray code, `sa` annealing; validated at T=3: cex_joint_v7 12/4 minimisers, cex_wholeTS_v9 18/16, tied_min 12 via SA),
ksubset.c (SA over subsets of a pool maximising |S|-Cfull), mclique.c (odd-or-zero cliques), realize.py (real LM realisability of F2 incidence structures), kg.py, units.py, pools.py.
Note: minQ >= v (Lemma B), so a certified gap <=> minF2 < v; no exact-Groebner Q side was needed (nothing below v found at T<=6).

| unit / family | T | v | best F2 cost found | note |
|---|---|---|---|---|
| D4,D5,D6 (std coords) | 4,5,6 | 12,20,30 | 12,20,30 | ties (cost = v) |
| F4 (24 rays) | 4 | 24 | 24 | tie, 150 bases |
| E6 | 6 | 36 | 36 | tie (best basis; other bases 40-42) |
| A4,A5,A6 | 4,5,6 | 10,15,21 | 16,21,34 | above v |
| E7 (any basis) | 7 | 63 | 49 | GAP 14 (SA on roots finds gain 14 from scratch; subsets of 57-60 roots also gain 14) |
| Fano Levi (7 pts, 7 planes, random Q realisation) | 4 / 5 | 7 | 11 / 8 | realises trivially at T=4 but cost>v |

Structural picture (mod-2 labels): "odd-or-zero" systems realise F2 geometry exactly; B=J+ab^T has F2 rank k+1, dense cost <= T(k+1). Roots give v = 12,20,36,63,120 for T=4..8 versus T^2 = 16,25,36,49,64: tie at E6 (T=6), first strict win at T=7. Max odd-or-zero cliques in tested lattice pools (E6,D5,D6,A6, Z^T) equal the root counts; random symmetric/nonsymmetric forms T=4 give cliques up to 16 but gain <= 0.
Real realisability (LM, residual 1e-24 = yes): Sp4 doily (15 pts) T=4 yes, T=3 no; Sp6 (63 pts) T=7 yes, T=6 residual 10-21 (no), T=5 no. E6's 36 nonsingular points + up to 5 singular points of Sp6 realise at T=6 (41 pts, F2 rank 7: 41 < 42, no gain); greedy beyond that fails.
Negative searches (all gain <= 0): ksubset SA on pools T=4,5 (H = I,A,D,E, random), E6/D5/A5/D6 lattice pools norm<=4, ksearch outer SA T=3,4 (only ties).
Attempted E7 -> T=6 projection (drop minuscule node): fails because the 27 weight lines would need W-W orth pairs of E7 to vanish in M'.
Not done: exact Groebner Q-side, stretch (real-unit pricing), minimal T=7 seed characterisation, Fano gadget growth beyond v=7.
