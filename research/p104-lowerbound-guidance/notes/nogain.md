# NOGAIN NG (Nov 20, Opus, theory + one exact check). Own code: lwcx.py -> lwcx.log (exact Fraction arithmetic, 1 proc, threads=1). No SAT/Lean/advisor.
Why not a retread: UNIFY §9-10 named LEVEL-WALL as the single core and asked for L1/L3. LEVELRANK (d56dir/levelrank, Nov 19) had already shown the level-rank minimum is 0 on P104, but UNIFY did not cite it.
This lane (a) re-verifies that fact independently on Q96 against UNIFY's exact statement, (b) proves the strongest relay-blind level cut (DX), and (c) explains why L1, L2 and the direct argument cannot work as stated.

## 0. Verdict: LEVEL-WALL is FALSE (as stated in UNIFY §4/§9) [P + C]. Not a closure. The core must be NET-D56 in DROP form.
- [C lwcx.py, exact] The network is a ROUTED E8 decoder:
  - n gatherers g_t with a = <q_t>, b = 0, F = e_t;
  - 8 hubs with a = <v_h, w_h>, b = <v_h>, where v_h is a P104 kernel line;
  - relays H[h, g_t] = U[t, h], and hub deposits G[:, h] = W[:, h], with W = Ah·A and U = Ah·A^{-T}/4.
- All conditions hold: decoder conditions (M_tt = 1, odd cells 0), the deposit rule (W[s,h] ≠ 0 ⇒ q_s ⊥ v_h), and relay legality (b = 0).

| set | rank M | D | YC level sum Σ_l rank M_l | DX sum (§1) |
|---|---|---|---|---|
| Q96 (n = 96) | 8 | 104 | **0** | 16 |
| P104 (n = 104) | 8 | 112 | **0** | 16 |

- So "every legal network realising −I@Q96 has Σ_l rank M_l ≥ 56" is false. It fails even inside the RIGID sector: M = G/2 exactly, rank 8.
- What it does NOT refute: NET-D56 itself (here D = 104 ≥ 56). The failure is in the invariant, not in the wall.
- Consequences:
  - "LEVEL-WALL ⇒ D ≥ 56 and R ≥ 56 modulo nothing" is void. The only true unified target is NET-D56 / NETR56 in drop form: Σ drops ≥ 56 for every network with D ≤ 55, i.e. no such network exists.
  - Any level-cut proof has to USE the budget D ≤ 55. LEVEL-WALL restricted to networks with D ≤ 55 is equivalent to NET-D56.

## 1. DX: downward-crossing level cut [P] (new; stronger per level than YC and NC/WC clique cuts on LR)
- Setup: an acyclic legal network with relays b_j ⊆ a_k and walk sum M = G N F. Call a walk (v_0..v_m) l-CROSSING if there exist i ≤ j with dim a_{v_i} ≥ l > dim b_{v_j}. Let M*_l be the sum over l-crossing walks.
- **Theorem DX.** rank M*_l ≤ |C_l|, hence **D ≥ Σ_l rank M*_l**.
- Proof:
  1. Let i* be the first index with dim a ≥ l, and j* = min{ j ≥ i* : dim b_{v_j} < l }. Then v_{j*} ∈ C_l:
     - if j* = i*, this is immediate;
     - otherwise dim b_{v_{j*−1}} ≥ l and b_{v_{j*−1}} ⊆ a_{v_{j*}}.
  2. The choice of j* depends only on the prefix up to v_{j*}. So M*_l = Σ_{x ∈ C_l} (G N)[:, x] · P_x, where P_x is the sum over admissible prefixes that end at x.
  3. A node k lies in exactly drop_k of the sets C_l. ∎
