# ARF (Nov 20, Opus, theory + one falsification run). Own code in this dir. venv python, <= 2 procs, threads=1.
Why not a retread: TAU48/DOUBLE56 bounded the tau-rank at the Rado minimisers. This lane asks whether a FIXED-Q
(decoder-independent) Z/4 or Z/8 invariant forces 48, and re-examines the evidence that 48 is an invariant.

VERDICT: no invariant proof of tau48 / rho_A+rho_B >= 56. The fixed-Q Z/4 invariants of P104 are computed exactly.
None of them is 48 or 56 in a way that bounds decoders. The main new finding: the "tight far from E8" evidence is explained
by a monotonicity law plus persistence of the E8 core. So it is NOT evidence that 48 is an invariant.
Falsification: 0 counterexamples (see §4).

## 1. The Z/4 form of P104 [P + C]
- Labels: 104 vectors in F2^9, Q[a,b] = a.b mod 2. [C] Every label has weight 3 (70) or 7 (34), so wt = 3 mod 4 for all of them.
  They are 104 of the 120 vectors with wt = 3 mod 4, which correspond to the E8 root lines (O+(8,2) nonsingular points; B = dot + (1.a)(1.b)).
- [P] q(x) := x^T Q x mod 4 (0/1 lift, well defined on F2^104) equals -wt(L^T x) mod 4.
  Proof: q(x) = |x| + 2 sum_{s<t} l_s.l_t. Also wt(sum l_t) = sum wt(l_t) - 2 sum_{s<t}|l_s ∧ l_t| = 3|x| + 2 sum_{s<t} l_s.l_t (mod 4). Add the two. ∎
- [P] Gauss sum: sum_x i^{q(x)} = 2^95 (1-i)^9, so |G|^2 = 2^199 and Brown(P104) = -9 = 7 mod 8. The radical of b = Q mod 2 is C^perp (dim 95), and q vanishes on it (C^perp is even, since 1 ∈ C).
  [C, inv.py] All 759 frames: the label span is 4-dim, Brown = 1. These are all odd residues mod 8, while 48 = 56 = 104 = 0 mod 8.
  So no Brown/Arf class of Q (or of its frames or sub-port-sets) can equal 48 or 56. A Z/8 class could at most enter as a parity obstruction, and none is visible.
- [P, checked inv.py/fixedfac.py] FIXED mod-4 factorisation: Q = L L^T + 2 Pi^T Pi (mod 4). Here Pi: F2^104 -> F2^36, e_t -> (l_ti l_tj)_{i<j}.
  This uses (w mod 2) = w - 2 C(w,2) (mod 4) with w = |l_s ∧ l_t|. [C] rank Pi = 28 (the pure-quadratic image P2), R2 = R1 + P2 (36 = 9 + 28 - 1).
  The R2 pairing has a 24-dim radical (Rad2). The universal tau-form on C^perp has rank 26 (TAU).
  Numerology only: 56 = 2 rank Pi, 48 = 2 dim Rad2. No inequality linking them to decoders was found (§3).
- The same identity, applied to any factorisation Q[D_k,S_k] = Phi^T Psi, re-derives TAU §1 in one line [P].
  If u, v are zero-sum (Phi u = 0, Psi v = 0 mod 2), then u^T Q v / 2 = <Lambda(Phi u-cols), Lambda(Psi v-cols)> mod 2, with Lambda the pair map. With the fixed (label) factorisation it gives:
  [P] for x ⊥ U^full := sum_k a_k o R1 and y ⊥ V^full, x.y = x^T M y with M = sum_k D_{a_k} E2 D_{b_k} and E2 = Pi^T Pi (rank 28). [C] holds on E8, g_2_4, g_3_8.
  This is weaker than the isotropic-pair lemma: U^full ⊋ U, with dim U^full = dim U + 8 on all three decoders.

