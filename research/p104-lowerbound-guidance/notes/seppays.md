# SEPPAYS SP (Nov 20, Opus, theory + exact). Own code here: arun_check.py (Task 0), eng.py (pinned-model engine, GF(2)/Q),
gen.py / gen2.py (Bennett F;G;F^-1 pinned generators, hot intake), gen3.py (separation gadgets: tree / shared / public carrier),
fa.py (global FA rows), sepcheck.py (carrier-tree class + decoder), f2mass.py (exact F2 decoder mass, Dijkstra), test*.py, f2_big.log.
1 proc, threads=1; no SAT/Lean/advisor/push.
Why this differs from FLUSHROW/G2C/UP: those priced one lifetime at a time (or flush rows). Here a nonzero-weight lifetime is
priced jointly with a forest of ZERO-weight lifetimes (token carriers), and only the root's FINAL effective content must be cold.
All statements port-general (any Q of odd vectors, any N).

## 0. Sanity: the relaxed cost-0 run is NOT in FutureAttr's ARun [P + C]
- The only ARun premise that fails is **hcold**, at `B_t += H_t` (B_t at <q_t>, content y_t, q_t.q_t = 1). It fails once per port.
- Everything else passes (arun_check.py: {1,2,7} and the 8 odd vectors of F2^4): hne, hch, hgtd, the up/down premises, h0, hq, hfx, hfy (the blanked helper ends at 0, which is cold), hfyX, hbal, receipts = −I, R = 0.
- [P] This failure cannot be avoided. Cleaning a hot public P by an owned register B needs chart(B) ≥ chart(P) (to write back) and chart(B) ≤ chart(P) (to read). So B sits exactly at P's hot chart, and its intake is hot.
- Hence the Lean theorem R ≥ mass is consistent. Note that ARun never mentions tokens: cold intake stands in for restoration.
- Control: the honest per-port run has 0 premise failures, R = |Q|.

## 1. Generators and exact tests [C]
- Every run below is replayed independently and checked: legal, pinned (helpers end = token, Y_s = y_s, X_t = x_t + y-part only), and the global FA identity holds over all symbols plus the odd-cell decoder identity (0 failures everywhere).
- **GF(2), exact F2 decoder mass:**
  - The mass is computed exactly by Dijkstra over odd-cell patterns, using all (D,S) rows.
  - [C] mass_F2 = rank_F2(Q∘Rec) for every pattern on {1,2,7}, {1,2,4,7}, {1,2,4,8,7} and {1,2,4,8,14}.
  - On {1,2,7,11,13} (N=4), 371 of 32,768 patterns have mass = rank + 1. Those are the only F2 patterns where SEP-PAYS says more than the REVERSE tensor bound.
  - gen2: 25k runs per port set, so 75k runs ({1,2,7}, {1,2,4,7}, {1,2,7,11,13}). Results: 0 runs with mass > R (no LOUD); 0 with rank > R (tensor sanity holds); about 25% hot; 112/166/107 tight runs (R = mass > 0); one gap pattern produced (R ≥ mass).
  - gen3 (tree/shared/pub) × 1.5k on {1,2,4,7} and {1,2,7,11,13}: 0 LOUD.
- **Q** (scalars ±1, ±1/2, 2) on {1,2,7}, {1,2,4,7}, {1,2,7,11,13} and the 8 odd vectors of F2^4:
  - gen2 3k each; gen3 1.5k per variant.
  - The FA row sum exceeded R in 21 runs. Every one is resolved exactly by a per-row or per-column decoder with price ≤ R.
  - 0 runs had no decoder at price ≤ R.
  - Exact mass over Q was NOT computed. These Q checks are one-sided: they show a decoder of price ≤ R exists.

