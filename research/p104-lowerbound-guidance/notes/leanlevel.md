# LEANLEVEL (Nov 20) -- lean/decoder-duality/Nov15/LevelCutRelay.lean, kernel-only, rc=0, axioms [propext, Classical.choice, Quot.sound] (axioms.log)
Proved: abstract node-restricted level cut (YC sec 2 exactly: M_l = G diag[db<l] N diag[l<=da] F), rank M_l <= |C_l|, sum_l rank M_l <= D;
NetW instance (relay rule b_j <= a_k = any slack); rank M >= 8 => >=8 gathering and >=8 depositing nodes; level_rank_ge56; NET8 corollary
with "<= 8" nodes (YC Cor. A) => 56 <= D. Non-vacuity: 2-node chain, slack-3 relay, rank M_2 = 1 <= |C_2| = 2.
Gaps/notes for YC.md:
1. Already in LevelCut.lean (Nov 19): port-restricted level cut for any relay graph; the NEW content is YC's node-restricted M_l and the "<=8" form.
2. YC says "<= 8 nodes"; the proof needs rank M >= 8 (clique8, hM), which forces EXACTLY 8 (rank_le_gat/dep) -- fine, now proved.
3. YC's "relays satisfy b_j <= a_k" must be the subspace inclusion; only dim b_j <= dim a_k is used by the cut (abstract theorem takes dims).
4. Corollary B (D<=55 needs a level with rank M_l<=7) is just the contrapositive of level_rank_ge56 / netw_level_D_ge; not P104-specific. The Lean hypothesis for P104 data is NetW.hM (M = c_s delta on odd pairs) only.
5. The step "rigid => dim a>=8, dim b<=1" (DFR) is used only for exactly-8 nodes; for >=9 nodes no rank fact on M_l is available (open: NET-D56).
