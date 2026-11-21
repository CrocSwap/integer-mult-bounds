# CFGBRIDGE (Nov 20, Sonnet, Lean). File: lean/decoder-duality/Nov15/CallerCfgBridge.lean (runlean rc=0, ~10 s, 2.5 GB; no sorry/native_decide; axioms propext/Classical.choice/Quot.sound).
Headline word_hpq [P Lean]: Legal type-B word (JB), odd targets, k>=77, n+2=|Iota| (e=0, T=Q), lambda!=-1 on every host slot (K-block unit), every role degree>=1  =>  cHatQ w < 128.891.
cHatQ w := 104/k (invoice - (n-(2k-2))) (CallerEv invoice, one unit per excess role = LawQ's valQ); cHatQ_q0: n+2=2k => cHatQ = cHat.
word_lawQ: exists Cfg k with LawQ and valQ = cHatQ w; EVERY LawQ field derived (no frame field assumed):
 DEEP/mains <- deep_stage (ev_pair l=2 via word_rc2_pair + per-stage Match; leaves absorb singleton events, >=2 left for deg>=2 roles) + mains_real
 rc2 (l>=3) <- rc2_row_real (rc_row_nat); piece/mainsing <- Match.mem/sub/decide
 lc <- Host.leaves_le (leaf_channel_thin; Th = non-J columns, Hs = J.pos; KInj via 2x2 block kblock_zero)
 leaf <- Host.leaves_le_kT (CallerThin.leaf_rank per stage, <=T each, biUnion over stages)
Frame-level core: structure Host (abstract A,B,beta). Non-vacuity: instHost = CallerThin A1/B1 (1 host+1 thin, n=1, leaf): inst_leaves (LC 1<=2, LEAF 1<=1), K-block det proved.
Not done: word-level instance (toyW has k=1; DEEP needs k>=2 and hlam for toyW not computed in Lean); type-A schema (JA slots span two events); TRIPLE row; role-degree>=1 and n+2=|Iota| remain hypotheses.