## 2. THEOREM CT (carrier-tree separation) [P]
Setting:
- ARun WITHOUT hcold: ADD needs chart(d) ≤ chart(e) and d ≠ e; publics ascend; owned registers start at 0; the attribution_decoder final-data hypotheses hold.
- Every owned lifetime is GTD with respect to its read-outs (reads of it by anything).
- A_k = meet of k's intake charts. B_k = join of k's charts at its read-outs. W_k = global FA weight.

Hypotheses:
- Attach every zero-weight lifetime k to a parent p(k), with A_{p(k)} ⊆ B_k and no cycles. A direct read of k by p, or a same-chart hand-over through a restored helper, gives this.
- Let A*_m = meet of A_k over m's subtree.
- If eff(final content of m) is cold at A*_m for every root m, then {(W_m, eff c_m)} is a decoder of the odd receipts with Σ price ≤ R. So R ≥ m(Q), and Wall56@Q96 ⇒ R ≥ 56 on this class.

Proof:
- Non-roots carry zero weight, so the FA identity (which does not use hcold) leaves only the root rows.
- Price: labels ⊆ B_m and coldness at A*_m give price ≤ dim B_m − dim(B_m ∩ A*_m) (PriceLemma).
- Cost: dim(A_k + B_k) ≤ dim A_k + cost_k (FutureAttr invariant i6, GTD).
- Induction S(k): for every Y ⊆ B_k, dim Y − dim(Y ∩ A_sub(k)) ≤ cost(subtree k). The proof splits at A_k, then telescopes over the children using Z ⊆ A_k ⊆ A_p-condition ⊆ B_child. The step uses dim X − dim(X∩Y) ≤ dim X' − dim(X'∩Y) for X ⊆ X'.
- At the root, dim B_m − dim(B_m ∩ A*_m) ≤ cost(tree). Summing over the trees gives the result.

What CT covers:
- It contains class F (singletons, every intake cold), and also singletons whose hot intakes cancel inside them.
- It contains the FLUSHROW pinned witness: O with carrier O'; A* = {0}; price 1 = cost 1.
- [C] gen3 'tree' and 'pub' (the snapshot carried by a PUBLIC helper G whose token is copied by an owned kt) are 100% in CT: 6k runs, about 58% hot, 0 rows with price > cost, 0 with Σ > R.
- So a public carrier reduces to an owned carrier of ITS token. This is the SEPARATION-PAYS recursion, made exact.
- The relaxed run is outside CT (the cleaner B has no carrier), as it must be. CT uses no restoration directly; its coldness hypothesis is what restoration is supposed to force.

## 3. What is open (= SEP-PAYS minus CT)
- (a) SHARED carriers: one zero-weight lifetime serving two roots. gen3 'shared' over Q is 0% in CT, yet the decoders found are always ≤ R. Proportional root contents merge into one row: price ≤ dim(B1+B2) − dim(...) ≤ cost by submodularity [P]. Non-proportional sharing is unpriced.
- (b) Multi-epoch lifetimes. SPLIT turns them into hand-overs whose old epoch has NONZERO weight, so they are not carriers. This is the flush-row / label-split residual of FR §3.
- (c) [CONJ CT-COVER] In every pinned GTD run, after merging proportional roots, the zero-weight lifetimes can be attached so that every root is cold at A*. With CT this would give SEP-PAYS for GTD runs.
- (d) Field-agnostic test, the cleanest open instance: Q5 = {1,2,7,11,13} in GF(2), Rec rows t0: y2+y3, t2: y0+y1+y2, t3: y0+y1+y3. Rank 2, mass_F2 = 3.
  - Is there a pinned GF(2) run with R = 2? If yes, SEP-PAYS has no field-agnostic proof.
  - Hand attempts fail on token cancellation at the chart <1100,0001>: the available public contents have the u-coefficient locked to the token coefficient.
NEXT: (i) Lean: CT is about 150 lines on top of FutureAttr: drop hcold, add an attach map and the S(k) induction. (ii) Decide (d) by an exhaustive or structured search. (iii) Shared-carrier pricing via rank-merged roots.
