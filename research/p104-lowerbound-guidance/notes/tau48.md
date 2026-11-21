# TAU48 (Nov 20, Opus, theory + exact checks). Own code in this dir. venv python, <= 2 procs, threads=1.
Why this is not a retread: DOUBLE56 stated tau48 but never broke the tau-form down by row and never tested it off the linear/E8 families. Here: the per-row structure, a new nonlinear decoder generator, and tightness far from E8.

VERDICT: tau48 is NOT proved. No counterexample to tau48 or to rho_A+rho_B >= 56. Three obstructions [P/C] and one new tight family.

## 1. The per-row tau-forms are bilinear but cannot be summed [P + C]
- [P] For x in Xs, y in Ys, set T_k(x,y) = tau(Q[x o a_k, y o b_k]). Each T_k is bilinear on Xs x Ys (it is not just their sum).
  Proof: u⊕u' has entry sum s(u)+s(u')-2 s(u∩u',v). Every row of Q[u,v] is even, so s(u∩u',v) is even. Hence tau is additive in u, and by symmetry in v.
- [P] With M = Q[J∩D_k, J'∩S_k] = Phi^T Psi of F2-rank r: Xs o a_k lies in leftker M and Ys o b_k lies in rightker M.
  T_k factors through the zero-sum subsets of F2^r: T(A,B) = #{(a,b) in A×B : <a,b> = 1}/2 = sum_{i<j} lambda_ij(A) mu_ij(B). So rank T_k <= C(r_k, 2).
- [C tk.py] At E8: rank T_k = 20 for each of the 8 rows (C(7,2) = 21). The sum of the ranks is 160, but rank X| = 48.
  So no row-additive tau bound can give 48. The cancellation (160 -> 48) is global, the same lesson as the ORBITLP filter.

## 2. tau48 is strictly stronger than the conjecture, and its "sharpenings" are trivial [P + C]
- In the J = J' = all case: tau-rank = n - dimU - dimV + rank<U,V>. So tau48 <=> dimU + dim(V ∩ U^perp) >= 56 (U, V must be nearly orthogonal).
  The conjecture only needs dimU + dimV >= 56.
- The lemma bound n - tau-rank is loose off E8. [C] Transvection neighbours: 56 vs rho = 58. Random factorisations: 60 vs 72. Gibbs decoders (§3): 56 vs 77 and 57 vs 98.
- Remark [P]: the map x -> x^T(I+X) sends U^perp into V. Counting its kernel gives rho_A+rho_B >= dimU + rank(Y^T|U^perp).
  This is dominated by the trivial rho_A + rank Y (y = w' in the master form). So the only non-trivial content of the isotropic-pair lemma is the tau-rank itself.

## 3. New decoder generator, and tightness far from E8 [C]
- gibbs.py: an EXACT validity-preserving move. Pick a port t and resample W[t] (or V[t]) from {w in Z4^m : w·V[p] = 2δ_tp mod 4 for all p with Q[t,p] = 1}.
  This is solved mod 2, then the carry is solved mod 2. The moves produce NONLINEAR decoders (up to 38 columns outside the label code C). DOUBLE56 had only linear decoders and completions.
- Walks: E8-56 + 4/8/12 empty rows, and random factorisations with m = 12/16. 3000+3000+800+400 steps. Every Rado-exact point (greedy Rado ub = GF(2^16) rank) has tau-rank <= 48.
  Max on E8-descended walks: 48. Max on random-factorisation walks: 44. 0 violations.
- TIGHT FAR FROM E8: g_W_2_4.npy / g_V_2_4.npy has C = 86, rho = 31 + 46 = 77 (Rado-exact), dims 73/58, tau-rank = 48, and dimU + dimV - rank<U,V> = 56 exactly.
  Most E8-descended points sit at exactly 48 (one dropped to 47), with U, V far from isotropic (rank<U,V> = 21, 41).
  Consequence: any proof of tau48 must be exactly tight on decoders with rho up to ~98. Arguments that use closeness to E8, linearity (a_k in C), or slack in rho cannot work.
- Structure [C uvstruct.py, probe.py]: at E8, U ≠ V (dim U∩V = 22), both 28-dim inside R(2) (the quadratic functions, 36-dim) and mutually orthogonal. Xs ⊆ R(3) at E8 but NOT in general (3_8: dim(Xs∩R3) = 48 of 52). No fixed canonical space carries the 48.
  Universal single-row tau-form of Q on C^perp x C^perp has rank 26 (univ.py), not 48.

## 4. Status of the chain / what is needed
- Wall56 (half-integer) ⇐ rho_A+rho_B >= 56 ⇐ tau48. tau48 remains [CONJ] with strong evidence (0 violations; tight on a positive-dimensional-looking family, not just E8).
- The invariant to explain: along E8-descended walks dimU + dim(V∩U^perp) is pinned at 56. Under one port move, U changes only in coordinate t and V only through R_t.
  So a POTENTIAL proof is plausible: show that a single-port resample cannot lower dimU + dim(V∩U^perp) below 56 unless rho jumps. That needs an invariant of the (Z4-gauge) decoder class. The candidate is the Arf/Brown-type class of the tau-refinement. Not done.
- Chart-closed: the isotropic-pair lemma (a), (c) and the §2 remark use only: rows of Y in R_t, columns of Z in R'_s, I+X = Y+Z, and the Rado formula. So they hold verbatim for chart-closed families (NETDOUBLE). Part (b) (the tau formula) uses the generators a_k∘Q_s and M̄∘Q = 0, so it holds for chart-closed families only if the closed generators keep the even-block property. Not checked.
- den > 2 (scope only): over Z/8 with M ≡ 4I, the HC identity splits into two carry levels: X1 + Y + Z = 0 (no I) and I = X2 + carry(level 1) + Y2 + Z2 + E, with E = Σ diag(w')Q diag(v').
  Lemma (a) then needs E controlled. E's rows and columns lie in neither U nor V. tau must also be replaced by tau_4 = (entry sum)/4 mod 2 on blocks with entry sums divisible by 4 (a Z/8 / Brown-level refinement). Three-level Rado spaces are needed. Not attempted.
FILES: tk.py (per-row ranks), fam.py/fam2.py (families), kphi.py/kchk.py (§2 remark bounds), gibbs.py/gibbs2.py/gibbs3.py (exact Gibbs moves), uvstruct.py, canon.py, probe.py, univ.py, g_*.npy (Gibbs decoders), g2_*.log, g3_*.log.
