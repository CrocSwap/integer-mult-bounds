# B175: re-balance 12 demand planes S1 stoppers vs B delivery. VERDICT: KILL PROVEN (scope: #656 skeleton, block 4567, shipped frames/values; register-count c_B). ship=false, no oracle/cpuq.
Tools (single process, seconds): gate.py/gate2.py/gate3.py (replay A,cut,B,tail,comp with exact rows; reads of any source whose row support lies inside a non-stopper plane). Block cols here are 20,21,36,37,46,47,110,111 (= card's 22,23,...; relabelled).
## Measured (4567)
- Non-stopper planes (2 classes, 4 planes): P1{20,21,46,47} P2{36,37,110,111} P3{20,37,46,110} P4{21,36,47,111}; stoppers = other 8 demand planes (8/8 confirmed).
- B delivers them through exactly the 8 PAIR-bound registers (lines 21,36,47,111 + scratch 441,443,445,447): 4 pair forms (20,46),(21,47),(36,111),(37,110), each held by 2 registers (original + twin), each pair used by exactly 2 of the 4 planes and by NO stopper plane (checked: no stopper contains both points of any pair). Plus couriers 437/442 (already whole-bound, counted in S1's 8).
- Readers (comp-phase targets 113.. ) get them as 1-4 reads of 441/443/445/447 (+437/442): extra ops, but NO extra registers; 447 additionally accumulates plane P2 in B for free (B170/173 accumulators 594/603 hold P4/P2 once).
## c_B (registers attributable to B-delivering one non-stopper plane)
- All 4 planes moved to S1 (k 8->12): S1 +2 regs/plane = +8; frees all 8 pair-bound regs (pairs no longer read) => c_B = 8/4 = 2.0 per plane => net (c_B-2) = 0.0. Total regs 12 stoppers+12 whole = 24 = same budget (B167 matching tight).
- Moving ONE class (2 planes) or one plane: pairs still needed by the remaining planes (each pair serves 2 planes, in both classes) => frees 0 => c_B = 0, net -2 per plane (worse).
- Opposite direction (k 8->6, deliver a stoppered class via B): needs new pair forms in another direction (4 pairs per class, twins forced by 2 crossing reader blocks B110) => c_B_added 4-8 regs vs 4 freed: net <= 0.
=> c_B = 2 within +-0.5 in both directions (partial moves strictly worse). Shipped trade is balanced; KILL PROVEN. Net helpers per moved plane: 0 (full) / -2 (partial). Word-wide gain 0 (<5 needed).
## Not covered
Op/read count (not registers) differs (stopper = 1 read vs 2-4); no register price. Blocks (0,1,*) not scanned (escape 2 for B171). Interface rewrite (lines holding plane rows) untested but is register-neutral by count.
