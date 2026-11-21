# CARRIER8 C8 (Nov 20, Opus, theory + exact checks). Own code: pa.py (PA-relay engine), q5.py, asc56c.py, split56.py, cfuzz.py; logs *.log. 1 proc, threads=1, no SAT/Lean.
Why not a retread: REUSE96 priced single-register chains (cold epochs only); UP/G2C priced lifetimes by FA/PA rows (hot intake = residual); UNIFY §7 read the Q5 rendezvous as a free PUBLIC NODE. Here hot intakes are resolved by past attribution into legal ⊥-RELAYS between owned epochs, so carrier runs become ordinary networks and the level cut applies.

VERDICT: Rendezvous Lemma A [P]: every pinned CF run (definition in §2) realising −I@Q96 has R ≥ 56 when its epoch factors have rank 8 on both sides. Carriers are free relays, not nodes. The cleaner + carrier + taker unit is a 2-node path costing ≥ 7. The R-side residual for rank ≥ 9 is the same network wall as on the D side. Not LOUD.

## 1. PA-relay dictionary [P]
Setting: the eng/fattr model.
- ADD d += λs needs chart(d) ⊆ chart(s).
- Publics only ascend; Y_s stays inside q_s^⊥.
- Pinned finals: Y_s = y_s; helper finals have a cold y-part; the x-part of X_t is x_t.
- Owned INIT is free anywhere, descents are free, and R = Σ ascents.

PA identity (exact telescoping). For a public P at time τ:
  content_P(τ) = final_P − Σ_{writes into P after τ} λ·content_src,
and public sources are expanded recursively. The result is
  ĉ_P(τ) = Σ_Q μ_Q ĉ(final_Q) + Σ_e μ_e ĉ_e,
where e runs over OWNED output events after τ.

Chart facts, for a taker at chart K reading P at τ:
- (i) every final term is cold at K. Its public Q had chart ⊇ chart(P) ⊇ K when it wrote, and Y_s ⊆ q_s^⊥. The effective content of an X final is 0.
- (ii) every event term has chart C_e ⊇ K. Writes into P need chart(P) ⊆ C_e, and P only ascends.

Epochs:
- An epoch is a maximal intake block followed by a maximal output block. An owned→owned read counts as an output of its source.
- The epoch's charts are A' = ∩ intake charts, intersected with the chart Z at the previous epoch's last output, and B = ∪ output charts.
- Its weight is w = Σ FA α over the block, and its content C is the effective content at the outputs.
- Its cold increment c is the sum of the final-parts of its intakes. Fold rule: a hot part whose net is cold at K counts as cold.

What this gives:
- (a) odd receipts = Σ_j w_j C_j^T (UP FA).
- (b) C = c + N·C, where N_{j,j−1} = 1 on the same register and N_{j,i} is the PA coefficient of epoch i's events.
- (c) supp c_j lies in the labels of A'_j^⊥.
- (d) RELAY LEGALITY: N_{j,i} ≠ 0 implies A'_j ⊆ B_i. For a hot edge, A'_j ⊆ K ⊆ C_e ⊆ B_i. On the same register, A'_j ⊆ Z ⊆ B_{j−1}.
- (e) the segment from the previous epoch's last output to this epoch's last output costs ≥ drop_j = dim(A'_j+B_j) − dim A'_j ≥ rank Q[supp w_j, supp c_j]. This is UP's modular induction with Z as a virtual first intake. The segments are disjoint.

Read through ⊥ (a = A'^⊥, b = (A'+B)^⊥), this is a legal NetW whose total drop is ≤ R. A hot intake is a FREE legal relay i → j with slack dim B_i − dim A'_j, realised by a public carrier instead of an owned descent. The node set is just the owned epochs. So the Q5 monotone run IS the NETATTR 2-node, 1-relay network, with the R2 descent replaced by the carrier (correcting UNIFY §7's "free public node").

## 2. Acyclicity (class CF) and the level cut [P]
- CF (clean-frozen): every event referenced by a hot pickup at τ belongs to an epoch whose last intake is before τ.
  - CF contains every frozen-cleaner rendezvous, including the Q5 run and all class-F runs.
