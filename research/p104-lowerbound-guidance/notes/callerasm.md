# CALLERASM (Nov 20, Sonnet, Lean). Files (lean/decoder-duality/Nov15/, copies here): CallerEv, CallerAsm, CallerAsmA, CallerAsmToy.
All built via runlean.sh, rc=0, ~6-15 s, <= 2.6 GB; no sorry/native_decide; axioms of every headline = propext, Classical.choice, Quot.sound.
Not a retread: CALLERWORD derived the analytic fields GIVEN a piece->role attribution (open). Here the attribution is removed.

## 1. Event-indexed RC2 [P Lean] (CallerEv)
- EvData: events e (support S e), kernel vector x e, dual y e, indexed by roles; fields x_supp (S e ⊆ M r), x_ker (|S e|>=2), biorth (events SHARING a stage: Σ_r y_e x_f = δ_ef).
- ev_pair: m + #{e : s∈S e, 2<=|S e|, (l<=|S e| or t∈S e)} <= #{r : s∈M r, (l<=|M r| or t∈M r)}  (reuses rc2_lin; independence from biorth at the common stage s; no role attached to an event).
- ev_avg: m k(k-1) + Σ_e Σ_{s∈S e} wl(|S e|) <= Σ_r Σ_{s∈M r} wl(|M r|), wl d = if l<=d then k-1 else d-1 (order/attribution free).
- HP objective: NO per-role partition is needed. exists_match: per stage s, V|_{E_s} invertible (W^T V = 1 + |roles at s| = |events at s|) => det expansion gives a bijection roles-at-s -> events-at-s with S(ev r s) ⊆ M r (one bijection PER STAGE, not consistent across stages: that is exactly what is not required). With a r s := |S(ev r s)| the stage form of HP is an exact re-expression of the event-form invoice: Σ_r roleVal = Σ_r (8D_r+1)^σ − Σ_{events} (8|S e|)^σ (roleVal_sum; a piece of size L contributes L stages × (8L)^σ/L). The RC2 rows and MAINS also transport exactly (rc_row_nat, mains_sum).
- ev_frame_bound: [3<=k, hbh/hah, EvData, Ghat_st invertible, counts, n+2<=2k, D>=2, ≥2k singleton events] => 104/k·invoice(.99) <= HP(k).
- Non-vacuity: toy_ev_pair (CallerRC2's toy re-indexed: ONE 2-stage event with x=(1,0,-1), tight 2+1<=3); toy_hp (CallerSGram's k=3 design A3/B3, singleton events, ev_frame_bound instantiated, not vacuous).
## 2. Words (CallerAsm, CallerAsmA)
- Sch interface: col s : two stage columns of the Iota frame, ord (stage column pairs ordered in event time), mains, hbh/hah, ker. JB (type B: HOST(u,v,a,b) a,b≠0 + IDLE u{s}, IDLE v{s}) and JA (type A: 2 HOSTs + 4 idles, α≠0; new jA_xker) both give a Sch. Anything else may sit between records (multi-stage IDLE, thin QUERY/IDLE_ODD, ADD/SCALE/...: extra D-incidences are just more events).
- wordEv: x_supp from support_VW, biorth from W^T V = 1, x_ker from jB_xker / jA_xker; word_count from stage_incidence. No regrouping to Fin k × Fin 2 blocks was needed: G_blk_unit_ord proves Ghat_st invertible in the EVENT-LABELLED frame (only needs: stage s columns before stage t columns), from sgForward rank K<=2 (needs n+2 = |Iota|) and the K-block hypothesis.
- word_rc2_pair (any thin columns, n+2 = |Iota|, i.e. T=Q covered): the RC2 pair form for legal words.
- HEADLINE word_hp / word_hp_B / word_hp_A: Legal w, schema, odd targets, k>=3, |Iota| = 2k (Q=0), n+2 = |Iota| (tight), lambda≠-1 (K-block of each stage's two columns invertible), D_r>=2  =>  cHat w := 104/k·invoice(.99) <= HP(k) (CallerHP.HPr).
- Non-vacuity (CallerAsmToy): legal word toyW (n=2,k=1, HOST(0,1,1,1)+2 contacts+swap/scale/2 thin QUERY, targets q^3,q): Legal in Lean (all rings), JB instance, odd, |Iota|=4=n+2, word_count (2=2), word_mains, wordEv instantiated. [C exact] prod V = -I, K block det 8. k=1 so pair statements are vacuous and the K-block (hlam) statement is not proved in Lean.
## 3. What remains / caveats (honest)
1. cHat is DEFINED as the event-form invoice (Σ_r (8D_r+1)^σ − Σ_events (8|S e|)^σ). It equals the role-piece invoice of any consistent attribution; its identification with the true cost is the CC/KASYM model, outside Lean (as before).
2. Tightness n+2 = |Iota| is a HYPOTHESIS (not derived): role_count_lam gives n+2 <= |Iota| only; Ghat_st invertibility (rank K<=2) needs equality. HP arithmetic itself needs only n+2<=2k.
3. lambda≠-1, Q=0, D>=2 remain branch hypotheses (Q=0: |Iota|=2k). For Q>=1 (T=Q) word_rc2_pair holds but HP(k) is NOT claimed (QB: HP_Q differs).
4. Q=0 + odd targets: no legal Q=0 word is exhibited (toy has T=Q=2). Existence of such words is open; word_hp's hypothesis cluster is exhibited non-vacuous only at the abstract level (toy_hp) and for the thin schema (toyW).
5. #7113 (n=36,k=17,Q=4, type B tight, 17 K-blocks invertible [C cw1]) satisfies the hypotheses of word_rc2_pair in principle; Legal #7113 in Lean (36 roles) NOT done.
6. Window k=5..71 for HP is unchanged (HP(k)>bar there); this lane only removes the attribution premise of CallerHP.frame_bound for words.
