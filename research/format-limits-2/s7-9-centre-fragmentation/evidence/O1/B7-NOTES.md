# B7 notes (Oct 12). VERDICT: KILL at fast gate. PROVEN (scope below) for ledger-priced tile covers; no heavy job, nothing built. ship=false

## (a) Charge anatomy of X4 (J21-K K.2/K.3, recomputed)
X4 raw +7.68% b, charged -4.53%, so charges = 12.21% b:
- S-type: 14 blocks x 0.3% = 4.2% (0 aligned blocks, X-tiles are cross-block and lose the rank-4 groups/gauges).
- Totals + cut timing: 56 retired-row helpers x 0.143 = 8.01% (X faces have 4 sources in 4 blocks, so their strands lie in no block frame; retired rows no longer supply the totals). Cut timing is the same cause; it is not a separate charge.
- 4.2 + 8.01 = 12.21, matches.
Shape dependence: both are "cross-block face" charges. Only the 168 block-local planes (eff reach 8) avoid them, and a plane-only ledger is 504. Any ledger < 504 needs faces of eff reach 9/10, which are non-block-local. A subset tile keeps the same faces, so the charges do not shrink. They are per converted block (0.3 + 4 totals rows x 0.143 = 0.87% b), linear, and all-or-nothing per block.
## (b) Best-case bound over ALL subset / partial-use covers
Model: ledger B = N2 + K + R - 112, R = 280, face reach <= 10, key reach <= 6 (J21-K inventory), 5376 cross-block cells, face slots 2*(5376/8) = 1344.
- Full-use face: 10 reader slots, > 6, so it needs >= 2 tiles; hence K >= N2 and N2 >= 134.4. Partial use costs more per slot (0.25 vs 0.2 objects/slot). Floor N2 + K >= 268.8, so B >= 436.8.
- Subset tiles revive this floor on paper: 4-subsets of a (10,10) 6-common pair give the (10,10,4) pairs that J21-K entry 7 said did not exist. That is the 437 ideal.
- Priced with J16-H classes (0.143 / 0.1095 / 0.0755): X4 (144,144) = +7.68 (reproduced). Absolute floor (134.4,134.4) = +10.75% b raw.
- Charges at full conversion = 12.21%, so net <= -1.46% b (uncapped best case, cover assumed to exist). Hybrid per converted block: gain <= 10.75/14 = 0.77 vs charge 0.87, so -0.10% b per block, never positive.
- Break-even needs B <= ~453; +1% needs ~447. The card's "LB <= 470" threshold is far too weak: 470 gives raw ~5.4% vs 12.2% of charges.
## (c) Decision: KILL (best-case net < +1%, in fact < 0). The cover question (wall a) is moot. Capped = uncapped = no gain.
PROVEN scope: ledger model of J21-K (calibrated on #531), reach <= 10 / <= 6, binary 2/4/8 ladder, coordinator charges as booked, R = 280. Not shown: the charges themselves (they are booked, not derived here).
## Escapes (>= 3)
1. Charge side (the one that matters): a totals supply for cross-block faces costing <= ~10 helpers instead of 56. This is J21-K E2, not a tile lever. If totals were free, the ideal net would be 10.75 - 4.2 = +6.5%, but it would also need a subset-tile cover with LB ~437 to exist.
2. S-type recovery (rank-4 groups in X blocks): 4.2% of the charge. Paired with escape 1 it would be a different card.
3. Non-binary / 12-24-source / odd-arity ladders (J21-K A5/E3). They change the face/key reach caps, so the floor of 436.8 moves.
4. Read side R < 280 (E4). It lowers every row, so it is not a tile lever.
## Rescue check (not run)
Show the totals charge is not generic to cross-block faces: e.g. price a cut-timing scheme where X-face strands get totals from existing helpers at <= 10 extra rows. If that holds, add subset tiles to library C (6-tile 4-/5-subsets), relax face usage, and run x4exact (CP-SAT) for a cover with N2 + K <= 290. Without it, escape 1 is only an assumption.