- Relay-free networks (decoders): DX = YC.
- On LR/lwcx: DX = 8 + 8 = 16 versus YC = 0. On E8 and the asc56 split runs: 56 = D, tight. DX ≤ D everywhere, Q5 included, since it is proved.
- Complement [P]: a non-crossing walk is a LOW prefix (every a < l) followed by a HIGH suffix (every b ≥ l). Hence M − M*_l is supported on cells (s, t) where t is gathered by a persistently-low walk or s is deposited by a persistently-high one.
  - So rank M*_l ≥ ω_odd(R*_l ∩ P*_l).
  - This is NC/WC's clique cut, but with "low/high" judged per WALK rather than per node. It is strictly sharper: on LR at level 2, P_2 = ∅ under NC while P*_2 = all ports.
- Both bounds are valid, so D ≥ Σ_l max(rank M_l^YC, rank M*_l).

## 2. Zero-drop contraction [P]
Every network is equivalent, at the same D and with M unchanged on odd and diagonal cells, to one in which every node has drop ≥ 1. So a counterexample has ≤ D ≤ 55 nodes.

Proof, for a node k with a_k = b_k. Make these replacements:
- Successors j of k gather k's ports directly: F_j += H[j,k] F_k. This is legal because q_p ∈ a_k = b_k ⊆ a_j.
- Predecessors i of k are rerouted to j: H[j,i] += H[j,k] H[k,i]. Legal because b_i ⊆ a_k ⊆ a_j.
- Predecessors i of k take over k's deposits: G_i += H[k,i] G_k. Legal because b_k^⊥ = a_k^⊥ ⊆ b_i^⊥.
- k's own term G_k F_k is dropped. It only touches labels s ⊥ a_k ∋ q_t, so it is zero on odd cells, and it is off the diagonal because q·q = 1.

D is unchanged and the node count falls by one. ∎

(NetContract handles tight RELAYS. This is the node version.)

## 3. Why L1 / L2 / the direct argument fail as stated [P], and the exact gap
- The rigidity inputs (q96(c): label span ≥ 8; R96) constrain only vectors of col M / col M^T.
  - Cut contents P_x (rows) and (GN)[:,x] (columns) lie in those spaces only when the factor ranks are 8. That is Lemma A on both sides (YC Cor A, C8 §3).
  - On LR, P_x = e_t ∉ row M: label span 1, rank F = 104.
- The per-level slice can therefore be EMPTY. On LR, M*_l = 0 for l ≥ 3 because every chart has dim ≤ 2. So "rank M_l ≥ 8 per level" (L1, L2, the direct argument) is false on Q96 itself. A Q5 test is moot, because the step fails before Q5.
- What LR pays instead: cut WIDTH with JUNK. At level 1, |C_1| = 96 and rank M*_1 = 8, so 88 dimensions of cut content cancel through G N, whose columns span only col M.
- PRECISE GAP (NoGain@Q96, drop form). Show that a network with ≤ 55 nodes, all of drop ≥ 1, cannot spend junk: that is, it cannot have levels where |C_l| > rank M*_l while other levels have rank M*_l < 8.
  - Equivalently: bound Σ_l (8 − rank M*_l)_+ by Σ_l (|C_l| − rank M*_l), the junk carried at the cut.
  - This is the brief's L1 (cancellation ⇒ rank loss elsewhere), restated with DX so that it is not false. It has to bound the loss by the junk, because on LR (Q96) the junk is 88 (level 1) + 0 (level 2) and the loss is 6 × 8 = 48 (levels 3..8).
- [CONJ JUNK-PAYS] Σ_{l=2..8} (8 − rank M*_l)_+ ≤ Σ_l (|C_l| − rank M*_l) on every legal −I@Q96 network.
  - It implies NET-D56: D = Σ rank + Σ junk ≥ 56.
  - It holds on LR (Q96: 48 ≤ 88; P104: 48 ≤ 96), on E8 (0 ≤ 0) and on asc56-split (0 ≤ 0).
  - Off Q96 it is UNTESTED. The Q5 analogue, with 2 in place of 8 (NA network, rank M = 2), has not been checked.
  - NEXT: an exact check of the Q5 analogue on NA/ZIGZAG, then a proof attempt via the cut factorisation M = M*_l + (low prefix)(high suffix).

