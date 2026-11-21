# L2TEST (Nov 20, Sonnet, exact compute). Code: base.py t1.py t1b.py lm.py t2*.py f2sat.py (task 1), netlib.py e8net.py pick.py run1-4.py (task 2). Logs run34.log run4.log.
## 1. L2 min-rank table (pattern: M_tt=1, M_pq=0 on odd pairs, even cells free; section = ports with label in u^perp)
Bounds: omega(odd graph on section) <= minrank (any field); minrank_Q <= rank_Q(E8 Gram on section) (G/2 realises it). [C exact]
- P104 (511 normals): 12 sections (44 ports) omega=8=E8 rank => minrank 8 exact; 95 (48 ports, even normals) 8; 56 (52) 8; 199 (56) 8; 12 (60) 8.
  16 sections (52 ports) omega=7=rank 7 => minrank EXACTLY 7 (<8!).  120 sections (all 104 port hyperplanes q_t^perp, 48 ports; plus 16 of the 52-port ones): omega=4, E8 rank 8: gap.
- Q96: ~24 sections omega=7=rank7 (min-rank 7 exact); 120 sections omega=4, rank 8 (gap); rest 8 exact.
- gap sections, numerics (own LM solver, 25 restarts): r=8 found (resid 1e-14), r<=7 never (stuck at resid ~1) => minrank_Q = 8 [numeric, NOT proved]. F2 (kissat, section u=11, 48 ports): r=8 SAT (0.2s), r=7 UNKNOWN at 300 s. Exact lower bound beyond omega=4 not obtained (determinant arguments cannot beat the clique bound: a minor is constant iff its rows form an odd clique).
- Verdict L2: "min-rank >= 8 on every hyperplane section" is FALSE (min 7, exact, 16 P104 / ~24 Q96 sections). Sections with rank 7 are E7-type 7-dim subspaces of the E8 frame.
## 2. Network tests (exact mod p=2^31-1; decoder condition + legality asserted in code)
Evaluator netlib.py: D, |C_l|, YC level sum, DX (NOGAIN's M*_l by 3-state walk DP), loss=sum_{l=2..8}(8-rank M*_l)+, junk=sum_l(|C_l|-rank M*_l).
- Validation: LR (lwcx) reproduced: D 104/112, YC 0, DX 16, loss 48, junk 88/96. E8 hubs (gather dim 8, b=1): D=YC=DX=56, junk 0 (kernel set picked so all gathers are 8-dim; pick.py).
- Family A (E8 rows split gather->deposit at random chart dim k=1..8; 80 nets, Q96+P104): all D=YC=DX=56, junk 0. No violation.
- Family B (hub gathers inside random chart A_h dim 2..8, rest via shared single-port gatherers; 140 nets): min D 116, min YC 12, min DX 28, 0 violations.
- Family C (hub chart A_h, rest via coset-group gatherers with b=a cap A_h; 140 nets): min D 77, min YC 16, min DX 26, 0 violations.
- RANK >= 9: LR + free extra hubs (a=b=0) realising a Delta supported on EVEN cells only: rank M = 10,18,28,48,96 (Q96), D=104 always:
  JUNK 86,78,68,48,0 vs loss 48 => JUNK-PAYS VIOLATED once rank M* >= 49 (rank 96: loss 48 > junk 0). Q96 and P104 (rank 104, D=112). [C exact, decoder+legality asserted]
  Cause: rank M*_1 is inflated by free even-cell content, so |C_1| - rank M*_1 shrinks to 0. D=104 >= 56, so NET-D56 is untouched; the inequality as stated is false.
