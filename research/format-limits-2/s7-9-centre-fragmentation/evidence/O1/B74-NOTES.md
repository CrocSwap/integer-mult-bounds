# B74 NOTES: supply the 56 cross-block totals at <= 10 helpers. VERDICT: KILL at 20-min gate, LOCAL-PRICE [scope: face-sum model of the totals; the real X4 totals/tiles do not exist]. ship=false

## Model (the exact J21-K objects are gone: gate1.py/facepack.py missing, and X4 has NO exact cover, J21-K K.6/B6)
Total = signed sum of the 4 source strands of an eff-reach-10 cross-block face. faces.txt = all 2688 such faces (dump.c = B68 faces.c + dump; reproduces 2688, all nb=4). g.py. Ranks over Q, 112 sources.
- The 2688 face forms span all of Q^112 (rank 112). Any 56 random faces: rank 56 (20/20 trials).
## Residual rank needing new standing registers, per supply (bar: > 46 => KILL)
(a) 8 centres (B16 R.npy): rank([C|T]) - 8 = 56 (residual 56). Agrees with B10 (centre weights >= 53 vs total weight 4). KILL.
(b) block-local retired-row / cold-end basis: SPAN residual 0 (a total is a sum of 4 single-source block pieces, each in its block's invertible basis), but this rank test is vacuous: forming the sum is an ADD across 4 block frames (common frame per ADD, SPEC), i.e. exactly the cross-block problem. As STANDING forms no total equals any block-local row, so register residual = 56. Not a saving.
(c) 2-level pair sums (total = pair + pair, pairs shared, Pippenger sharing): random 56 faces need 105-112 distinct pair registers (greedy pairing, 50 trials), i.e. MORE than the 56 totals. Only an adversarially clustered choice of 56 faces (greedy, 24 distinct sources) reaches 30 pair regs; the real 56 are fixed by the (non-existent) cover, 4 per block, so clustering is not available. Residual 105+ (>46) => KILL. Pair registers also sit in 2-block frames, so legality is untested even at 30.
(d) transient totals: not a rank question; it is the frame schedule (in-place cross-frame ADD with dirty borrow). No real X4 word exists to run the B11 oracle / B15 invoice on; not run. The B7 numbers (0.143/helper) remain unpriced against B2's 0.043 (3x), so even a 56 -> 20 helper saving would be worth ~+1.5..+5% raw, before the 4.2% S-type charge and with the cover still infeasible.
## PROVEN scope: (a) centres, source-sum or strand-sum totals (same as B10); (c) random-selection pair sharing under the face-sum model. LOCAL-PRICE for (b),(d): rank cannot separate them, legality can, and that needs a real X4 word (does not exist).
## Escapes (>= 3)
1. Make X4 exist first: exact cover is infeasible in both Aut-orbit branches (J21-K K.6); totals supply is moot until a cover exists (subset tiles/partial faces, B7 esc.).
2. Totals as in-place cross-frame ADD chains with dirty borrow (d): needs a frame-lowering primitive / non-monotone frames (convention-breaking allowance); test on a toy block pair with the B11 oracle.
3. Totals supplied target-side (B10 esc.3): span(C + 32 target rows) contains them but is circular with the cut timing; reorder so targets of 4 blocks are final-written before the totals are used (B11_reorder).
4. Choose faces so that the 56 cluster on <= ~24 sources (30 pair regs): a different cover objective (min distinct sources), not the max-reach cover.
## Rescue check (not run, ~15 min): redo (c) with the actual 4-per-block constraint and the 6/4-tile library C (needs rebuild of J21-K tiles) to see whether any cover forces pair sharing <= 46; and a sign-aware version of the face forms (signs here are random; ranks are generic so unaffected).
