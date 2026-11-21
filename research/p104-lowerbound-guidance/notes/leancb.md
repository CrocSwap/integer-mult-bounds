# LEANCB (Sonnet, Nov 20): hMu removed from P104 linear 56 bound [P, kernel-checked]
Axioms of every headline theorem: propext, Classical.choice, Quot.sound (no sorry / native_decide). Built only via LEANCERT/runlean.sh, peak <= 3.0 GB.
Files (lean/decoder-duality/Nov15/), build order:
- LinCB.lean: `LinCB.cb_exists`: A P : m x n over any field, det(A^T P) != 0 => injective f : Fin n -> rows with det A_f != 0 and det P_f != 0. Own proof of the existence form of Cauchy-Binet (det(A^T P) = sum_f prod P(f i,i) det A_f, group injective f by image, fibre = orbit f0 o tau sums to det A_f0 det P_f0).
- LinKbarBase/C0..C3/Fin: `kern_B`: any K over F2 with c_t^T K c_s = 0 on all B-orthogonal label pairs has K i j = B i j * K 0 1 (63 explicit cells + 64 explicit combinations, kernel `decide`; data from gen.py, kern.json). Also dep4: labels 0,6,16,95 pairwise B-orthogonal, sum 0.
- LinP104Free.lean: `Z4Lin` (w_k(t) = x_k.ct_t, v_k(t) = y_k.ct_t mod 4 for integer vectors x_k,y_k and ANY integer lift ct of the labels) and
  `P104.p104_linear_cost_ge_free`: Z4Lin + exact decoder identity => 56 <= C. No hMu.
  Proof: Kbar = sum xbar ybar^T obeys the mod-2 law on odd cells => Kbar in {0,B}; Kbar = 0 gives K = 2Z, Z-Gram = delta on odd cells, contradicted by the dependent orthogonal quadruple; so Kbar = B; N = sum alpha_k p_k^T = Kbar Binv^T has det != 0; cb_exists gives the 8 rows; old `p104_linear_cost_ge` finishes.
- LinP104FreeInst*.lean: non-vacuity: honest E8 decoder x_k = e_k, y_k = G e_k (w = ct[k], v = (G ct)[k]), ct = e8base C rows 0..103; Z4Lin, exact identity on all 104^2 cells and hct (ct mod 2 = lab, so the embedded masks ARE the E8 root coordinates mod 2) certified; `nonvac_instance`.
Remarks:
1. Definition matters: parity-linear alone (LinSetup) does NOT give Kbar != 0 (all-even rows w = 2u have alpha = 0). K != 0 uses the Z4 lift; this is the "Z4-linear" class of LINEAR.md, now explicit. The old hypothesis hMu is derived; the old theorem (hMu form) is kept.
2. Only the mod-2 labels and Qlab pattern matter; ct is arbitrary integer lift (stronger than E8 coords).
3. Still not certified: bmMasks/Binv are the E8 Gram mod 2 (Lean checks Q = 1 + B on labels.txt and the instance's ct/lab agreement, not Gram = E8 Cartan). Theorem A (7+ per row), f >= 56: not attempted.
