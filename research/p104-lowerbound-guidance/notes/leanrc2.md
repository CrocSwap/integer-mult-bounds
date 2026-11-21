# LEANRC2 (Sonnet, Lean) -- lean/decoder-duality/Nov15/CallerRC2.lean (439 lines, rc=0 via runlean.sh, no sorry; axioms propext, Classical.choice, Quot.sound only)
Imports Nov15.CallerSGram (olean built to .lake/build/lib/lean/Nov15/CallerSGram.olean).
[P, Lean] rc2_lin   : rows b_r spanning K^m with |iota| independent kernel vectors supported on W  =>  m + |iota| <= |W|  (rank-nullity).
[P, Lean] rc2_pair  : s/=t, l>=2, Ghat_st invertible  =>  m <= rcDeep + rcShal  (m=2: >= 2), exactly CC section 1 pair form.
          Model = RB section 0 coordinatised: masks M, bh/ah supported on masks, Ghat_st = sum_r bh_r[s] ah_r[t]^T (gBlk), piece INSTANCES (role, block)
          with kernel x (supp E(q), sum x bh = 0 at every stage of q) and biorthogonal y. Proof as CC (a)-(c): surjectivity of rows on W from Ghat_st^-1.
[P, Lean] rc2_avg   : per-stage averaged row: m k (k-1) <= sum_r ( sum_{s in M_r, D_r>=l, |P|<l} (k-|P|) + sum_{s in M_r, D_r<l} (D_r-|P|) ).
[P, Lean] rc2_pair_sg: in any CallerSGram P_k=-1 frame (char/=2, K_tt invertible) the Ghat_st hypotheses hold (sgG_blk_unit, gBlk_eq_blkOf), for ANY piece data.
Non-vacuity: inst_rc2 (k=3,n=4 design, all-singleton pieces: kernel family empty); toy_rc2/toy_rc2_val (k=2,m=2, 3 roles, role 2 has the multi piece {0,1}
  with kernel (1,0,-1), toy_piece: nonzero kernel vector; exact values rcDeep=2, rcShal=0, i.e. the piece-carrying role is correctly NOT counted).
Gaps / clarifications for CC.md: (1) pieces must be piece INSTANCES (one kernel vector per role-piece). If two roles shared one vector per stage SET, the
  count would be |W| - #distinct pieces and RC2 would need + sum_q (n_q - 1); cc0's check2 counts roles, consistent with instances.
  (2) The L(k-L) regrouped averaged form needs pieces of a role to partition its mask (pc r s' = pc r s for s' in pc r s); only the per-stage form is formalised
  (the regroup is a finite identity). (3) x,y existence and biorthogonality are the RB model (hypotheses), not derived from prod V = -I in Lean; Ghat_st invertibility IS derived in SGram frames.
  (4) rc2_avg needs Ghat_st invertible for ALL s/=t.
