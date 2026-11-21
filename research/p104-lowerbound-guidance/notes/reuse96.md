# REUSE96 RU (Nov 20, Opus, theory + exact checks). Own code: chainfuzz.py (chain-law fuzz, GF(2) and Q), encm.py (enc6 + --mono / --absmove flags), eng.py (copied from r2test). 1 proc, threads=1; kissat only (≤ 20 min, feasible control first).
Why this differs from UP/G2C/SP/CT/R2: those price one GTD lifetime (or a SPLIT forest) as ONE row. Here a multi-epoch lifetime is priced EPOCH BY EPOCH against the epoch's own output increment w_j (not the Abel row weight W_j = Σ_{i≥j} w_i). This is the invariant that R2's run is tight for, and it is what Lemma A extends to.

VERDICT: no R < 56 construction. Shared climbs cannot go below 56 in the rank-8 (E8) sector [P]. Any shared-climb counterexample must have epoch-factor rank ≥ 9, which is the same open core as Wall56@Q96. But the R side needs the CHAIN form of the wall, ChainWall56@Q96, and that is stronger than Wall56. Not LOUD.

## 1. Chain law (multi-epoch class F) [P]
Setting: the ARun/engine model (free INIT anywhere, free descents, R = Σ ascents).
- An epoch of an owned lifetime is a maximal block of intakes followed by outputs.
- Each epoch's intake must be cold in effective content at its own intake charts. That is class F per epoch; the lifetime as a whole need not be GTD.
- For epoch j, let c_j = its net intake, w_j = its net FA output weight, A_j = the meet of its intake charts, and B_j = the join of its output charts.
- Then (a) the odd receipts are Σ_j w_j (Σ_{i≤j} c_i)^T, with the sum taken per lifetime (FA identity). Equivalently they are the Abel rows (W_i = Σ_{j≥i} w_j, c_i).
- (b) R ≥ Σ_j [dim B_j − dim(B_j ∩ A_j)] ≥ Σ_j rank_F2 Q[supp w_j, supp c_j]. This sum is the CHAIN PRICE.

Proof:
- The time segments from first intake to last output of each epoch are disjoint. Each segment is GTD, so UP §3's cost lemma applies to it. Descents between segments are free.
- The labels of supp w_j lie in B_j, and those of supp c_j lie in A_j^⊥. The bound then follows from PriceLemma.
- Degenerate epochs reduce:
  - An epoch with net intake 0 merges into the previous one. Its intakes are irrelevant, and the after-last-intake path bound holds for any path.
  - An epoch with net output 0 merges into the next one. Its outputs are irrelevant; the merged row is (W_{j+1}, c_j + c_{j+1}), cold at A_j ∩ A_{j+1}.
- So WLOG every epoch has w_j ≠ 0 and c_j ≠ 0.

What the chain law says about known runs:
- R2's run has chain price 1 + 1 = 2 = R, so it is tight: epoch 1 is ({t0}, {y2,y3}) and epoch 2 is ({t2,t3}, {y0,y1}). The Abel rows price 3.
- So the correct run-side invariant is the CHAIN MASS m_ch(pattern) = min over chain decoders of the chain price. Here m_ch ≤ m, with equality for single-epoch chains. R2 and CTCOVER show m_ch < m (Q5: 2 < 3).
- Exact fuzz, chainfuzz.log [C]: 60,000 random multi-epoch runs over GF(2) and Q (scalars ±1, ±1/2, 2, −3/2) on {1,2,4,7}, Q5, and the 8 odd vectors of F2^4.
  - 0 failures of (a) on all cells, of the per-epoch bound, or of R ≥ chain price.
  - About 22k runs have multi-epoch lifetimes.
  - 63 runs have Abel row price > R. That is the teeth: shared climbs really happen in the fuzz, and the chain law still holds.

## 2. CHAIN LEMMA A at Q96 [P, from R96 + q96.log(c), as WQ §2]
Statement: suppose a chain-F run on Q96 realises −I on the odd cells, and its reduced epoch decoder has rank_Q[w_j] = rank_Q[c_j] = 8. Then every epoch costs ≥ 7 and there are ≥ 8 epochs, so R ≥ 56.

