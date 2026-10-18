# B159 NOTES: minimum pre-read targets on #799 (exact-oracle conflict model + CP-SAT). CLOSED within the move family. ship=false
Files: mdl.py (271-move universe, exact oracle evaluate, pair table), ilp.py (CP-SAT, workers 2), tri.py (triple probe), pairs.pkl, tri.pkl.
Model (full #799 word, no 2-block shortcut needed: 14 ms/eval): moves = 84 h2r (read r not h, delete matching pre-read), 92 r2h (read h, insert pre-read), 95 pre-read deferrals
(to just after a later t climb whose frame holds h's), + 46 whole-copy-pair bundles. Leak set V(m) = exact set of raised final caps / centre violations from the forward join cascade.
Data: singles legal 0/271 (every |V| >= 2). Pairs 36,501: legal 0; creating NEW violations 0; 76 non-additive pairs (h2r+r2h, same pair) only SWAP violations (|V| 4->4). Min |V| over pairs = 2.
Triples: all 76 repair pairs x every 3rd move (20,368): legal 0, min |V| = 2. Bundles: 38/46 legal (exact), all net <= 0 (B155).
ILP: minimise touched targets, repair constraint "each leaked cap needs a pairwise repairer in the set", insert/delete pre-read counts per target.
- Ignore legality (ceiling of the move family): min touched 21 (45 cleared; exact check of that set: 104 violations).
- Legal moves only (singles V=0 + legal bundles) and the pairwise-repair model: min touched = 66, OPTIMAL, bound 66. Best legal set (9 bundles): touched 66, dk -3.2e-7.
Answer: minimum = 66 (full word) vs threshold 62: no target can be cleared. Pre-read lever CLOSED for this skeleton under exchange/deferral/h2r/r2h/copy-pair moves, retained frames.
Proof status: exact legality for every evaluated set; the bound is PROVEN only at the pairwise/triple-probe level (singles, all pairs, repair-pair triples), not for arbitrary k-sets (B155 adds target-sharing k<=3 move level, k<=4 pair level: 0). Not tested: copy-gate retiming jointly (B158 singles only), re-gauge, end-frame convention.
LEAD/SHIP: none.