## 2. Monotone form of the target [P] and why "tight far from E8" is not evidence [P + C]
- Let f(U,V) := dim U + dim V - rank<U,V> (= n - tau-rank in the J = J' = all case). [P] f(U,V) = max{dim U0 + dim V0 : U0 ⊆ U, V0 ⊆ V, U0 ⊥ V0}.
  Proof: pick bases in which the pairing is [I_r 0; 0 0]. Keep the radicals, and from each of the r hyperbolic pairs keep one side. That gives dim U + dim V - r. Conversely, if U0 ⊥ V0 then rank<U,V> <= rank<U,V0> + (dim V - dim V0) <= (dim U - dim U0) + (dim V - dim V0), because U0 is in the left kernel of the pairing on U × V0. ∎
  So f is MONOTONE in U and in V. Since U = sum_s R'_s and V = sum_t R_t, every sub-family of ports gives a lower bound.
  So tau48 (J = all case) ⟺ every valid decoder carries ORTHOGONAL sub-spans U0 ⊆ U, V0 ⊆ V with dim U0 + dim V0 >= 56. E8: U0 = U, V0 = V (28 + 28).
- [C core.py] The tight Gibbs decoder g_2_4 (C = 86, rho = 77, tau-rank 48) has U ⊇ U_E8 and V ⊇ V_E8 exactly (28/28 of 28).
  So f(g_2_4) >= f(U_E8, V_E8) = 56 by monotonicity alone. Its tightness is the E8 core surviving the walk plus extra dimensions paid for 1:1 by rank<U,V>.
  It is not a second extremal point. The same holds for the E8-descended walks that "sit at 48".
  The one near-tight point where the core is partly lost, g_3_8 (U∩U_E8 = 24, V∩V_E8 = 27), has f = 57, not 56.
  Random-factorisation walks never get below f = 60 (TAU: max tau 44). Revised reading: the evidence is "E8 is a strict, robust local minimum of f". It is not "48 is an invariant".
- [C stats.py] On E8 and both Gibbs decoders: U∩R2 = V∩R2 = 28 (E8 core), U∩P2 = V∩P2 = 20, U∩Rad2 = V∩Rad2 = 22, (U+V)∩R2 = 34.
  For linear decoders (a_k, b_k ∈ R1), U, V ⊆ R2 [P: product of two linear functions]. So for them f >= 56 is a question inside the 36-dim R2 (12-dim nondegenerate part, 24-dim radical).
  That is the cleanest open sub-case (finite, Q-fixed). Not done.

## 3. The "n - (max tau-isotropic)" route [negative]
- In the J = all case the target is the plain pairing x.y on U^perp × V^perp (it equals the tau-form by lemma (a)). A fixed-Q bound would need a fixed pair of spaces carrying all U^perp mod V. [C]
  The E8 core lives in R2 but nonlinear decoders leave R2 (g_3_8 loses 4/1 dims). Xs ⊄ R3 in general (TAU). The fixed factorisation only controls (U^full)^perp, which is 8 dims too small.
  No decoder-independent space of pairing rank 48 contains the data. The cancellation 160 -> 48 is a property of the E8 core, not of Q.

- Decoder-level Arf test [C theta.py]. On Z = (U+V)^perp set sigma(x) = sum_k (x o w_k)^T Q (x o v_k) mod 8 (lifts in 0..3). Validity gives sigma = 2|x| mod 4 there, so theta = (sigma - 2|x|)/4 mod 2.
  theta is a genuine quadratic form [C, 200 random triples + full expansion check].
  - E8: dim Z = 70, theta ≡ 0 (polar rank 0, Arf 0).
  - g_2_4: dim Z = 49, polar rank 18, and theta is nonzero on the radical, so the Gauss sum is 0 and there is no Arf class.
  - g_3_8: dim Z = 29, polar rank 28, Arf 0.
  So no constant nonzero Arf/Brown class is carried along decoders. There is nothing to "pay for".

## 4. Falsification [C] (descent.py, annealed heat-bath over exact Gibbs port resamples, 6 starts each: E8+2/4/8 empty rows, randfact m = 10/12/16)
- Two 50-min runs (threads=1, about 1.7 CPU-h), mode C (seed 1) and mode rho (seed 2). The logs are desc_C.log and desc_rho.log.
- [C] 0 violations: no valid decoder with C < 56, and no certified rho_A + rho_B < 56. Best C = 56 (the E8 orbit). Best rho_A + rho_B = 56 (Rado ub 28 + 28).
- tau-rank at Rado-exact checkpoints: mode C 67 points, max 48 (hist 44:15, 48:52); mode rho 7 points, max 48 (44:3, 48:4). Over 0 points did tau-rank exceed 48.
- CAVEAT (weak sampler): every start ended at its own value. E8+extra rows stays at 56 in the gauge orbit, even at T = 2. Randfact starts stay at 72 = 36 + 36 (rare excursions to 77/78 are rejected).
  Heat-bath over single-port resamples does not cross the barriers. The run is a robustness check of E8's local minimality, not a global search.
  A stronger falsifier needs multi-port or row-level moves. descent.py has an extra mode 'f' (minimise f directly), which was not run (CPU cap).

FILES: inv.py (Z/4 form, Gauss sums, frames, Pi), stats.py (subspace stats vs R1/P2/R2/Rad2), core.py (E8-core persistence), fixedfac.py (fixed mod-4 factorisation),
descent.py (falsification; modes C / rho / f), desc_*.log, best_*_{W,V}.npy.
