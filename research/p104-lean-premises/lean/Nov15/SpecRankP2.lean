/-
SPECBREAK RB4 item (c): the U = 4 step of #7's kill, in the form the AUDIT confirmed .
Source: internal notes,AUDIT}.md, LEDGER "#7 status".  See SpecRankP2.md.
-/
import Nov15.SpecRankP
import Nov15.SpecINV

open Matrix Module SpecTSUR SpecRankP

set_option linter.unusedSectionVars false

namespace SpecRankP2

variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- RB1 coordinates: `e₁ | S = 4 coordinates | ancillas`. -/
abbrev Nn (ι : Type*) := Unit ⊕ Fin 4 ⊕ ι

/-- the reflection `ρ = I - e₁ (2 e₁*)ᵀ`: `-1` on `e₁`, `+1` elsewhere. -/
def rho (K : Type*) [Field K] (ι : Type*) [Fintype ι] [DecidableEq ι] : Matrix (Nn ι) (Nn ι) K :=
  diagonal (Sum.elim (fun _ => -1) (fun _ => 1))

/-- `N = ρΔ`: `-1` on `e₁` and `S`, `+1` on the ancillas. -/
def Nd (K : Type*) [Field K] (ι : Type*) [Fintype ι] [DecidableEq ι] : Matrix (Nn ι) (Nn ι) K :=
  diagonal (Sum.elim (fun _ => -1) (Sum.elim (fun _ => -1) (fun _ => 1)))

/-- the vector `e₁`. -/
def e1v (K : Type*) [Field K] (ι : Type*) [Fintype ι] [DecidableEq ι] : Nn ι → K :=
  Pi.single (Sum.inl ()) 1

theorem rho_eq_refl : rho K ι = SpecTSUR.refl (e1v K ι) ((2 : K) • e1v K ι) := by
  ext a b
  rcases a with a | a | a <;> rcases b with b | b | b <;>
    simp [rho, SpecTSUR.refl, e1v, vecMulVec_apply, diagonal_apply, Pi.single_apply, Matrix.one_apply] <;> norm_num

theorem rho_mul_rho : rho K ι * rho K ι = 1 := by
  rw [rho, diagonal_mul_diagonal, ← diagonal_one]; congr 1; funext a
  rcases a with a | a | a <;> simp

theorem rho_mul_Nd : rho K ι * Nd K ι = Dl K ι := by
  rw [rho, Nd, Dl, diagonal_mul_diagonal]; congr 1; funext a
  rcases a with a | a | a <;> simp

theorem Nd_mul_rho : Nd K ι * rho K ι = Dl K ι := by
  rw [rho, Nd, Dl, diagonal_mul_diagonal]; congr 1; funext a
  rcases a with a | a | a <;> simp

theorem Dl_mul_rho : Dl K ι * rho K ι = Nd K ι := by
  rw [rho, Nd, Dl, diagonal_mul_diagonal]; congr 1; funext a
  rcases a with a | a | a <;> simp

theorem rho_mul_Dl : rho K ι * Dl K ι = Nd K ι := by
  rw [rho, Nd, Dl, diagonal_mul_diagonal]; congr 1; funext a
  rcases a with a | a | a <;> simp

theorem Dl_mul_Dl : Dl K ι * Dl K ι = 1 := by
  rw [Dl, diagonal_mul_diagonal, ← diagonal_one]; congr 1; funext a
  rcases a with a | a | a <;> simp

theorem det_rho : (rho K ι).det = -1 := by
  rw [rho, det_diagonal, Fintype.prod_sum_type]
  simp

/-! ## §1. rank ≤ 4 forces the reflection to live on `e₁, S` -/

