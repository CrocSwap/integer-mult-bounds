# Nov15/SpecLemmaU.lean 
Formalises survivor #0's kill steps (internal notes + AUDIT.md). Kernel-only: no sorry, no native_decide; 9 `#print axioms` all [propext, Classical.choice, Quot.sound]; 21 s / 2.05 GB. Paper statements are TRUE as written (no counterexample needed).

## (1) LEMMA U (auditor's derivation, not RB4 `rank_ge`)
- `lemmaU` (abstract; field, 2 != 0, finite-dim W): V <= F1, codim F1 = c, im(P-1) in V, D = -1 mod F1 (D w + w in F1), P (Lam w) = D w (Lam = P^-1 D). Then rank(Lam-1) >= c, and rank = c => Lam^2 = 1. Uses neither dim V <= 4 nor invertibility of P (only Fix(Lam) <= F1 and Lam = -1 mod F1 at equality). `fix_le`, `lam_neg_mod` are the two steps.
- `lemmaU_mat` (RB6 coordinates Fin 4 + iota, C4 = e1..e4, F1 = {C4 coords = 0}; D = `Dm d` with d^2 = 1; P invertible; C4-coordinates of (P-1)w vanish "proj_C4 X0 = 0"): 4 <= rank(P^-1 D - 1), and rank = 4 => (P^-1 D)^2 = 1.
- `lemmaU_mat_T` (transpose case: C4-columns of P-1 vanish, "Y0 vanishes on C4"): same conclusions for P^-1 D, via rank(D-P^T) = rank(D-P) and (P^-T D)^2 = 1 <=> (P^-1 D)^2 = 1.
## (2) Sylvester step
- `sylvester` (general A B: rank A + rank B <= rank(AB) + card n; not in Mathlib). `sylvester_step`: X,Y : iota x 4, N invertible, rank(XNY^T) = r, rank X = r+p0, rank Y = r+q0 => p0+q0+r <= 4. `p0_q0_le_two`: P = 1 - XNY^T = Z (Z = -1 on i5 != i6, +1 elsewhere, `rank_one_sub_Zm` = 2) => p0+q0 <= 2. `rank_le_left/right` give r <= rank X, rank Y (p0, q0 are genuine naturals). Needs only det N != 0 (unitriangular suffices).
## (3) 3x3 core (partial, as allowed)
Proved on 3x3 matrices T, G = diag(1,1,k), Msys_core = T G - diag(2,0,2) (`Mcore`):
- `det_core`, `core_det_neg`: det(1 - Vt T Yt^T) = det(1 - T (Yt^T Vt)), so det P|_V = -1 transports to det(1 - T G) = -1.
- `core_neither_ne_zero` (k != 0): det(1-TG) = -1 => Mcore != 0 (so rank >= 4). `core_k0_ne_zero`: k = 0 => Mcore != 0 (column 3 = -2 e3).
- `core_neither_rank`: k != 0, det(1-TG) = -1, rank Mcore <= 1 => rank(T - diag(0,2,0)) = 2 (nullity 1). Proof: (T-Dp)G = Mcore + diag(2,-2,2); rank-one det identity det(M+diag(2,-2,2)) = 4s - 8 = 0 (from det = -1), rank >= 2 by subadditivity. This is a PROOF of the case the audit only checked numerically (297/297 random rank-1 M); it holds for all T over any field with 2 != 0.
- `core_neither_involution`, `core_k0_rank_ge`: rank(Lam-1) >= 4, equality => Lam^2 = 1 (via `invol_of_dims`: dim ker(Lam-1) + dim ker(Lam+1) = dim W => Lam^2 = 1).
NAMED HYPOTHESES (not re-derived in Lean): `hrk : rank(Lam-1) = 3 + rank Msys` and `hE : dim E_-1(Lam) = 3 + nullity(T - diag(0,2,0))` (RB6 item 3 coordinate formulas; audit re-verified exactly over Q, chkT.py numerically); the unit-char / P = product-of-three-reflections structure (det P = -1 enters via `core_det_neg`); RB5 structure (e56, x_E, x_F in e56); INV.
NOT formalised: Msys != 0 in the cases u_E != 0 or eta_E != 0 (trivial extra row / T e3 column; not needed for the k != 0 neither case), the hand cases u_E-only / eta_E-only / both nonzero at rank 4, and all of item 4 (k = 0 Singular radical checks: omega_mu in radical, (DD_mu U_mu)^2 - I in radical, 90 classes), RB5's 720-order symmetry reduction.