Proof:
1. M = W_mat C^T has rank ≤ 8, and clique8 gives rank ≥ 8. So R96 applies: M = Λ(Ah)(Λ^{-1}Ah/4)^T, col(W_mat) = col(M) and col(C) = col(M^T).
2. So each epoch output w_j is Λ Ah a for some a ≠ 0. By q96(c), the labels of its support span ≥ 8 of the 9 dims. The same holds for each intake c_j.
3. Hence dim B_j − dim(B_j ∩ A_j) ≥ 8 − 1 = 7.
4. The c_j have rank 8, so there are at least 8 epochs. ∎

Coordinator's question (E8 rows sharing a climb):
- Answer: no saving is possible in any order.
- A chain of E8 rows k → l has epoch output w_k − αw_l ∈ col(M) \ 0. That output's label span is ≥ 8, while the intake chart has dim ≤ 1, so the CT overcount term dim B2 − dim(B1∩B2) never turns into a saving.
- The E8 rows' charts can share a climb, but every epoch increment is still a full-span vector.
- So R2-type reuse at Q96 needs epoch increments outside an 8-dim column space. That forces factor rank ≥ 9 on a side (overcomplete/cancelling epochs).

Corollary [P]: any chain-F run on Q96 with R < 56 has reduced epoch-factor rank ≥ 9 on some side. This is exactly WQ's corollary, extended from decoders to chains.

## 3. Status of the R side (ladder update)
- Allowed-premise gap:
  - R ≥ 56 for chain-F runs ⇐ ChainWall56@Q96: m_ch(−I@Q96) ≥ 56.
  - This is STRONGER than Wall56@Q96, the allowed premise. Lemma A covers rank 8 for both forms.
  - No reduction ChainWall ⇐ Wall is known. The Q5 gap m_ch = 2 < m = 3 is for a non-identity target. Over F2 with the identity target, rank = n kills the gap (CT §3).
- CORRECTION from §4 [C]: the R2 saving does NOT need a descent. Charging descents does not rescue anything, and OWN112 per cluster fails on Q5 too (D + R = 2 < mass 3).
- What reuse really needs is free birth at a nonzero chart. That is the word model: R − D = Σ(dim CLEAR − dim INIT), and the t7669 R chains start at 1-dim charts.
- With INIT forced to {0}, R2 Result 2 found R = 2 UNSAT within its bounds.

## 4. Small exact SAT [C] (Q5 target, nh = 1, no = 2, L = 16, kissat, each ≤ 20 min, feasible control first)
- Control: R = 2 SAT at L = 16 (290 s), replayed: legal, pinned, cost 2, receipts = target.
- --mono (owned descents forbidden): SAT, R = 2 (719 s, replay ok).
- --absmove (descents charged, so the bound is on D + R): SAT, cost 2 (432 s).
- The decoded run (g2run.py → g2run.log, independent eng replay) has bad = [], pinned = [], R = 2, 0 owned descents, odd pattern = the target, F2 mass 3, rank 2.
- Mechanism (Y-carrier rendezvous, UP's G2 shape, now with a mass gap):
  - Both lifetimes are monotone and GTD. O0 is born at <13>, takes y2 and y3, and deposits y2+y3 into Y1, which is at {0}.
  - Y1 climbs to <12> and hands y1+y2+y3 to O1, which is born at <12>. That is a hot intake.
  - Y1 climbs to <1,12,13> and delivers into X0, a public hot delivery.
  - O0 climbs to <1,12,13>, cleans Y1 and pays 1. O1 takes y0, climbs to <7,11,12>, delivers to X2 and X3, and pays 1.
- So R ≥ m fails for GTD monotone runs as well. The failure lives in the hot-intake / public-delivery classes (G2), outside chain-F, and §2 does not cover it.
- Q96 status: whether Chain Lemma A extends to rendezvous runs is OPEN. A hot intake lets a lifetime be born at a large chart, so the "intake chart dim ≤ 1" step fails.
NEXT: (0) Rendezvous Lemma A: in the rank-8 sector, price the cluster (cleaner O0 + carrier + hot taker O1) with ≥ 7 per cluster output; the E8 B-charts are 8-dim and every col(M) vector has label span ≥ 8. (i) Lean: the chain law is about 120 lines over FutureAttr: epoch-split ARun, a per-epoch Inv, and the sum. Chain Lemma A is a small addition to the Lemma A chain. (ii) ChainWall in the one-sided rank-8 class (WQ §3), via the same assignment search with epoch increments. (iii) First place to test m_ch < m_Q for −I with half-integers: the E7 shard (n = 63).
