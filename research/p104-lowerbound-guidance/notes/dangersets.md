# DANGERSETS DS (Nov 20, Opus, theory + exact). Own code in this dir (ds_lib.py, ds_rank.py, s1..s10). venv python, 1 thread, light. No Lean, no advisor, no push.
Differs from PORTGEN: PG only listed the dangerous port sets with quoted/sampled c; this lane computes their h, exact decoders and class floors, and proves the h-monotonicity PG had only computed.
Thresholds from PG: need c >= rho_eq(h)*n, rho_eq(7) = .64059, rho_eq(8) = .58929, rho_eq(9) = 7/13 (U k->inf, X+HS).

## (i) half-spin 64 and E7+A1
| set | n | h [C] | need | tau-trivial? [C] | best exact decoder [C] | Gram-class floor | general-model floor |
|---|---|---|---|---|---|---|---|
| half-spin 64 (P120 - D8) | 64 | 8 | c >= 38 (37.71) | NO (defect: 3x9 even block, sum = 2 mod 4) | **48** (orthoframe D8 design, 8 terms rho 6; quarters) | **48 [P from C]** => m_Gram = 48 exactly, rhobar .750 | 2n/(h+1) = 15 (halves only) [P ADICWALL]; quarters: none |
| E7+A1 | 64 | **7** (PG had <= 8) | c >= 41 (41.0) | NO | 50 (E7 49 + 1) | **>= 49 [P from C]** | C(E7) <= C(E7+A1) <= C(E7)+1 [P] |
| E7 | 63 | 7 | c >= 41 (40.36) | NO | 49 | **49 [P from C]** (= #2228 without the dense-pairing hypothesis, Gram class) | as P104: open |
| E7 - 7-frame | 56 | 7 | c >= 36 (35.9) | - | 42 [Q UNITS] | **42 [P from C]** (float rank for the M check) | open |
Verdict (i): all safe in the Gram class with wide margins (48 vs 38; 49 vs 41; 42 vs 36). None is LOUD. In the general model they sit at the same level as P104 itself (Wall56 is the owner-accepted premise there); here the premise would be PORTWALL(8) at 48/64 and PORTWALL(7) at 49/63.

Proofs / computations:
- h = rank_F2(J + G) [C s1_basic.py]. E7+A1: the A1 line is orthogonal to all of E7, so its label adds nothing new mod 2: h = 7. So E7+A1 needs rho_eq(7), not rho_eq(8).
- tau-triviality [C s1]: random even pairs, about half have tau = 1 on all three sets; the clique theorem gives nothing here. Expected: the exact 48 decoder has quarters, so the half-integer lemmas would not bind it anyway.
- Half-spin exact decoder [C s7_hsdesign.py]: terms u_k = w_k = r_k over the orthogonal D8 frame {e1+-e2, e3+-e4, e5+-e6, e7+-e8}; O = Gram exactly, so N o O = I on the mask; each term has |A| = |B| = 32 (the half-spin lines not orthogonal to r_k) and F2 rank 6. Cost 48 = 3/4 per port. Improves the quoted design <= 54 (OMEGA48 table, sampled).
- Half-spin Gram floor [P from C s2_flats.py, s3_gramfloor.py, s4_mforced.py, s6_hsflats.py]:
  1. M is forced: the linear system l^T M l = l.l, l^T M l' = 0 on orthogonal pairs has rank 64 [C exact, sympy] => sum_k u_k w_k^T = I_8 => >= 8 terms.
  2. For any u != 0, u^perp ∩ P lies in a hyperplane flat F of the half-spin line matroid, so A(u) ⊇ P \ F, and rank is monotone under submatrices. Every hyperplane flat is spanned by roots, so its normal is a fundamental-coweight image of norm <= 30: all 3,721,680 E8 vectors of norm <= 30 were enumerated; 268,712 flats.
  3. Pair ranks rank Q[P\F1, P\F2] over all flat pairs (cached by row spaces; exact F2): min 6. rank 6 only when both F1, F2 are the 32-line flats r^perp for D8 roots r (the only complements with a 7-dim label span).
  4. So c >= 8 x 6 = 48 for every Gram-class decoder, and the D8 design attains it.
- E7 / E7+A1 [P from C s5_e7floor.py]: 8,821 rank-6 flats in R^7 (all 7 parabolic types: 36, 30, 21 (x2 types), 16, 13, 10); every complement spans the full 7-dim label space, so every term has rho >= 7; M is unique on R^7 (constraint rank 49 + 15 free a0-directions), so >= 7 terms: c(E7) >= 49. E7+A1: restriction gives c >= 49 in both models (C(K) <= C(L) for K ⊆ L); padding gives <= 50.
- E7 - 7-frame [C s10_e7frame.py]: h = 7; rank-6 flats: pair ranks min 6 => c >= 7 x 6 = 42 = design.

## (ii) E8 subsets with v <= 95 at h = 9
- [P, general model] deletion law (T0, re-stated): C(L) - |L\K| <= C(K) <= C(L). With C(P120) >= 72 this gives c >= v - 48, which beats 7v/13 only for v >= 104. Port deletion saves at most 1 per port; the danger is a run of deletions each saving close to 1 after P104 (P104 sits exactly on 7/13).
- [P Gram class, OMEGA48 T3] v >= 96 safe; nothing beyond that at v <= 95 except the 32..36 window, which gives only c >= 40 (below 7v/13 = 45..47, so T3's window does NOT cover it).
- [C search, Gram class, s9_subset_sa.py; logs s9_v95.log, s9_v70.log] SA over subsets P (toggle moves, objective 13c - 7v, exact F2 ranks) for 6 fixed designs (P104's wB pairs, orthoframe, 4 random root bases + dual): every run is pushed UP to the v cap. Best at v <= 95: wB 56/95 = .5895, random designs .62-.65, frame .674. At v = 70: c stays 56-64 (ratio >= .80). Deleting ports below P104 does not lower c in any tested design (the T3 plateau continues). No subset below 7/13. Scope: fixed designs, not a per-subset design optimisation; evidence, not a floor.
- half-spin + D8 lines under the frame design (s8_hsplus.py) [C]: ratio never below .6000 (v = 65..120, h = 9 from v = 65); minimum at v <= 95 is .7158.

## (iii) h-monotonicity of the ceiling [P]
Rung (PG §1): f(s) = c A_u(s) - 2 rhobar psi_h(s) - eta H_u(s) - sigma p_u(s), u = h-1, A_u = (2u+1)^s - 2u^s, psi_h = (u+1)^s - u^s, H_u = 1 + (u-1)^s - u^s, p_u = (u - u^s)/(u-1); kappa_ceil = 1 - s*, s* the first zero on (0,1].
THEOREM. For c in [1, 2] (Theorem U, k >= 2), eta >= 0, sigma >= 0, 0 <= rhobar < c, u >= 2 real: kappa_ceil is strictly decreasing in h. Hence rho_eq(h) is non-increasing in h.
Proof. Put g(x) = x^(s-1), strictly decreasing for s in (0,1). Differentiate in u:
  dA/du = 2s[g(2u+1) - g(u)] = -2s D1, dpsi/du = s[g(u+1) - g(u)] = -s D2, dH/du = s[g(u-1) - g(u)] = s D3,
  with D1 = g(u) - g(2u+1) > D2 = g(u) - g(u+1) > 0 (since 2u+1 > u+1) and D3 > 0.
  dp/du = [(1-s)u^s + s u^(s-1) - 1]/(u-1)^2 >= 0 by weighted AM-GM ((1-s)u^s + s u^(s-1) >= u^(s(1-s) + s(s-1)) = 1).
  So df/du = -s[2c D1 - 2 rhobar D2 + eta D3] - sigma dp/du < 0, because rhobar < c and D2 < D1.
  f(0) = -c - eta - sigma < 0. If u < u', then f(s; u') < f(s; u) < 0 for every s < s*(u), and f(s*(u); u') < 0, so s*(u') > s*(u) (when s*(u) < 1; when rhobar >= c the ceiling is 0 for every h). ∎
- Scope: the U-family caller (prefactor c = 2 - 2/k) with the PG native terms. It does not cover the #7113-shaped caller model (PG pg3, MODEL), which has its own radices; there monotonicity stays [C].
- Consequence: PORTWALL(h) need only be checked against a decreasing threshold; any port set with lower h must pay more per port (PG's "smaller label spaces need more" is now a theorem in this family).

## Files
ds_lib.py (E8 lines, Q = J+G mod 2, F2 rank), ds_rank.py (row-space-cached pair ranks), s1_basic.py (h, tau search), s2_flats.py (flat census, flats.pkl), s3_gramfloor.py, s4_mforced.py, s5_e7floor.py, s6_hsflats.py, s7_hsdesign.py, s8_hsplus.py, s9_subset_sa.py, s10_e7frame.py.