## 4. Round 2 (coordinator follow-ups)
### 4a. L2TEST refutes JUNK-PAYS as stated; repaired in INVARIANT form [P]
- L2TEST: free zero-drop hubs (a = b = 0) add arbitrary even-cell mass Δ. This raises rank M*_1 from 10 to 96 at fixed D, so junk falls to 0 while loss stays at 48. Plain rank is not an invariant of the decoding problem, because even cells are free.
- Fix: replace rank by the ODD-PATTERN MIN-RANK
  μ_l := min{ rank X : X agrees with M*_l on the odd and diagonal cells } (min over all even-cell completions).
- **DX-inv [P]: D ≥ Σ_l μ_l.** Proof: μ_l ≤ rank M*_l ≤ |C_l| (§1).
  - Tight at E8. Levels 2..8 have M*_l = M with odd pattern I, so μ_l = 8: ≥ 8 from an odd 8-clique (the identity block), and ≤ 8 by E8 itself. That gives 56 = D.
  - On lwcx, plus any free hubs: μ_1 = μ_2 = 8 (same argument, M = G/2 has rank 8). The hubs only touch even cells, so the invariant cannot move.
- **JUNK-PAYS-inv [CONJ]: Σ_{l=2..8} (8 − μ_l)_+ ≤ Σ_l (|C_l| − μ_l).**
  - Equivalently D ≥ Σ_{l∉[2,8]} μ_l + Σ_{l∈[2,8]} max(8, μ_l). It implies NET-D56.
  - lwcx + hubs: 48 ≤ 104 − 16 = 88, for every Δ. E8 and asc56-split: 0 ≤ 0.
- Second, equivalent-in-spirit repair [P]: state plain-rank JUNK-PAYS only on zero-drop-CONTRACTED networks (§2). Contraction deletes free hubs, and their own terms are even-cell only. The invariant form is cleaner because it needs no normal form.
- Computing μ_l: an exact general min-rank completion is hard. A valid lower bound is the largest set on which the odd pattern of M*_l is a nonsingular triangular pattern (e.g. an odd clique on which M*_l is diagonal and nonzero). Any test with this bound checks a WEAKER loss side, so a violation found with it is not conclusive. Report μ only with lower and upper bounds (upper = rank of the actual M*_l).

### 4b. Decoder test of JUNK-PAYS [C, weak teeth]
- jp_dec.py: Gibbs walks on P104 Z4 decoders (E8 start; random 12-row factorisation start), 124 evaluations, both orientations. Result: 0 violations of plain-rank JUNK-PAYS.
- The minimum slack is 0, at E8 and at the 8-row random factorisation (levels all 8).
- The walks fill every level (ranks 12–16), so this is a consistency check, not adversarial. Plain rank is used here, and for decoders μ_l ≤ rank, so the check does not certify the invariant form.

### 4c. Proof attempt for JUNK-PAYS from the cut factorisation — NOT obtained. What is proved, and where it stops
- [P] After contraction every node has drop ≥ 1, so EVERY walk crosses at least one level downward (at its own nodes). Content is never invisible to DX; a level-l loss means content routed entirely below l (low prefix) or entirely above l (high suffix).
- [P] At level l: M = M*_l + X_l^{LL} + X_l^{LH} + X_l^{HH}.
  - LL = walks with every chart dim < l;
  - HH = walks with every b ≥ l (sinks deposit into a (≤ 9 − l)-dim b^⊥);
  - LH = low prefix then high suffix, factored at the first node with a ≥ l.
  - On an odd 8-clique K, I_K = M*_l[K,K] + X_l[K,K], so the loss forces rank X_l[K,K] ≥ 8 − μ_l^K for every odd 8-clique K ⊂ Q96 (369 frames lie inside Q96, R96).