/-- If `x` has a nonzero ancilla coordinate then `rank(N - I + x yᵀ) ≥ 5`.  (No condition on `y`.) -/
theorem anc_zero (h2 : (2 : K) ≠ 0) (x y : Nn ι → K)
    (hr : (Nd K ι - 1 + vecMulVec x y).rank ≤ 4) : ∀ j, x (Sum.inr (Sum.inr j)) = 0 := by
  by_contra hcon
  push_neg at hcon
  obtain ⟨j0, hj0⟩ := hcon
  set A : Matrix (Nn ι) (Nn ι) K := Nd K ι - 1 + vecMulVec x y with hA
  set f := A.mulVecLin with hf
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have hrank : Matrix.rank A = finrank K (LinearMap.range f) := rfl
  have hdom : finrank K (Nn ι → K) = 5 + Fintype.card ι := by
    simp [Module.finrank_fintype_fun_eq_card]; omega
  let g : LinearMap.ker f →ₗ[K] (ι → K) :=
    (LinearMap.funLeft K K (fun j : ι => (Sum.inr (Sum.inr j) : Nn ι))).comp (LinearMap.ker f).subtype
  have hinj : Function.Injective g := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro u hu
    have hu' : ∀ j, (u : Nn ι → K) (Sum.inr (Sum.inr j)) = 0 := fun j => by
      have := congrFun hu j
      simpa [g, LinearMap.funLeft] using this
    have hAu : A *ᵥ (u : Nn ι → K) = 0 := u.2
    have hcoord : ∀ i, (Nd K ι).mulVec (u : Nn ι → K) i - (u : Nn ι → K) i + x i * (y ⬝ᵥ (u : Nn ι → K)) = 0 := by
      intro i
      have := congrFun hAu i
      simp [hA, add_mulVec, sub_mulVec, vecMulVec_mulVec, Matrix.one_mulVec] at this
      linear_combination this
    have hc : y ⬝ᵥ (u : Nn ι → K) = 0 := by
      have := hcoord (Sum.inr (Sum.inr j0))
      simp [Nd, mulVec_diagonal, hu' j0] at this
      rcases this with h | h
      · exact absurd h hj0
      · exact h
    apply Subtype.ext
    funext i
    have := hcoord i
    rw [hc] at this
    rcases i with i | i | i
    · simp [Nd, mulVec_diagonal] at this
      have : (2 : K) * (u : Nn ι → K) (Sum.inl i) = 0 := by linear_combination -this
      simpa [h2] using this
    · simp [Nd, mulVec_diagonal] at this
      have : (2 : K) * (u : Nn ι → K) (Sum.inr (Sum.inl i)) = 0 := by linear_combination -this
      simpa [h2] using this
    · simpa using hu' i
  have hker : finrank K (LinearMap.ker f) ≤ Fintype.card ι := by
    have := LinearMap.finrank_le_finrank_of_injective hinj
    simpa [Module.finrank_fintype_fun_eq_card] using this
  omega

/-- rank ≤ 4 ⇒ both `x` and `y` vanish on the ancillas (transpose for `y`). -/
theorem anc_zero_both (h2 : (2 : K) ≠ 0) (x y : Nn ι → K)
    (hr : (Nd K ι - 1 + vecMulVec x y).rank ≤ 4) :
    (∀ j, x (Sum.inr (Sum.inr j)) = 0) ∧ (∀ j, y (Sum.inr (Sum.inr j)) = 0) := by
  refine ⟨anc_zero h2 x y hr, anc_zero h2 y x ?_⟩
  have : (Nd K ι - 1 + vecMulVec x y)ᵀ = Nd K ι - 1 + vecMulVec y x := by
    rw [transpose_add, transpose_sub, transpose_vecMulVec, Nd, transpose_one, diagonal_transpose]
  rw [← this, rank_transpose]; exact hr

/-! ## §2. supported reflection commutes with `N` -/

theorem JNJ (x y : Nn ι → K) (hxy : y ⬝ᵥ x = 2)
    (hx : ∀ j, x (Sum.inr (Sum.inr j)) = 0) (hy : ∀ j, y (Sum.inr (Sum.inr j)) = 0) :
    SpecTSUR.refl x y * Nd K ι * SpecTSUR.refl x y = Nd K ι := by
  have hNx : Nd K ι *ᵥ x = -x := by
    funext i; rcases i with i | i | i <;> simp [Nd, mulVec_diagonal, hx]
  have hyN : y ᵥ* Nd K ι = -y := by
    funext i; rcases i with i | i | i <;> simp [Nd, vecMul_diagonal, hy]
  set M := vecMulVec x y with hM
  have h1 : M * Nd K ι = -M := by
    rw [hM, vecMulVec_mul, hyN, vecMulVec_neg]
  have h2 : Nd K ι * M = -M := by
    rw [hM, mul_vecMulVec, hNx, neg_vecMulVec]
  have h3 : M * M = (2 : K) • M := by
    rw [hM, vecMulVec_mul_vecMulVec, hxy]; ext a b; simp [vecMulVec_apply]; ring
  have : SpecTSUR.refl x y * Nd K ι * SpecTSUR.refl x y = Nd K ι - M * Nd K ι - Nd K ι * M + M * (Nd K ι * M) := by
    rw [SpecTSUR.refl, ← hM]; noncomm_ring
  rw [this, h1, h2, mul_neg, h3]; module

theorem refl_sq (x y : Nn ι → K) (hxy : y ⬝ᵥ x = 2) : SpecTSUR.refl x y * SpecTSUR.refl x y = 1 := by
  have h3 : vecMulVec x y * vecMulVec x y = (2 : K) • vecMulVec x y := by
    rw [vecMulVec_mul_vecMulVec, hxy]; ext a b; simp [vecMulVec_apply]; ring
  rw [SpecTSUR.refl]
  calc (1 - vecMulVec x y) * (1 - vecMulVec x y)
      = 1 - (2 : K) • vecMulVec x y + vecMulVec x y * vecMulVec x y := by
        rw [two_smul]; noncomm_ring
    _ = 1 := by rw [h3]; abel

/-! ## §3. the two orders: `rank(Δ - P) ≤ 4 ⇒ PΔP = Δ` -/

theorem unit_rho : IsUnit (rho K ι).det := by rw [det_rho]; exact isUnit_one.neg

theorem rhoJ_invol (h2 : (2 : K) ≠ 0) (x y : Nn ι → K) (hxy : y ⬝ᵥ x = 2)
    (hr : (Dl K ι - rho K ι * SpecTSUR.refl x y).rank ≤ 4) :
    (rho K ι * SpecTSUR.refl x y) * Dl K ι * (rho K ι * SpecTSUR.refl x y) = Dl K ι := by
  have e1 : Dl K ι - rho K ι * SpecTSUR.refl x y = rho K ι * (Nd K ι - 1 + vecMulVec x y) := by
    conv_lhs => rw [← rho_mul_Nd]
    rw [SpecTSUR.refl]; noncomm_ring
  rw [e1, rank_mul_eq_right_of_isUnit_det _ _ unit_rho] at hr
  obtain ⟨hx, hy⟩ := anc_zero_both h2 x y hr
  calc (rho K ι * SpecTSUR.refl x y) * Dl K ι * (rho K ι * SpecTSUR.refl x y)
      = rho K ι * (SpecTSUR.refl x y * (Dl K ι * rho K ι) * SpecTSUR.refl x y) := by simp only [Matrix.mul_assoc]
    _ = Dl K ι := by rw [Dl_mul_rho, JNJ x y hxy hx hy, rho_mul_Nd]

theorem Jrho_invol (h2 : (2 : K) ≠ 0) (x y : Nn ι → K) (hxy : y ⬝ᵥ x = 2)
    (hr : (Dl K ι - SpecTSUR.refl x y * rho K ι).rank ≤ 4) :
    (SpecTSUR.refl x y * rho K ι) * Dl K ι * (SpecTSUR.refl x y * rho K ι) = Dl K ι := by
  have e1 : Dl K ι - SpecTSUR.refl x y * rho K ι = (Nd K ι - 1 + vecMulVec x y) * rho K ι := by
    conv_lhs => rw [← Nd_mul_rho]
    rw [SpecTSUR.refl]; noncomm_ring
  rw [e1, rank_mul_eq_left_of_isUnit_det _ _ unit_rho] at hr
  obtain ⟨hx, hy⟩ := anc_zero_both h2 x y hr
  calc (SpecTSUR.refl x y * rho K ι) * Dl K ι * (SpecTSUR.refl x y * rho K ι)
      = (SpecTSUR.refl x y * (rho K ι * Dl K ι) * SpecTSUR.refl x y) * rho K ι := by simp only [Matrix.mul_assoc]
    _ = Dl K ι := by rw [rho_mul_Dl, JNJ x y hxy hx hy, Nd_mul_rho]

/-! ## §4. composition with `SpecRankP.rank_ge_four` and `SpecINV.inv_rank` -/

theorem rho_mulVec (w : Nn ι → K) :
    rho K ι *ᵥ w = w - (2 * w (Sum.inl ())) • e1v K ι := by
  funext i; rcases i with i | i | i <;> simp [rho, mulVec_diagonal, e1v, Pi.single_apply] <;> ring

theorem refl_mulVec (x y w : Nn ι → K) : SpecTSUR.refl x y *ᵥ w = w - (y ⬝ᵥ w) • x := by
  rw [SpecTSUR.refl, sub_mulVec, one_mulVec, vecMulVec_mulVec, op_smul_eq_smul]

theorem one_sub_pp_rank [DecidableEq K] (U : ℕ) (x y : ℕ → Nn ι → K) :
    (1 - SpecTSUR.pp x y U).rank ≤ U := by
  rw [SpecINV.one_sub_pp]
  exact (rank_mul_le_left _ _).trans (by simpa using (SpecTSUR.Zm x y U).rank_le_card_width)

/-- **`spec7_dead_U34`.**  Model: char ≠ 2 (any field), `W = K^(1+4+a)` in the RB1 coordinates,
`Δ = Dl`, `ρ = I - e₁(2e₁*)ᵀ`, `J = I - x_J y_Jᵀ` a job reflection (`y_J·x_J = 2`) with
`x_J ∈ V ∋ e₁`, `dim V ≤ 2` (no condition on `y_J`, no pairing / stratum condition), and `P` one of
`ρJ`, `Jρ`.  `Λ = P⁻¹Δ`, i.e. `P Λ = Δ`, is a product of `U` transvections (Theorem A).
Then `U ∉ {3, 4}`.  (The reduction "for every one of the 720 job orders some unit-character
`P_μ` is `ρJ` or `Jρ`" is the 15-class reduction of RB3/RB4, a hypothesis here.) -/
theorem spec7_dead_U34 [DecidableEq K] (h2 : (2 : K) ≠ 0) (U : ℕ) (hU : U = 3 ∨ U = 4)
    (xt yt : ℕ → Nn ι → K) (hq : ∀ i < U, yt i ⬝ᵥ xt i = 0)
    (xJ yJ : Nn ι → K) (hJ : yJ ⬝ᵥ xJ = 2)
    (V : Submodule K (Nn ι → K)) (hV : finrank K V ≤ 2) (hxV : xJ ∈ V) (he1 : e1v K ι ∈ V)
    (P : Matrix (Nn ι) (Nn ι) K)
    (hP : P = rho K ι * SpecTSUR.refl xJ yJ ∨ P = SpecTSUR.refl xJ yJ * rho K ι)
    (hΛ : P * SpecTSUR.pp xt yt U = Dl K ι) : False := by
  have hPV : ∀ w, P *ᵥ w - w ∈ V := by
    intro w
    have hx : ∀ c : K, c • xJ ∈ V := fun c => V.smul_mem c hxV
    have he : ∀ c : K, c • e1v K ι ∈ V := fun c => V.smul_mem c he1
    rcases hP with rfl | rfl
    · rw [← mulVec_mulVec, refl_mulVec, rho_mulVec]
      have : w - (yJ ⬝ᵥ w) • xJ - (2 * (w - (yJ ⬝ᵥ w) • xJ) (Sum.inl ())) • e1v K ι - w
          = -((yJ ⬝ᵥ w) • xJ) - (2 * (w - (yJ ⬝ᵥ w) • xJ) (Sum.inl ())) • e1v K ι := by abel
      rw [this]; exact V.sub_mem (V.neg_mem (hx _)) (he _)
    · rw [← mulVec_mulVec, rho_mulVec, refl_mulVec]
      have : w - (2 * w (Sum.inl ())) • e1v K ι - (yJ ⬝ᵥ (w - (2 * w (Sum.inl ())) • e1v K ι)) • xJ - w
          = -((2 * w (Sum.inl ())) • e1v K ι) - (yJ ⬝ᵥ (w - (2 * w (Sum.inl ())) • e1v K ι)) • xJ := by abel
      rw [this]; exact V.sub_mem (V.neg_mem (he _)) (hx _)
  have hdet : P.det = 1 := by
    rcases hP with rfl | rfl <;>
      simp [det_mul, det_rho, SpecINV.det_refl, hJ] <;> norm_num
  have hge : 4 ≤ (Dl K ι - P).rank := rank_ge_four h2 P V hV he1 hPV hdet
  have hrk : (Dl K ι - P).rank ≤ (1 - SpecTSUR.pp xt yt U).rank := by
    have : Dl K ι - P = (-P) * (1 - SpecTSUR.pp xt yt U) := by
      simp only [mul_sub, mul_one, neg_mul, hΛ]; abel
    rw [this]; exact rank_mul_le_right _ _
  have hle := one_sub_pp_rank U xt yt
  rcases hU with rfl | rfl
  · omega
  · -- U = 4: rank = 4, involution, INV
    have hr4 : (Dl K ι - P).rank ≤ 4 := hrk.trans hle
    have hinv : P * Dl K ι * P = Dl K ι := by
      rcases hP with rfl | rfl
      · exact rhoJ_invol h2 xJ yJ hJ hr4
      · exact Jrho_invol h2 xJ yJ hJ hr4
    obtain ⟨P', hPP', hP'P⟩ : ∃ P' : Matrix (Nn ι) (Nn ι) K, P * P' = 1 ∧ P' * P = 1 := by
      have hr := rho_mul_rho (K := K) (ι := ι)
      have hj := refl_sq xJ yJ hJ
      rcases hP with rfl | rfl
      · exact ⟨SpecTSUR.refl xJ yJ * rho K ι, by
          calc _ = rho K ι * (SpecTSUR.refl xJ yJ * SpecTSUR.refl xJ yJ) * rho K ι := by simp only [Matrix.mul_assoc]
            _ = 1 := by rw [hj, mul_one, hr],
          by calc _ = SpecTSUR.refl xJ yJ * (rho K ι * rho K ι) * SpecTSUR.refl xJ yJ := by simp only [Matrix.mul_assoc]
               _ = 1 := by rw [hr, mul_one, hj]⟩
      · exact ⟨rho K ι * SpecTSUR.refl xJ yJ, by
          calc _ = SpecTSUR.refl xJ yJ * (rho K ι * rho K ι) * SpecTSUR.refl xJ yJ := by simp only [Matrix.mul_assoc]
            _ = 1 := by rw [hr, mul_one, hj],
          by calc _ = rho K ι * (SpecTSUR.refl xJ yJ * SpecTSUR.refl xJ yJ) * rho K ι := by simp only [Matrix.mul_assoc]
               _ = 1 := by rw [hj, mul_one, hr]⟩
    have hpp : SpecTSUR.pp xt yt 4 = P' * Dl K ι := by
      rw [← hΛ, ← Matrix.mul_assoc, hP'P, Matrix.one_mul]
    have hP'D : P' * Dl K ι * P' = Dl K ι := by
      calc P' * Dl K ι * P' = P' * (P * Dl K ι * P) * P' := by rw [hinv]
        _ = Dl K ι := by
          calc P' * (P * Dl K ι * P) * P' = (P' * P) * Dl K ι * (P * P') := by simp only [Matrix.mul_assoc]
            _ = Dl K ι := by rw [hP'P, hPP', Matrix.one_mul, Matrix.mul_one]
    have hsq : SpecTSUR.pp xt yt 4 * SpecTSUR.pp xt yt 4 = 1 := by
      rw [hpp]
      calc P' * Dl K ι * (P' * Dl K ι) = (P' * Dl K ι * P') * Dl K ι := by simp only [Matrix.mul_assoc]
        _ = 1 := by rw [hP'D, Dl_mul_Dl]
    have := SpecINV.inv_rank h2 4 xt yt hq hsq
    omega

end SpecRankP2

#print axioms SpecRankP2.rhoJ_invol
#print axioms SpecRankP2.Jrho_invol
#print axioms SpecRankP2.spec7_dead_U34
#print axioms SpecRankP2.anc_zero_both
#print axioms SpecRankP2.JNJ
#print axioms SpecRankP2.rho_eq_refl
