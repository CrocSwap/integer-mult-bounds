# JASCHEMA (Nov 20, Sonnet, Lean). File: lean/decoder-duality/Nov15/CallerJASchema.lean (runlean rc=0, ~7 s, 2.5 GB; no sorry/native_decide; axioms propext/Classical.choice/Quot.sound).
(Also built the olean of CallerCfgBridge so it can be imported.)
Headline word_hpq_A [P Lean]: Legal type-A word (JA), odd targets, k>=77, n+2=|Iota|, lambda!=-1 on each stage's 2x2 K-block (type-A K-block spans two slots), every role degree>=1 => cHatQ w < 128.891.
Obstruction: JA's two host columns sit in different events (pos s, pos s+1), so CallerBridge.Host (both columns in one slot) and LeafSet (leaf vanishes off ONE slot) fail on the event-labelled frame.
Fix: merge slot pos s+1 into pos s (beta' = betaA J).
 - G_zero [P]: G(col s 1, col s 0) = b_HOST2 . a_HOST1 = -2 [v=y] = 0 (M M^-1 = 1 at P1(pos s+1); fields y,v distinct).
 - low_eq / sgK_regroup / prod_regroup [P]: if for all i j (beta' j<beta' i <-> beta j<beta i) or G i j = 0, then sgLow, sgK (via sgK_eq) and sgProd (via sgProd_eq) are unchanged. betaA_rel: the relation differs only at (col s 1, col s 0) where G=0.
 - hostA [P]: Host structure on (Aw,Bw,beta'): hP = -1 transferred, hlam transferred (K identical), <=2 columns per merged slot, hA/hB from JA.sch.
 - word_lawQ_gen [P]: CfgBridge's word_lawQ for ANY Sch, with the three leaf facts (2k<=|Iota|, LC, LEAF) as hypotheses; word_hpq_A feeds them from hostA (leaves_le, leaves_le_kT). DEEP, RC2 rows via the generic Sch lemmas.
Q=0: word_hp / word_hp_A (CallerAsm/CallerAsmA) already cover type A for Q=0 (hdeg>=2, |Iota|=2k); nothing to add.
Non-vacuity (frame level only): toy_* : n=2, two single-column slots p,q, G_pq=1 (nonzero), G_qp=0, order relation genuinely changed (toy_changed); toy_rel hypothesis holds, toy_prod, toy_prod_val (= [[1,1],[0,2]]), toy_K [P Lean].
NOT done: word-level instance with k>=2. A legal tight k>=2 word needs shared roles across stages (a disjoint union of toyW's has |Iota|=2n, not n+2); finding one is a search + Legal-over-all-rings proof, not cheap. #7113 type A (n=36,k=17) has n+2=|Iota| [C cw1] and hlam [C]; Lean Legal for it not built.
Still hypotheses: n+2=|Iota| (tightness), lambda!=-1 (2x2 K-block), role degree>=1, odd targets.