- The obstruction to a charging proof: junk at level l' (|C_l'| − μ_l') is a kernel of the cut factorisation M*_l' = S P. Loss at level l is rank of NON-crossing content at l. Nothing ties a kernel at l' to non-crossing rank at l except node identity.
  - On lwcx the charge is level 3..8 loss (48) ← level 1 junk (88). There the junk comes from the low CHART capacity (dim-1 gatherers each cover one label), i.e. from N(d) = max labels in a d-dim chart.
  - A proof needs a lemma of the form: "content of label span ≥ 8 (q96(c)), routed with every chart < l, costs ≥ (8 − μ_l) of junk at levels ≤ l". This is WC's capacity/SOLE family made per-walk. WC's type-level IP stopped at 16, so the per-walk (DAG) version is the open step: WC §5's BOTTLENECK-CUT.
- So JUNK-PAYS-inv is a correct-looking target (0 counterexamples, invariant, implies NET-D56), but it is not easier than NET-D56 unless the per-walk capacity lemma is proved.

## 5. Lean (LEANDX, Nov 20): DX and zero-drop contraction formalised [P]
lean/decoder-duality/Nov15/LevelCutDX.lean, kernel-only, axioms [propext, choice, Quot.sound]. `dx_rank_le`, `dx_D_ge`, `netw_dx_D_ge`; `contract_identity`, `contractW`, `exists_contracted`, `contracted_live_le_D`; toys `ToyDX.dx_gt_yc` (YC sum 0 < DX sum 2 <= D 2) and `ToyContract.toy_contract`.
Gaps found: (a) Mstar is the 3-state automaton sum (crossing-walk sum by construction; no Lean walk bijection / M = M* + noncrossing); (b) contraction needs a_k <= b_k and, for "drop >= 1", the extra hypothesis b_k <= a_k for all k (not a NetW field); (c) nodes are isolated (Dead), not deleted; (d) the complement clique cut and DX-inv are not formalised. Notes: cards/WILD/NOVEL/leandx/NOTES.md.

### 4d. Q5 analogue (2 in place of 8) [C exact, q5jp.py -> q5jp.log]
| object | D | rank M | (l, \|C_l\|, rk YC, rk DX) | junk | min decoder |
|---|---|---|---|---|---|
| Q5 / NA (R2 through ⊥) | 2 | 2 | level 3: (2, 2, 2); all other levels 0 | 0 | mass 3: ONE row (dim a 4, price 3, b 1) covering levels 2, 3, 4 at rank 1 |
| ZIGZAG h=5 | 4 | 2 | (2: 1,1,1), (3: 2,2,2), (4: 1,1,1) | 0 | mass 6 (UNIFY §11; the re-run of the decoder search timed out, budget 6 was not re-decided here) |

- Analogue statement: JUNK-PAYS(r, L): Σ_{l∈L} (r − μ_l)_+ ≤ junk, which implies D ≥ r·|L|.
  - On Q5 the network has junk 0 and nonzero rank at level 3 only. So JUNK-PAYS(2, L) holds iff L ⊆ {3}, and then it only gives D ≥ 2.
  - Every window that would give the decoder floor (r·|L| ≥ 3) FAILS on Q5, as required: the gain there is real.
  - The same holds on ZIGZAG. The network has junk 0 and levels {2,3,4} with ranks (1,2,1). JUNK-PAYS(2, L) holds only for L ⊆ {3}.
- MECHANISM of the gain, read off exactly: sharing TRADES LEVEL SPAN FOR RANK.
  - The Q5 decoder spreads rank 1 over 3 levels (cost 3).
  - The network stacks rank 2 on one level (cost 2).
- JUNK-PAYS-inv on Q96 says precisely that this trade is impossible for rigid content. Every level in the window [2, 8] must keep μ_l ≥ 8, or the deficit must be paid in junk.
  - The window is forced by rigidity: on E8, q96(c) gives dim a ≥ 8 and dim b ≤ 1.
  - So the Q96-specific input has to be: rigid content (label span ≥ 8) cannot be compressed into fewer levels at no junk.
  - That is the per-walk capacity lemma of §4c. Q5 content has label span 2–4, so it can be compressed.
