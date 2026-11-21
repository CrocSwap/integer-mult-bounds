# LEANCF (Nov 20, Sonnet) -- Lean for CARRIER8 + REUSE96 chain law. Kernel-only (axioms propext, Classical.choice, Quot.sound), all rc=0.
Files (lean/decoder-duality/Nov15/): CFChain.lean, CFRelay.lean, CFRelayE8.lean, CFRelayQ5.lean (+ oleans built in .lake/build/lib/lean/Nov15; LevelCutRelay.olean was missing, I built it).
Imports: FutureAttr (life_up/life_intake/life_output, price, exact_price, Row.ok analogue), PriceLemma, LevelCutRelay (abstract_level_D_ge, Mnode).
## Proved
(1) CFChain: one-register trace model (intake only before outputs = GTD per epoch; output; up/down), Pot = FutureAttr Inv.i6; seg_price (epoch segment cost >= dim(A+B)-dim A);
    Life = multi-epoch register (gap + segment per epoch, costs additive); price_le_charts (rank Q[supp w,supp c] <= dim B - dim(B^A)); life_chain/chain_law:
    R >= sum_j cost_j >= sum_j [dim B_j - dim(B_j^A_j)] >= sum_j rank Q[supp w_j, supp c_j]; chain_law_family; total_drop_le (nodes = epochs of a family).
    Tr.intake_le / Tr.output_le: A'_final <= chart at EVERY intake, B_final >= chart at EVERY output.
(2) CFRelay: hot_relay_legal (taker intake chart K <= chart P at pickup, P monotone, owned write at C_e >= chart P later => A'_j <= B_i), same_register_legal,
    relay_acyclic (lam strictly increasing along relays => no TransGen cycle), cf_time_hot, Tr.det.
(3) cf_level_cut: any labelling with lam increasing along relays (no index-order assumption): sum_l rank M_l <= sum_k (da-db); via Mnode_reindex (sort by lam) + LevelCutRelay.abstract_level_D_ge.
(4) rendezvous_lemma_A (matrix form, ambient F2^9): hyps rank(G N F)>=8, dim A'<=1 on supp F, dim B>=8 on supp G, relay legality A'_k<=B_j, lam => sum drops >= 56.
    rendezvous_lemma_A_run: same for CFChain.Life registers => R = sum c_r >= 56.
## Non-vacuity
CFChain.Toy.toy_chain: 2 cold epochs, R=2=sum drop=sum rank (price computed exactly = 1 each). CFRelayE8.e8_instance: 8 registers x 1 epoch (dim A'=1, dim B=8 in F2^9, cost 7), all Lemma A hypotheses proved, R=56 attained.
CFRelayQ5.q5_summary: Q5 carrier run (charts of C8 sec 4: O0 A'=<13>,B=<1,12>; O1 A'=<12>,B=<11,12>), two Lives R=1+1=2, drops 1+1, hot intake legal relay X1<=B0 (via hot_relay_legal), sum_l rank M_l = 2 = R (level 3 only).
## Gaps / honest caveats
- The run-level facts "w labels in B" and "c labels in A'^perp" (Life.cons hw/hu) are HYPOTHESES (they are Inv.i4/i5 of FutureAttr for single lifetimes); I did NOT re-derive the PA identity / chart facts (i), (ii) / C = c + N C from a full engine (ARun) with hot pickups. So the connection ARun -> Life (PA decomposition, N = PA coefficients, CF as a property of an engine run) is NOT formalised; CF is encoded as the lam-monotonicity hypothesis hHlam, and relay legality as hleg (hot_relay_legal proves it from the timeline hypotheses).
- Life models one register at a time with a free `gap` between epochs; "R = sum of ascents" over registers; owned->owned reads, public ascents are not modelled (they are free).
- rendezvous_lemma_A takes the three rank-8 facts (from R96/q96(c)/clique8) as hypotheses, as requested. Injectivity of lam is not needed (hHlam is strict), kept in signatures.
- Q5 instance uses Q5's chart geometry with synthetic port labels (hw/hu satisfied), not the real -I target; level cut equality 2=2=R.
