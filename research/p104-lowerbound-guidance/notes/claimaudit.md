# CLAIMAUDIT (read-only) on pkgfinal/PR_BODY.md (= body.md + header). Lean read for C1,C2,C6,C10,C14,K2,K7,K8; rest from body text vs. hypotheses named in it.
Verdict: NOT ready as written. Rule breach: CLAIMS contain non-Wall56 premises. Fix = move rows, reword intro.

## Intro sentence (breach)
Now: "CLAIMS are theorems whose only hypotheses are the definition of the class or branch ... no row uses ... any other unproved premise."
Fix: "CLAIMS are theorems whose hypotheses are only the definition of a model class (linear, Z/4-linear, legal word, verifier clauses). Any theorem with a further structural hypothesis (tightness, lambda != -1, degree bounds, k thresholds, P_k = -1, H_frame/H_FS4/H_id, J-schema) is a CONDITIONAL LEMMA and is listed there with that hypothesis named."

## Move CLAIMS -> CONDITIONAL (extra hypothesis not Wall56, not class definition)
- C10 (word_hp/_B/_A, verified in CallerAsm/CallerAsmA): hyps = hQ0, hn tightness n+2=|Iota| (underived), hlam, hdeg>=2, k>=3, odd, Sch mains. Extra hyp: "tightness n+2=|Iota|, lambda != -1 on each stage K-block, D_r>=2, MAINS, J schema". Also the "<128.891 for k>=74" is a COMPOSITION (word_hp + CallerHP.hp_lt_128891); no single Lean theorem; say "by composing".
- C14 (word_hpq/word_hpq_A, verified): hyps hk 77<=k, tightness hn, hlam, hdeg1 (D>=1), odd. Move; extra hyp: "tightness, lambda != -1, D>=1, k>=77". Keep "non-vacuity frame-level only; no word instance k>=2".
  Both rows: conclusion is about cHat/cHatQ, DEFINED event-form invoices; suffix "(a bound on a defined invoice, not on the caller cost; no kappa/ceiling claim)".
- C13: row itself says "conditional on P_k=-1" (sgForward) -> split: unconditional normal form stays; rank K + n <= |iota| and RC2 go to CONDITIONAL "extra hyp: P_k=-1, char != 2".
- C11: needs lambda != -1 on host slots and full product -1 -> CONDITIONAL.
- C9 pair form needs |Iota|=n+2 -> CONDITIONAL (extra hyp: tightness for the pair form); ev_avg part may stay.
- C8 role_count_lam needs lambda != -1: split that item to CONDITIONAL; rest of C8 OK.
- C4: Lemma T/all-or-nothing/chart-clean need H_id, H_frame, H_FS4, A in Lam, trace-model hyps -> CONDITIONAL, extra hyp "the named H_* hypotheses (verified for P104 frames only as [C] in C5)". PRICE7 reduction itself may stay (pure rank arithmetic) if it has no H_*.
- C5: "block laws keep H_FS4 (and A,B inside D,S) as hypotheses" -> block-law half to CONDITIONAL; FrameCert/BlockComplete computations stay.
- C7: relay rule b_j<=a_k and triangularity are network properties; OK as a class definition but add "(networks only; applies to words via C6)".

## Wording overstatements in rows that stay
- C6: "So the network results LevelCutRelay, LevelCutDX, Net8Cut are theorems about words" -> "LevelCutRelay and LevelCutDX apply to word networks; Net8Cut gives D>=56 only under at most 8 gathering and 8 depositing nodes (K1)". word_net_laws verified: ownDrop>=56 conclusion is implication on <=8/<=8.
- C6 also needs hyps Word cl s, ChartsSubsp, OwnedNested, hlab (labels = DW4 labels via permutation): present, OK.
- C2/DataId: Lean text says "unconditional on the data tables" - true for tables; body correctly states which-104-lines is instance data. OK. Keep "Z/4-linear only" in the Statement cell, not only Scope.
- C1: linear_cost_ge also needs hMu (row-pair matrix invertible), hB, HInj: all in Scope. OK. Add "linear decoders only" to Statement ("not a general decoder bound").
- C12: OK (explicit scope).
- C3: OK.

## Conditional section
- K7: rung_word_7113_joint/_of_halves verified: premise hJ = 112*17 <= sum(descMass+hostedRise) plus hV crossing. Table already says so; ADD in the Statement cell the words "CONDITIONAL on hJ and hV" before "kappa < .0093454", since the κ number appears bare. Keep no-κ-claim sentence adjacent.
- K2: cited as BridgeNet.rung_hD_of_netD56; located in BridgeRung.lean, namespace BridgeNet -> name is right.
- K8 verified: corollary_ge72 takes h72,h73,Extra as hypotheses. OK.
- K1: Lean says <=8 gat and <=8 dep; body says "at most 8" in extra hyp, but headline text "gatS.card = 8" - say "<= 8".
- K10 OK. K3-K6, K9: consistent with body; not re-read in Lean.

## Checks
- TIGHT55 / old unsound result: grep of body, PR_BODY and package tree: ABSENT. OK.
- DRAT section: not in PR_BODY.md (correct for interim). When added: must say "trusted base: DRAT checker + CNF encoding; not kernel-checked; conclusion conditional on encoding fidelity".
- Not-covered list: adequate (mid-k window, e>=1, NET-D56 core, R side, general decoder wall, no kappa/ceiling). ADD: "C10/C14 hypotheses (tightness, lambda != -1, degree) are not shown for any actual caller word with k>=5" (partly present in Premises bullet) and "cHat/cHatQ are defined invoices".
