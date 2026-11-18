# LemmaW.lean: BORROW Lemma W (R12 §2) in the caller stage model 
Kernel-only, no sorry/native_decide, all axioms [propext, Classical.choice, Quot.sound]; 9 s / 2.0 GB. Imports Nov15.CallerBorrow (model: `unitM`, `pp`, `pm`).
## Model
Units T_s = 1 - 2 x_s y_s^T; prefix `pp s = T_{s-1}..T_0`. Cut prefix A = `pp a`; thins u_j = index a+j (j<k); stage R_i at index a+k with mask m = m_R; Q_{j-1} = `pp (a+j)`; pulled-back covector w_j = `y (a+j) ᵥ* pp (a+j)`; borrowed role r with `¬ m r`.
## Proved
- `pp_window_entry`: pp(a+k)[r,c] = A[r,c] - 2 Σ_j x_{a+j}[r] w_j[c] (pure algebra).
- `lemmaW_defect` (exact; only "prefix before R commutes with m"): for r ∉ m, c ∈ m: 2 Σ_j x_{a+j}[r] w_j[c] = A[r,c].
- `lemmaW` / `lemmaW_vec` (i): if also A commutes with m ("R untouched before") and 2 ≠ 0: Σ_j x_{a+j}[r] w_j|_m = 0.
- `lemmaW_unique`: if exactly one thin has x[r] ≠ 0, its w_j vanishes on all of m.
- `single_thin_forces` (ii): k = 1, units invertible, x[r] ≠ 0 => y vanishes on m_R (`InMask ¬m`). So a thin with ANY support of y on m_R cannot borrow alone; needs >= 2 thins with cancelling contributions.
## Verdict: paper statement TRUE, with one sharpening (not false)
R12 says a single toucher "needs its pulled-back covector to vanish on all of m_R": correct (`lemmaW_unique`). The gloss "impossible with a single thin" holds exactly when the thin's y meets m_R (pm y ≠ 0, with A invertible and commuting: w|_m = (pm y)^T A, zero iff pm y = 0). A single thin with y supported OFF m_R and x on r is consistent with Lemma W (Lean `example` in the file: Fin 2, m={0}, x=y=e_1, both prefixes commute). Hypothesis list: A commutes with m (else the defect term A[r,c] appears, `lemmaW_defect`), char ≠ 2.
Not formalised: "≥2 cancelling thins is achievable" (only the necessary condition), the rank/Jacobian rigidity numerics of R12 §2.
