# NONLIN NL (Nov 20, Opus, theory + exact checks). Own code in this dir (venv python, 1-2 procs, threads=1; kissat only, <= 20 min).
Why not a retread: LINEAR56 closed decoders linear on BOTH sides; DOUBLE56/TAU48/ARF attacked rho_A+rho_B / tau48 for all decoders.
This lane takes decoders linear on ONE side only (the other side, and the number of rows, arbitrary), finds their exact structure,
and decides the tight sub-class exactly.

VERDICT: half-integer Wall56 NOT closed; no counterexample. New: [P] one-side-linear => M = Gram/2 (class M0);
[P] B-linear decodability = a per-port Z4-module (covering) condition, ports independent, rows merge;
[C] tight B-linear class (v in {0,+-1}, linear; W arbitrary, any m): exact SAT encoding built; budget 56 SAT from scratch (E8 type), budget 55 UNKNOWN at 20 min.
Coordinator target (level-cut sum >= 56): [P] holds on the full linear class (7 levels x rank 8); NOT obtained beyond it (§5).

## 1. One linear side forces the Gram decoder [P + C]
Setting: M = W U^T, M∘Q = I, W integral, V = 2U integral, c_t = integral E8 root coordinates, Gamma = C G C^T (Gram of P104).
- LEMMA M0. If every row is B-linear over Z (v_k(s) = <c_s, y_k>, y_k in E8), then M = Gamma/2 on ALL cells. Same if every row is A-linear.
  Proof: Y_t := sum_k w_k(t) y_k satisfies <c_s, Y_t> = 2 delta_ts for all s in O_t (odd neighbours, t included). [C] {c_s : s in O_t} has real rank 8 for every t,
  and <c_s,c_t> = 0 on odd off-diagonal cells [C], so Y_t = c_t. Hence M(t,s) = <c_s,c_t>/2. ∎
- So one-side-linear ⊆ M0 := {decoders with M = Gamma/2} (even cells = ±1/2). A general decoder is M = Gamma/2 + E with E arbitrary on even cells.
  In M0 the mod-2 law becomes the FULL identity  Abar Bbar^T = Bmat (B(c_t,c_s), rank 8), not just "zero on odd cells".
- mod 4 version [P]: one side linear mod 4 => W V^T = Sigma·Gamma (mod 4), Sigma = diag(±1) per port.
  Uses [C]: span_F2{c_s : s in O_t} = c_t^{perp B} (7-dim) and c_t in span{c_s : s in O_t, s != t}, for all t.

## 2. B-linear decodability is a covering condition [P + C]
- B-linear mod 4: v_k(s) = <c_s, y_k> mod 4, y_k in L4 := E8/4E8. Then the decoder condition is, port by port:
  (DEC_t)  c_t ∈ span_Z4{ y_k : t ∈ D_k }   (D_k = mod-4 support of w_k).
  Proof: the odd-cell equations at port t involve only row t of W and read <c_s, Y_t> = 2 delta_ts mod 4 on O_t; by §1 this forces Y_t = ±c_t (Gc_t in coordinates).
- So for a fixed B side the rows of W are chosen INDEPENDENTLY per port; cost couples only through the supports D_k.
- Z4 is self-injective (double annihilator), so (DEC_t) <=> for every x in L4 with <x,c_t> != 0 mod 4 there is a row k with t ∈ D_k and <x,y_k> != 0 mod 4.
  x = c_s gives: the diagonal and ALL even cells are covered by rectangles D_k × S_k (in M0, M is ±1/2 there).
  [C zclauses.py] this covering form agrees with brute-force solution counting (zfeas.npy) on 20,000 random (port, mask) pairs, 0 mismatches.
- MERGING [P]: rows with y_l = ±y_k merge into one row (w_k ± w_l) without raising cost: rank Q[D ∪ D', S] <= rank Q[D,S] + rank Q[D',S].
- Prices in the class: H_{S_k} is a hyperplane or all of F2^9 ([C] rowbound: every hyperplane section spans), so price_k = dim U_k − [n_k ∈ U_k],
  U_k = span{h_t : t ∈ D_k}, n_k = normal of H_{S_k} (none if loose). Cheap rows exist (trivial decoder: 104 rows of price 1, cost 104).

## 3. Tight B-linear class [P]
- v_k ∈ {0, ±1} and linear  <=>  y_k = ±G z with z in Z16 (LINEAR56 §2: the 32 tight Z4 vectors). By merging: AT MOST 16 ROWS, one per z ∈ Z16, W arbitrary.
- Decoder <=> choose U_z ⊆ F2^9 (z ∈ Z16) such that every port t has a feasible row set inside {z : h_t ∈ U_z};
  cost = Σ_z (dim U_z − [(1,z) ∈ U_z]). Per port: 630–664 minimal feasible supports, sizes 2–4 (ztight.py);
  equivalently 144–172 minimal covering clauses of sizes 4/7/8/9 (zclauses.py).
- E8-56 lies in this class: its 8 V-columns are ±G z for 8 elements of Z16 (e8map.py), cost 56 recomputed.

## 4. Exact decision of the tight B-linear class [C, NOT decided]
- zsat.py: U_z^perp in canonical RREF (no GL symmetry), membership of h_t via XOR chains, covering clauses (§3), totalizer on Σ(u_z + nin_z) >= 144 − B.
  zdecode.py re-derives U_z, recomputes every price as rank_F2 Q[P∩U_z, S_z] and re-checks decodability against zfeas.npy (independent of the CNF).
- Controls: E8 rows forced (z56fix): SAT instantly, decoded 8×7 = 56. FROM SCRATCH, budget 56 (z56): SAT in ~8 min, decoded 8 rows × 7 = 56, all ports decodable (E8 type).
- Budget 55 (z55): UNKNOWN at 1200 s (kissat timeout). The control finished well inside the cap, so a later UNSAT would mean something, but this run is NOT a proof.
- Next: Aut(P104) (order 384, acts on Z16) symmetry breaking, or a cube split on the dimension profile of the cheapest row, then rerun 55.
- If it closes, the extension is to all y in L4 (loose rows, price = dim U): rows merge per ±y, but the pool is ~32k vectors, so it needs theory, not SAT.

## 5. Coordinator's level-cut form  Σ_l rank_F2(M_l mod 2) >= 56
- [P] LINEAR class: every rank row has (dim a, price, dim b) ∈ {(8,7,1),(8,8,0),(9,8,1),(9,9,0)} (Theorem A prices + section spanning),
  so levels l = 2..8 contain every rank row; rows with a zero odd side add 0 mod 2. Hence M_l mod 2 = Abar Bbar^T = Bmat (by §1, M0) for l = 2..8,
  rank Bmat = 8 [C], and Σ_l rank >= 7·8 = 56. Tight at E8. (Either orientation: dim a = dim H_S >= 8 for either side.)
- Beyond linear: in M0 the FULL product Abar Bbar^T is still Bmat (rank 8), but a row of price p sits in exactly p levels (those in (dim b, dim a]),
  so a level containing few rows can have rank < 8. The level form needs a per-level rank-8 law; my argument does not give it for nonlinear rows.