- In CF the last-intake time λ strictly increases along every relay: hot edges have λ_i < τ ≤ λ_j, and same-register edges are time-ordered. So N is acyclic and C = (I−N)^{-1} c.
- LEVEL CUT (YC's proof verbatim): R ≥ Σ_m rank M_m, where M_m sums over sinks d with dim(A'_d+B_d) > m and sources g with dim A'_g ≤ m. It holds because along a relay dim A'_j ≤ dim B_i ≤ dim(A'_i+B_i).
- A weaker hypothesis suffices: only the "high" pure-relay subsystem (c = 0, dim A' > m) has to be nonsingular.

## 3. RENDEZVOUS LEMMA A @Q96 [P, from R96 + q96(c) + clique8, as WQ §2]
Statement. Take a CF run with odd receipts −I@Q96, and restrict its epoch factors to Q96: W = [w_j|Q96] and C = [C_j|Q96]. If rank_Q W = rank_Q C = 8, then R ≥ 56.

Proof:
1. col W = col M and col C = col M^T, so every c_j = C_j − Σ N C lies in col M^T.
2. By q96(c), every nonzero c_j has label span ≥ 8, so dim A'_j ≤ 1. Every nonzero w_j gives dim B_j ≥ 8.
3. Hence for m = 1..7, M_m = M (all source–sink walks cross level m), and rank M ≥ 8.
4. So Σ_{m=1..7} rank M_m ≥ 56. ∎

Path form (Menger, same hypotheses):
- rank M ≤ the maximum number of vertex-disjoint source→sink relay paths.
- A path v_0..v_m costs ≥ dim B_m − dim(B_m ∩ A'_0 ∩ … ∩ A'_m), by telescoping with A'_{k+1} ⊆ B_k. That is ≥ 7 here.
- So the cleaner + carrier + taker unit is priced as a PATH of epochs, not as one epoch. Each end keeps its own increment, and the carrier is the free relay.

## 4. Exact checks [C]
| run | pinned/legal | R | drops | own-price | level cut (per m) | relays / hot | notes |
|---|---|---|---|---|---|---|---|
| Q5 rendezvous, GF(2) and Q (q5.py) | yes | 2 | 2 | 2 | 2 ([0,2,0,0,0]) | 1 hot relay O0→O1, CF, acyclic | EQUALITY. Routing mass 3 > R. Naive per-lifetime price of O1 is 2 > cost 1. Control: wrong clean sign over Q leaves the run unpinned → rec/cold/seg fail |
| asc56 no-mix and mixed (asc56c.log) | yes | 56 | 56 | 56 | 56 ([0,8×7,0,0]); Q96 same | 0 | 8 epochs (1,8): 7 each; rank W\|Q96 = rank C\|Q96 = 8 |
| asc56 CARRIER-SPLIT k = 2,4,6,8 (split56.log) | yes, 0 bad | 56 | 56 | **0** | **56** (8 at m = 1..7, P104 and Q96) | 8 hot relays | Each lifetime becomes cleaner (dim A'=1, B=k: w=0) + helper carrier + taker (A'=K, B=8: c=0); acyclic; rank W = rank C = 8 |
| cfuzz.py, 18,600 random pinned carrier runs (GF(2) and Q; n = 3, 4; 4–8 ports) | 0 bad / 0 unpinned | — | — | — | — | ~1,650 with cross-register hot relays | 0 fails of PA identity, cold, chart, C=c+NC, receipts, relay legality, segment bound. 0 cyclic. 0 last-intake potential violations (checked on seeds 6–7, 6,000 runs). R ≥ drops ≥ LS always. Teeth weak (9 naive over-prices, 0 sharing gains) |

Lemma A is tight on real Q96 data with carriers: the split runs keep R = 56 = level cut for every rendezvous height k.

## 5. What this says about ChainWall56 and the rank ≥ 9 gap
- [C, split56] The own-price / chain-price form is FALSE as a carrier invariant. The generalised chain price of a pinned R = 56 run is 0, because silent cleaners and pure takers each own-price 0.
  - So REUSE96's ChainWall56 (min chain price) cannot be the R-side target once carriers exist.
  - UNIFY §7's NETWALL "Σ own-price ≥ 56" fails the same way: split any E8 row into a gather-only node plus a deposit-only node joined by one relay.
  - The correct invariant is in drop or level-cut form.
- The run-side wall needed is NETR56: every legal ⊥-network realising −I@Q96 (nodes = epochs, any free relays) has Σ drops ≥ 56. The sufficient relay-blind form is LEVEL-WALL (Σ_m rank M_m ≥ 56).
  - Under ⊥ these are the same objects as D-side networks. So NETR56 = NET-D56: one conjecture for both sides.
  - With carriers, relays are free on both sides, so no relay-cost argument can help.
- Wall56@Q96 is NETR56 restricted to relay-free networks (decoders). The gap NETR56 ∖ Wall56 is exactly the network-coding gain.
- Is ChainWall56 (network form) ⇐ Wall56 + a chain-to-decoder lemma in the rank ≥ 9 sector?
  - Formally yes, with the lemma NoGain≥9: every −I@Q96 network with factor rank ≥ 9 on some side has Σ drops ≥ min decoder mass.
  - But no GENERAL chain-to-decoder lemma exists. Q5/NETATTR has gain 1 [C] at factor rank = rank M = 2, so even rank-minimal networks share.
  - The rank-8 sector has zero gain only because of rigidity (q96(c): every col M vector spans ≥ 8 labels), not because of rank minimality. So NoGain≥9 must use Q96-specific structure and is not implied by Wall56 by any known argument.
- Per-level sharpening [P]: a sub-56 CF network needs a level m ∈ [1,7] with rank M_m ≤ 7. That requires a source with dim A' > m (content of label span ≤ 8 − m, outside col M^T) or a sink with dim(A'+B) ≤ m (outside col M). This is YC Cor B read through ⊥.
- Residual outside CF [CONJ]: a cleaner re-intake between a pickup and its clean can create relay cycles (junk loops), and then the walk-sum identity needs nonsingularity. No such pinned run was found (0 cyclic in 18.6k). A construction attempt fails because the carrier's own symbol rides with the junk.

LADDER (updated): R-side PR56 ⇐ [CF or nonsingular relays] + NETR56@Q96. Proved: the rank-8 sector (any carriers) and class F. Open: NETR56 in the factor-rank ≥ 9 sector, the same core as NET-D56 / Wall56(≥9). The owner rules forbid NetWall as a premise.

NEXT:
- (i) Lean: PA identity + chart facts + relay legality on top of FutureAttr/LevelCutRelay (Rendezvous Lemma A = LevelCutRelay with the rank-8 sector hypotheses).
- (ii) Prove CF is WLOG, or find a cyclic pinned run. Exhaustive search on Q5 with a CRI shape.
- (iii) Test LEVEL-WALL on rank ≥ 9 Q96 decoders with split relays.
