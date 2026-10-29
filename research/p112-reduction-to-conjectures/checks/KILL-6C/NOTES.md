# KILL-6C — six-heavy d=8 rows by a multiplicity-aware line count (theory route; KILL-6B's cover searches untouched)
STATE: KILL-6C: DONE. All 9 target rows KILLED in every open scenario (303 β1/α/bump5/bump6, 315 α/bump4, 400 401 402 409 411 417 425 ClassI).
  Impl A = cert.py (HiGHS dual LP -> rational Farkas certs, certs.json); impl B = verB.py (pure Fraction, no scipy, enumerates all 2^p-1 M) -> ALL CERTS OK.
  Closed-form Lemma TC (hand proof, uses only G2) independently kills 303 β1/α/bump5, 400, 401, 402, 409. Controls: ctl.py, ctl2.py. Not the PS analogue (not needed).
## Setting / premises (all already in the project)
CARRIER §2 Circuit Lemma, E8 version (ClassI and the s=6 sub-cases; α: plus the one extra line f): h: R -> K^8 injective, dim R = d, and for every c in R
Off_E(h(c)) ⊆ ∪_{j∈supp c} Λ_E(F_j), |Λ_E(F_j)| ≤ g(w_j) (g = 1,2,4,8,12,20,36,64). G2 (PROVEN): a k-dim subspace contains ≤ 1,3,6 root lines (k=1,2,3).
Scenario modelling exactly as SIXHEAVY grrc.py (β1 = ClassI weights; α = one excused line; bump x = one piece of weight x raised to x+1); b3B n/a (303 has no 7; 315 only α/bump4 open).
## Lemma LF (line form; = Lemma F, SEVEN S1). M_t := {j : t ∈ Λ_E(F_j)}. If c_j = 0 ∀ j∈M_t then t ∉ Off(h(c)); so ⟨·,r_t⟩ vanishes on ∩_{j∈M_t} ker φ_j,
i.e. r_t ∈ span{φ_j : j∈M_t} (φ_j = c_j∘h^{-1}). If d = 8 then V = h(R) = K^8, so M_t ≠ ∅ for every constrained line (all 120; 119 in α).
## Lemma CNT (d = 8). (i) #{t : M_t ⊆ K} ≤ N(|K|) for |K| ≤ 3 (lines in span φ_K, G2); (ii) Σ_t |M_t| = Σ_j |Λ_E(F_j)| ≤ Σ_j g(w_j).
Any y_K ≥ 0 (|K|≤3), z_j ≥ 0 with Σ_{K⊇M} y_K + Σ_{j∈M} z_j ≥ 1 for all nonempty M gives NL ≤ Σ_t(...) ≤ Σ y_K N(|K|) + Σ z_j g(w_j). If RHS < NL: contradiction.
## Lemma TC (closed form, symmetric). a, b := #lines with |M_t| = 1, 2. Double count over triples T: C(p−1,2)a + (p−2)b ≤ 6·C(p,3); and a+b ≤ NL.
Then Σ_t|M_t| ≥ 3NL − (2a+b) ≥ (2(p−2)NL − 2p(p−1))/(p−3)  [multipliers 2/((p−2)(p−3)) and (p−5)/(p−3)] = 237.33 (p=12), 235.11 (p=12, α),
232.8 (p=13), 228.73 (p=14). Kill iff Σg < bound: 303 β1 224, α 224, bump5 232; 400 222 (p=14); 401 222, 402 225 (p=13); 409 232. (verB.py prints it.)
## Weighted certificates (cells with Σg ≥ 237: 303 bump6 240, 315 α 252 / bump4 256, 411 240, 417 248, 425 256) — certs.json, |K| ≤ 3 only.
Cert RHS (must be < NL): 303 β1 113.35, α 113.35, bump5 117.35, bump6 114.23; 315 α 117.23 (<119), bump4 119.57; 400 112.86; 401 112.54; 402 114.35;
409 117.35; 411 114.23; 417 117.93; 425 119.57. min-cover ≥ 1 exactly for all (verB). Tightest: 315 bump4 / 425 (margin 0.43 line).
## Controls (own E8 build, ctl.py / ctl2.py)
- G2 recomputed: N1 = 1, N2 = 3 (all pairs), N3 = 6 (1/9 of triples).
- Real configuration (12 roots as φ, M_t = a minimum spanning subset): 0 violations of (i), Σ|M_t| = 367 ≥ 237.33; LP with its caps: FEAS (constraints don't exclude real geometry).
- Non-vacuity: 12 pieces, uniform cap 18/19 infeasible, cap 20 ([6^12], Σ 240) FEAS; 411 with one extra 6->7 FEAS. So the count bites exactly at these rows' budgets.
## Side note (not claimed): TC alone kills 18 of the 339 d=8 ledger rows in ClassI (most already killed elsewhere) — free second route for the consolidated PR.
Extension (not pursued): d < 8 works with N(|K|) replaced by N(|K| + 8 − d) incl. K = ∅ — needs N(k) for k ≥ 4 (classical parabolic counts, as in the README count lemma).
Files: lp.py (size-only LP), lpfull.py (|K|≤7 LP, first pass), cert.py (impl A), certs.json, verB.py (impl B), ctl.py, ctl2.py, ctl_caps.txt.
Bump validity: a drop-1 member has support ⊆ Λ_E(F_j) ∪ {one frame line} ⊆ Λ_E(F_j ⊕ ⟨label f⟩), a (w+1)-flat, so 'bump x -> x+1' is a valid relaxation.
Rerun: `python3 -I verB.py` (last line ALL CERTS OK; saved verB.out); `../../venv/bin/python -I ctl2.py` (saved ctl2.out); `../../venv/bin/python -I cert.py` regenerates certs.json.
## Follow-up (coordinator): seven-heavy 579, 596–601 and the 7 prior-only rows 381 384 576 577 578 580 581 — route does NOT kill (LP FEASIBLE)
cert2.py (G2 only, |K|+8−d ≤ 3, empty K/M included so d=7 b3B works): every cell FEASIBLE (dual 127–144 ≥ NL). cert2k7.py (adds classical N4..N7 =
12,20,36,63, same as the README count lemma): still FEASIBLE: 579 (121.1), 596–601 (131.8–136.8), 576 (120.0, boundary), 577 121, 578 127, 580 122.7, 581 127.3;
381: β1/α/bump1/bump7/b3B infeasible but bump5 (121) and bump6 (120) FEASIBLE; 384: β1/bump7/b3B infeasible but α/bump5/bump6 FEASIBLE. No row closes,
so no impl-B verification was run for the partial cells. Why it fails: 7-pieces (g=36) make Σg 293–346, well above the ~237 threshold for p ≈ 12.
