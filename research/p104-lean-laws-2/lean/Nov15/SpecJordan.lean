/-
SPECBREAK R51/R53 formalised (lane LEAN-NEXT33, Nov 17): JORDAN-U, R51 item 2 (order-free), R53 order-free kill of #1 at U = 4.
Source: cards/WILD/SPECBREAK/R51/{RESULT51,AUDIT51}.md, R53/{RESULT53,AUDIT53}.md.  See SpecJordan.md.
Builds on Nov15/SpecTSUR.lean (pp, Zm, Nm, ev/jobsP/uconj/ucount), SpecINV.lean (inv_rank, uconj_forms),
SpecKills.lean (bd4, jm23, jm45, R2, R3, Nfacts, sl2_dual, rank_bd4_ge).
-/
import Nov15.SpecKills
import Mathlib.LinearAlgebra.Matrix.SchurComplement
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

open Matrix Finset SpecTSUR SpecINV SpecKills

set_option linter.unusedSectionVars false

namespace SpecJordan

variable {K : Type*} [Field K]

/-! ## §0. nullity -/
section Nullity
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- `m = dim ker M` -/
noncomputable def nullity (M : Matrix n n K) : ℕ := Module.finrank K (LinearMap.ker M.mulVecLin)

theorem nullity_add_rank (M : Matrix n n K) : nullity M + M.rank = Fintype.card n := by
  unfold nullity Matrix.rank
  rw [add_comm, LinearMap.finrank_range_add_finrank_ker M.mulVecLin]
  simp

theorem nullity_le_of_inj {m : Type*} [Fintype m] (M : Matrix n n K) (N : Matrix m n K)
    (hN : ∀ v, M *ᵥ v = 0 → N *ᵥ v = 0 → v = 0) : nullity M ≤ Fintype.card m := by
  let φ : LinearMap.ker M.mulVecLin →ₗ[K] (m → K) := N.mulVecLin ∘ₗ (LinearMap.ker M.mulVecLin).subtype
  have hinj : Function.Injective φ := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro v hv
    have h1 : M *ᵥ (v : n → K) = 0 := v.2
    have h2 : N *ᵥ (v : n → K) = 0 := hv
    exact Subtype.ext (hN _ h1 h2)
  have := LinearMap.finrank_le_finrank_of_injective hinj
  simpa [nullity] using this

end Nullity

/-! ## §1. JORDAN-U -/
section Jordan
variable {n ι : Type*} [Fintype n] [DecidableEq n] [Fintype ι] [DecidableEq ι]

/-- abstract form: `g = 1 - A B`, `H = B A`; `m = dim ker (g + 1) ≤ |ι|`. -/
theorem nullity_le_card (h2 : (2 : K) ≠ 0) (A : Matrix n ι K) (B : Matrix ι n K) :
    nullity (1 - A * B + 1 : Matrix n n K) ≤ Fintype.card ι := by
  apply nullity_le_of_inj _ B
  intro v hv hB
  have h1 : (1 - A * B + 1 : Matrix n n K) *ᵥ v = 0 := hv
  rw [add_mulVec, sub_mulVec, one_mulVec, ← mulVec_mulVec, hB, mulVec_zero] at h1
  simp only [sub_zero] at h1
  have : (2 : K) • v = 0 := by rw [two_smul]; exact h1
  exact (smul_eq_zero.1 this).resolve_left h2

/-- `m = |ι|` forces `H = B A = 2 I`. -/
theorem H_eq_two (h2 : (2 : K) ≠ 0) (A : Matrix n ι K) (B : Matrix ι n K)
    (hm : nullity (1 - A * B + 1 : Matrix n n K) = Fintype.card ι) :
    B * A = (2 : K) • (1 : Matrix ι ι K) := by
  let M : Matrix n n K := 1 - A * B + 1
  let φ : LinearMap.ker M.mulVecLin →ₗ[K] (ι → K) := B.mulVecLin ∘ₗ (LinearMap.ker M.mulVecLin).subtype
  have hker : ∀ v, M *ᵥ v = 0 → A *ᵥ (B *ᵥ v) = (2 : K) • v := by
    intro v hv
    have h1 : (1 - A * B + 1 : Matrix n n K) *ᵥ v = 0 := hv
    rw [add_mulVec, sub_mulVec, one_mulVec, ← mulVec_mulVec] at h1
    rw [two_smul]; linear_combination (exp := 1) -h1
  have hinj : Function.Injective φ := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro v hv
    have h1 : M *ᵥ (v : n → K) = 0 := v.2
    have h2' : B *ᵥ (v : n → K) = 0 := hv
    have := hker _ h1
    rw [h2', mulVec_zero] at this
    have h3 : (2 : K) • (v : n → K) = 0 := this.symm
    exact Subtype.ext ((smul_eq_zero.1 h3).resolve_left h2)
  have hsurj : Function.Surjective φ := by
    rw [← LinearMap.injective_iff_surjective_of_finrank_eq_finrank]
    · exact hinj
    · simpa [nullity] using hm
  apply Matrix.toLin'.injective
  apply LinearMap.ext
  intro w
  obtain ⟨v, hv⟩ := hsurj w
  have hBv : B *ᵥ (v : n → K) = w := hv
  have := hker _ v.2
  rw [hBv] at this
  simp only [Matrix.toLin'_apply]
  rw [smul_mulVec, one_mulVec, ← mulVec_mulVec, this, mulVec_smul, hBv]


/-! ### helpers: rank 0, rank ≤ 1 decomposition, inverse-pairs -/
variable [DecidableEq K]

theorem eq_zero_of_rank_zero {ι : Type*} [Fintype ι] [DecidableEq ι] (M : Matrix ι ι K) (h : M.rank = 0) :
    M = 0 := by
  apply Matrix.toLin'.injective
  apply LinearMap.ext
  intro w
  simpa [Matrix.toLin'_apply] using rank_zero_mulVec M h w

theorem rank_le_one_decomp (M : Matrix ι ι K) (h : M.rank ≤ 1) : ∃ u v : ι → K, M = vecMulVec u v := by
  have h1 : Module.finrank K (LinearMap.range M.mulVecLin) ≤ 1 := h
  obtain ⟨u, hu⟩ := finrank_le_one_iff.1 h1
  have hcol : ∀ j, ∃ c : K, M *ᵥ Pi.single j 1 = c • (u : ι → K) := by
    intro j
    obtain ⟨c, hc⟩ := hu ⟨M *ᵥ Pi.single j 1, ⟨Pi.single j 1, rfl⟩⟩
    exact ⟨c, by simpa using (congrArg Subtype.val hc).symm⟩
  choose c hc using hcol
  refine ⟨u, c, ?_⟩
  ext i j
  have := congrFun (hc j) i
  simp only [mulVec_single_one, Matrix.transpose_apply, Pi.smul_apply, smul_eq_mul] at this
  have h3 : M i j = c j * (u : ι → K) i := this
  rw [vecMulVec_apply, mul_comm]; exact h3

theorem rank_mul_inv_right {p : Type*} [Fintype p] (A : Matrix p ι K) (H Hi : Matrix ι ι K) (h : H * Hi = 1) :
    (A * H).rank = A.rank := by
  apply le_antisymm (rank_mul_le_left _ _)
  have : A = (A * H) * Hi := by rw [Matrix.mul_assoc, h, Matrix.mul_one]
  conv_lhs => rw [this]
  exact rank_mul_le_left _ _

theorem rank_mul_inv_left {p : Type*} [Fintype p] (A : Matrix ι p K) (H Hi : Matrix ι ι K) (h : Hi * H = 1) :
    (H * A).rank = A.rank := by
  apply le_antisymm (rank_mul_le_right _ _)
  have : A = Hi * (H * A) := by rw [← Matrix.mul_assoc, h, Matrix.one_mul]
  conv_lhs => rw [this]
  exact rank_mul_le_right _ _

theorem nullity_le_nullity (M : Matrix n n K) (M' : Matrix ι ι K) (N : Matrix ι n K)
    (hmap : ∀ v, M *ᵥ v = 0 → M' *ᵥ (N *ᵥ v) = 0)
    (hinj : ∀ v, M *ᵥ v = 0 → N *ᵥ v = 0 → v = 0) : nullity M ≤ nullity M' := by
  let φ : LinearMap.ker M.mulVecLin →ₗ[K] LinearMap.ker M'.mulVecLin :=
    (N.mulVecLin ∘ₗ (LinearMap.ker M.mulVecLin).subtype).codRestrict (LinearMap.ker M'.mulVecLin)
      (fun v => hmap _ v.2)
  have hinj' : Function.Injective φ := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro v hv
    have h2 : N *ᵥ (v : n → K) = 0 := by
      exact congrArg Subtype.val hv
    exact Subtype.ext (hinj _ v.2 h2)
  exact LinearMap.finrank_le_finrank_of_injective hinj'

/-- `ker(g + 1) ⊆ range(1 - g)` (char ≠ 2): `nullity(g+1) ≤ rank(1-g)` -/
theorem nullity_le_rank (h2 : (2 : K) ≠ 0) (g : Matrix n n K) : nullity (g + 1) ≤ (1 - g).rank := by
  unfold nullity Matrix.rank
  apply Submodule.finrank_mono
  intro v hv
  have h1 : (g + 1) *ᵥ v = 0 := hv
  refine ⟨(2 : K)⁻¹ • v, ?_⟩
  rw [mulVecLin_apply, mulVec_smul, sub_mulVec, one_mulVec]
  rw [add_mulVec, one_mulVec] at h1
  have hg : g *ᵥ v = -v := eq_neg_of_add_eq_zero_left h1
  rw [hg]
  have : (2 : K)⁻¹ • (v - -v) = v := by
    rw [sub_neg_eq_add, ← two_smul K v, smul_smul, inv_mul_cancel₀ h2, one_smul]
  exact this

/-- abstract JORDAN-U (even, `m = |ι| - 1`): `g = 1 - A B`, `det g = 1`, `|ι|` even, `B A ≠ 2`. -/
theorem jordan_even_abs (h2 : (2 : K) ≠ 0) (A : Matrix n ι K) (B : Matrix ι n K)
    (hev : Even (Fintype.card ι)) (hdet : (1 - A * B : Matrix n n K).det = 1)
    (hm : nullity (1 - A * B + 1 : Matrix n n K) + 1 = Fintype.card ι)
    (hH : B * A ≠ (2 : K) • (1 : Matrix ι ι K)) :
    A.rank = Fintype.card ι ∧ ((1 - A * B + 1) * A).rank = 1 ∧
    (1 - A * B + 1) * ((1 - A * B + 1) * A) = 0 ∧ (1 - (1 - A * B)).rank = Fintype.card ι ∧
    (1 - A * B + 1) * (1 - A * B + 1) * (1 - A * B - 1) = 0 := by
  have h4 : (4 : K) ≠ 0 := by
    have : (4 : K) = 2 * 2 := by norm_num
    rw [this]; exact mul_ne_zero h2 h2
  obtain ⟨M, hM⟩ : ∃ M : Matrix ι ι K, M = B * A - 1 - 1 := ⟨_, rfl⟩
  -- (1) rank M ≤ 1
  have hnl : nullity (1 - A * B + 1 : Matrix n n K) ≤ nullity M := by
    apply nullity_le_nullity _ M B
    · intro v hv
      have h1 : (1 - A * B + 1 : Matrix n n K) *ᵥ v = 0 := hv
      rw [add_mulVec, sub_mulVec, one_mulVec, ← mulVec_mulVec] at h1
      have : A *ᵥ (B *ᵥ v) = v + v := by linear_combination (exp := 1) -h1
      rw [hM, sub_mulVec, sub_mulVec, one_mulVec, ← mulVec_mulVec, this, mulVec_add]
      abel
    · intro v hv hB
      have h1 : (1 - A * B + 1 : Matrix n n K) *ᵥ v = 0 := hv
      rw [add_mulVec, sub_mulVec, one_mulVec, ← mulVec_mulVec, hB, mulVec_zero] at h1
      simp only [sub_zero] at h1
      have : (2 : K) • v = 0 := by rw [two_smul]; exact h1
      exact (smul_eq_zero.1 this).resolve_left h2
  have hrM : M.rank ≤ 1 := by
    have h1 := nullity_add_rank M
    omega
  obtain ⟨u, v, huv⟩ := rank_le_one_decomp M hrM
  -- (2) det: v·u = 0
  have hdet2 : (1 - B * A : Matrix ι ι K).det = 1 := by rw [← det_one_sub_mul_comm, hdet]
  have e1 : (1 - B * A : Matrix ι ι K) = -(1 + replicateCol Unit u * replicateRow Unit v) := by
    rw [← vecMulVec_eq, ← huv, hM]; abel
  have hvu : v ⬝ᵥ u = 0 := by
    rw [e1, det_neg, det_one_add_replicateCol_mul_replicateRow, hev.neg_one_pow, one_mul] at hdet2
    linear_combination hdet2
  have hMM : M * M = 0 := by
    rw [huv, vecMulVec_mul_vecMulVec, hvu, zero_smul]; ext i j; simp [vecMulVec_apply]
  -- (3) H invertible
  have hMM' : (1 + 1 - M) * (M + 1 + 1) = (4 : K) • (1 : Matrix ι ι K) := by
    have e4 : (4 : K) • (1 : Matrix ι ι K) = 1 + 1 + 1 + 1 := by
      rw [show (4 : K) = 1 + 1 + 1 + 1 by norm_num]; simp only [add_smul, one_smul]
    rw [e4]
    have : (1 + 1 - M) * (M + 1 + 1) = 1 + 1 + 1 + 1 - M * M := by noncomm_ring
    rw [this, hMM]; abel
  have hMM2 : (M + 1 + 1) * (1 + 1 - M) = (4 : K) • (1 : Matrix ι ι K) := by
    have e4 : (4 : K) • (1 : Matrix ι ι K) = 1 + 1 + 1 + 1 := by
      rw [show (4 : K) = 1 + 1 + 1 + 1 by norm_num]; simp only [add_smul, one_smul]
    rw [e4]
    have : (M + 1 + 1) * (1 + 1 - M) = 1 + 1 + 1 + 1 - M * M := by noncomm_ring
    rw [this, hMM]; abel
  set Hi : Matrix ι ι K := (4 : K)⁻¹ • (1 + 1 - M) with hHi
  have hHH : (M + 1 + 1) * Hi = 1 := by
    rw [hHi, mul_smul_comm, hMM2, smul_smul, inv_mul_cancel₀ h4, one_smul]
  have hHH' : Hi * (M + 1 + 1) = 1 := by
    rw [hHi, smul_mul_assoc, hMM', smul_smul, inv_mul_cancel₀ h4, one_smul]
  have hHdef : B * A = M + 1 + 1 := by rw [hM]; abel
  -- (4) ranks
  have hrA : A.rank = Fintype.card ι := by
    apply le_antisymm (rank_le_card_width A)
    have h1 : (B * A).rank ≤ A.rank := rank_mul_le_right _ _
    have h2' : (M + 1 + 1 : Matrix ι ι K).rank ≥ (1 : Matrix ι ι K).rank := by
      have := rank_mul_le_left (M + 1 + 1) Hi
      rwa [hHH] at this
    rw [rank_one] at h2'
    rw [hHdef] at h1
    omega
  have hgA : (1 - (1 - A * B) : Matrix n n K) = A * B := by abel
  have hrAB : (A * B).rank = Fintype.card ι := by
    apply le_antisymm ((rank_mul_le_left _ _).trans (rank_le_card_width A))
    have h1 : (A * B * A).rank ≤ (A * B).rank := rank_mul_le_left _ _
    have h2' : (A * B * A).rank = A.rank := by
      rw [Matrix.mul_assoc, hHdef]; exact rank_mul_inv_right A _ Hi hHH
    omega
  -- (5) identities
  have hgA' : (1 - A * B + 1 : Matrix n n K) * A = -(A * M) := by
    rw [hM]
    simp only [Matrix.add_mul, Matrix.sub_mul, Matrix.one_mul, Matrix.mul_sub, Matrix.mul_one,
      Matrix.mul_assoc, neg_sub]
    abel
  have hgAA : (1 - A * B + 1 : Matrix n n K) * ((1 - A * B + 1) * A) = 0 := by
    rw [hgA', Matrix.mul_neg, ← Matrix.mul_assoc, hgA', Matrix.neg_mul, neg_neg, Matrix.mul_assoc, hMM,
      Matrix.mul_zero]
  have hMne : M ≠ 0 := by
    intro h0; apply hH
    rw [hHdef, h0]
    have : (2 : K) • (1 : Matrix ι ι K) = 1 + 1 := by rw [two_smul]
    rw [this]; abel
  have hrM : M.rank = 1 := by
    apply le_antisymm hrM
    by_contra hlt
    exact hMne (eq_zero_of_rank_zero M (by omega))
  have hrAM : (A * M).rank = 1 := by
    apply le_antisymm ((rank_mul_le_right _ _).trans hrM.le)
    have h1 : (Hi * (B * (A * M))).rank ≤ (A * M).rank :=
      (rank_mul_le_right _ _).trans (rank_mul_le_right _ _)
    have h3 : Hi * (B * (A * M)) = M := by
      rw [← Matrix.mul_assoc B A M, hHdef, ← Matrix.mul_assoc, hHH', Matrix.one_mul]
    rw [h3, hrM] at h1
    exact h1
  refine ⟨hrA, ?_, hgAA, ?_, ?_⟩
  · rw [hgA', rank_neg_eq, hrAM]
  · rw [hgA, hrAB]
  · have e : (1 - A * B - 1 : Matrix n n K) = -(A * B) := by abel
    have key : ∀ P : Matrix n n K, P * (P * A) = 0 → P * P * (-(A * B)) = 0 := fun P hP => by
      rw [Matrix.mul_neg, ← Matrix.mul_assoc (P * P) A B, Matrix.mul_assoc P P A, hP, Matrix.zero_mul,
        neg_zero]
    rw [e]; exact key _ hgAA

end Jordan

/-! ### specialisation to a product of `U` transvections `pp x y U` -/
section PPCase
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

/-- `Qᵀ` as in `one_sub_pp` -/
abbrev Qm (x y : ℕ → n → K) (U : ℕ) : Matrix (Fin U) n K := (Matrix.of fun a (i : Fin U) => y i a)ᵀ

theorem pp_eq_AB (x y : ℕ → n → K) (U : ℕ) : pp x y U = 1 - Zm x y U * Qm x y U := by
  rw [← one_sub_pp]; abel

/-- `Qᵀ Z ≠ 2 I` for transvections (diagonal of `Qᵀ Z N = Qᵀ X` is `y_i·x_i = 0`, `N` unitriangular) -/
theorem H_ne_two (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (U : ℕ) (hq : ∀ i < U, y i ⬝ᵥ x i = 0)
    (hU : 0 < U) : Qm x y U * Zm x y U ≠ (2 : K) • (1 : Matrix (Fin U) (Fin U) K) := by
  intro h
  have e : (Qm x y U * Zm x y U) * Nm x y U = Qm x y U * Xm x U := by
    rw [Matrix.mul_assoc, ZN_eq]
  rw [h] at e
  have h0 := congrFun (congrFun e ⟨0, hU⟩) ⟨0, hU⟩
  have hg : (Qm x y U * Xm x U) ⟨0, hU⟩ ⟨0, hU⟩ = 0 := by
    have := gram_apply x y U ⟨0, hU⟩ ⟨0, hU⟩
    simp only [Qm]; rw [this]; exact hq 0 hU
  rw [hg] at h0
  have hN : (Nm x y U) ⟨0, hU⟩ ⟨0, hU⟩ = 1 := by simp [Nm]
  rw [smul_mul_assoc, Matrix.one_mul] at h0
  simp only [Matrix.smul_apply, hN, smul_eq_mul, mul_one] at h0
  exact h2 h0

/-- **JORDAN-U (a), paper form.** `g = ∏ T_i`, `m = dim ker (g + I)`: `m ≤ U`; `m = U ⇒ g² = I`. -/
theorem jordan_a (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (U : ℕ)
    (hm : nullity (pp x y U + 1) = U) : pp x y U * pp x y U = 1 := by
  rw [pp_eq_AB] at hm ⊢
  have hH := H_eq_two h2 (Zm x y U) (Qm x y U) (by simpa using hm)
  have e : (1 - Zm x y U * Qm x y U) * (1 - Zm x y U * Qm x y U) =
      1 - Zm x y U * Qm x y U - Zm x y U * Qm x y U + Zm x y U * (Qm x y U * Zm x y U) * Qm x y U := by
    simp only [Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_one, Matrix.one_mul, Matrix.mul_assoc]
    abel
  rw [e, hH]
  have e3 : Zm x y U * ((2 : K) • (1 : Matrix (Fin U) (Fin U) K)) * Qm x y U =
      (2 : K) • (Zm x y U * Qm x y U) := by
    rw [Matrix.mul_smul, Matrix.mul_one, Matrix.smul_mul]
  rw [e3, two_smul]
  abel

theorem jordan_le_U (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (U : ℕ) :
    nullity (pp x y U + 1) ≤ U := by
  rw [pp_eq_AB]
  simpa using nullity_le_card h2 (Zm x y U) (Qm x y U)

/-- **JORDAN-U (a) + INV.** `m ≤ U - 1` always (so `m = U` is impossible for `U ≥ 1`): `m = U ⇒ g² = I`
(`jordan_a`), then INV gives `rank(I - g) ≤ U - 1`, while `ker(g+I) ⊆ im(I-g)` gives `rank(I-g) ≥ m`. -/
theorem jordan_le (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (U : ℕ) (hq : ∀ i < U, y i ⬝ᵥ x i = 0) :
    nullity (pp x y U + 1) ≤ U - 1 := by
  have hle := jordan_le_U h2 x y U
  by_contra hcon
  have hm : nullity (pp x y U + 1) = U := by omega
  have hg := jordan_a h2 x y U hm
  have h1 := inv_rank h2 U x y hq hg
  have h3 := nullity_le_rank h2 (pp x y U)
  omega

/-- direct form of the same fact (diagonal argument): `m = U` is impossible for `U ≥ 1` -/
theorem jordan_ne_U (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (U : ℕ) (hq : ∀ i < U, y i ⬝ᵥ x i = 0)
    (hU : 0 < U) : nullity (pp x y U + 1) ≠ U := by
  intro hm
  rw [pp_eq_AB] at hm
  exact H_ne_two h2 x y U hq hU (H_eq_two h2 (Zm x y U) (Qm x y U) (by simpa using hm))

theorem det_pp_one (x y : ℕ → n → K) (U : ℕ) (hq : ∀ i < U, y i ⬝ᵥ x i = 0) : (pp x y U).det = 1 := by
  rw [det_pp_gen]
  exact Finset.prod_eq_one fun i hi => by rw [hq i (Finset.mem_range.1 hi)]; simp

/-- **JORDAN-U (b).** EVEN `U`, `m = U - 1`: `range Z` (`Z = (T_0⋯T_{i-1}) x_i`, a `g`-invariant `U`-dim subspace)
carries `g + I` nilpotent of type `(2, 1^{U-2})`: ONE Jordan block of size 2 at `-1`; `rank(I - g) = U`;
`(g+I)²(g-I) = 0`. -/
theorem jordan_even (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (U : ℕ) (hq : ∀ i < U, y i ⬝ᵥ x i = 0)
    (hev : Even U) (hm : nullity (pp x y U + 1) + 1 = U) :
    (Zm x y U).rank = U ∧ ((pp x y U + 1) * Zm x y U).rank = 1 ∧
    (pp x y U + 1) * ((pp x y U + 1) * Zm x y U) = 0 ∧ (1 - pp x y U).rank = U ∧
    (pp x y U + 1) * (pp x y U + 1) * (pp x y U - 1) = 0 := by
  have hU : 0 < U := by omega
  have hdet := det_pp_one x y U hq
  have key := jordan_even_abs h2 (Zm x y U) (Qm x y U) (by simpa using hev)
    (by rw [← pp_eq_AB]; exact hdet) (by rw [← pp_eq_AB]; simpa using hm) (H_ne_two h2 x y U hq hU)
  rw [← pp_eq_AB] at key
  simpa using key

/-! ### odd `U`: the even-`U` clause of JORDAN-U (b) is FALSE (AUDIT51 FIX, counterexample) -/

/-- `U = 3`, `n = 3` over `ℚ`: `g = T₀T₁T₂` (each `y·x = 0`) equals `diag(-1,-1,1)`, so `m = 2 = U - 1`
but `g` is an involution (no Jordan block of size 2) and `rank(I - g) = 2 ≠ U`.  The paper's clause
"`m = U-1` ⇒ single 2-block at `-1`, `rank(I-g) = U`" is false for odd `U`. -/
theorem odd_counterexample : ∃ x y : ℕ → Fin 3 → ℚ, (∀ i < 3, y i ⬝ᵥ x i = 0) ∧
    pp x y 3 = diagonal ![-1, -1, 1] ∧ nullity (pp x y 3 + 1) + 1 = 3 ∧
    (1 - pp x y 3).rank = 2 ∧ pp x y 3 * pp x y 3 = 1 := by
  let x : ℕ → Fin 3 → ℚ := fun i => if i = 0 then ![-1, -1, -1] else if i = 1 then ![-1, 1, -1] else ![0, 2, -1]
  let y : ℕ → Fin 3 → ℚ := fun i => if i = 0 then ![-1, 1, 0] else if i = 1 then ![1, 1, 0] else ![2, 0, 0]
  have hpp : pp x y 3 = diagonal ![-1, -1, 1] := by
    ext i j
    fin_cases i <;> fin_cases j <;>
      simp [pp, SpecTSUR.refl, x, y, Matrix.mul_apply, vecMulVec_apply, Fin.sum_univ_three, diagonal_apply] <;>
      norm_num
  have hrk : ∀ w : Fin 3 → ℚ, (diagonal w : Matrix (Fin 3) (Fin 3) ℚ).rank =
      Fintype.card {i // w i ≠ 0} := fun w => Matrix.rank_diagonal w
  refine ⟨x, y, ?_, hpp, ?_, ?_, ?_⟩
  · intro i hi
    interval_cases i <;> simp [x, y, dotProduct, Fin.sum_univ_three]
  · have h1 := nullity_add_rank (pp x y 3 + 1)
    have e : pp x y 3 + 1 = diagonal ![0, 0, 2] := by
      rw [hpp]; ext i j
      fin_cases i <;> fin_cases j <;> simp [diagonal_apply] <;> norm_num
    rw [e] at h1 ⊢
    rw [hrk] at h1
    have hc : Fintype.card {i : Fin 3 // (![0, 0, 2] : Fin 3 → ℚ) i ≠ 0} = 1 := by
      rw [Fintype.card_subtype]; decide +revert
    rw [hc] at h1
    simp only [Fintype.card_fin] at h1
    omega
  · have e : (1 - pp x y 3) = diagonal ![2, 2, 0] := by
      rw [hpp]; ext i j
      fin_cases i <;> fin_cases j <;> simp [diagonal_apply] <;> norm_num
    rw [e, hrk]
    rw [Fintype.card_subtype]; decide +revert
  · rw [hpp, diagonal_mul_diagonal]
    ext i j
    fin_cases i <;> fin_cases j <;> simp [diagonal_apply]

end PPCase

/-! ## §2. R51 item 2, order-free: units conjugated into a product `g` of `U` transvections, `D = g J`,
`J = P d Q` (`d` a free reflection, `P Q` the clique product): `5 ≤ U + rank(Pβ + Mβ) + rank(Pγ + Mγ)`. -/
section Item2

theorem rank_fromBlocks_diag_le {m₁ m₂ n₁ n₂ : Type*} [Fintype m₁] [Fintype m₂] [Fintype n₁]
    [Fintype n₂] [DecidableEq m₁] [DecidableEq m₂] [DecidableEq n₁] [DecidableEq n₂]
    (A : Matrix m₁ n₁ K) (B : Matrix m₂ n₂ K) :
    (fromBlocks A 0 0 B).rank ≤ A.rank + B.rank := by
  let e := (LinearEquiv.sumArrowLequivProdArrow m₁ m₂ K K).symm
  let φ : (LinearMap.range A.mulVecLin × LinearMap.range B.mulVecLin) →ₗ[K] ((m₁ ⊕ m₂) → K) :=
    e.toLinearMap ∘ₗ LinearMap.prodMap (LinearMap.range A.mulVecLin).subtype
      (LinearMap.range B.mulVecLin).subtype
  have hS : LinearMap.range (fromBlocks A 0 0 B).mulVecLin ≤ LinearMap.range φ := by
    rintro _ ⟨v, rfl⟩
    refine ⟨(⟨A *ᵥ (v ∘ Sum.inl), ⟨v ∘ Sum.inl, rfl⟩⟩, ⟨B *ᵥ (v ∘ Sum.inr), ⟨v ∘ Sum.inr, rfl⟩⟩), ?_⟩
    ext (i | i) <;> simp [φ, e, fromBlocks_mulVec]
  have h1 := Submodule.finrank_mono hS
  have h2 := LinearMap.finrank_range_le φ
  rw [Module.finrank_prod] at h2
  unfold Matrix.rank
  omega

variable {nd : Type*} [Fintype nd] [DecidableEq nd] [DecidableEq K]

theorem rank_bd4_le (a : Matrix (Fin 1) (Fin 1) K) (b c : Matrix (Fin 2) (Fin 2) K) (d : Matrix nd nd K) :
    (bd4 a b c d).rank ≤ a.rank + b.rank + c.rank + d.rank := by
  have h1 := rank_fromBlocks_diag_le c d
  have h2 := rank_fromBlocks_diag_le b (fromBlocks c 0 0 d)
  have h3 := rank_fromBlocks_diag_le a (fromBlocks b 0 0 (fromBlocks c 0 0 d))
  unfold bd4
  omega

theorem bd4_add (a a' : Matrix (Fin 1) (Fin 1) K) (b b' c c' : Matrix (Fin 2) (Fin 2) K)
    (d d' : Matrix nd nd K) : bd4 a b c d + bd4 a' b' c' d' = bd4 (a + a') (b + b') (c + c') (d + d') := by
  ext (i | i | i | i) (j | j | j | j) <;> simp [bd4, Matrix.add_apply]

theorem bd4_one : (bd4 1 1 1 1 : Matrix (VV nd) (VV nd) K) = 1 := by
  simp [bd4, fromBlocks_one]

/-- **R51 item 2 (order-free), core.** `w` a word whose units are transvections (`hform`); `D = ev w`,
`J = jobsP w = P d Q` (`d` a free reflection, `P Q` the clique parts in whatever order the job letters
occur: only `P Q = S` is used, `S` the commuting clique product).  Moving units to the left, `D = g J` with
`g` a product of `U` transvections.  Then `rank(g+I) = rank(D+J) ≤ rank(D+S) + 1` and JORDAN-U gives
`nullity(g+I) ≤ U-1`; hence `5 ≤ U + rank(Pβ+Mβ) + rank(Pγ+Mγ)` (`U ≥ 1`). -/
theorem unit_core2 (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : VV nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl a b)
    (hU : 1 ≤ ucount w)
    (P d Q : Matrix (VV nd) (VV nd) K) (Pβ Pγ Mβ Mγ : Matrix (Fin 2) (Fin 2) K)
    (hD : ((ev w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 (-1) Pβ Pγ 1)
    (hJ : ((jobsP w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = P * d * Q)
    (hd : (d - 1).rank ≤ 1) (hcl : P * Q = bd4 1 Mβ Mγ 1) :
    5 ≤ ucount w + (Pβ + Mβ).rank + (Pγ + Mγ).rank := by
  obtain ⟨x, y, hxy, hp⟩ := prod_units_pp (uconj w 1) (uconj_forms w 1 hform)
  rw [length_uconj] at hxy hp
  have h1 := ev_move w 1
  simp only [one_mul] at h1
  set g : Matrix (VV nd) (VV nd) K := (((uconj w 1).prod : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K)
    with hg
  set Jm : Matrix (VV nd) (VV nd) K := ((jobsP w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K)
    with hJm
  have hDg : ((ev w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = g * Jm := by
    rw [h1]; simp [hg, hJm]
  have hnull := jordan_le h2 x y (ucount w) hxy
  rw [← hp] at hnull
  -- rank(g+1) = rank(D+J)
  have hrk1 : (g + 1).rank = (bd4 (-1) Pβ Pγ 1 + Jm).rank := by
    have e : bd4 (-1) Pβ Pγ 1 + Jm = (g + 1) * Jm := by
      rw [← hD, hDg, Matrix.add_mul, Matrix.one_mul]
    rw [e]
    have hinv : Jm * ((jobsP w)⁻¹ : (Matrix (VV nd) (VV nd) K)ˣ) = 1 := by
      rw [hJm, ← Units.val_mul, mul_inv_cancel]; rfl
    exact (rank_mul_inv_right (g + 1) Jm _ hinv).symm
  -- D + J = (D + S) + P (d-1) Q
  have hrk2 : (bd4 (-1) Pβ Pγ 1 + Jm).rank ≤ (bd4 (-1) Pβ Pγ 1 + P * Q).rank + 1 := by
    have e : bd4 (-1) Pβ Pγ 1 + Jm = (bd4 (-1) Pβ Pγ 1 + P * Q) + P * (d - 1) * Q := by
      rw [hJ]; noncomm_ring
    rw [e]
    refine (rank_add_le' _ _).trans ?_
    have h3 : (P * (d - 1) * Q).rank ≤ 1 :=
      ((rank_mul_le_left _ _).trans (rank_mul_le_right _ _)).trans hd
    omega
  have hrk3 : (bd4 (-1) Pβ Pγ 1 + P * Q : Matrix (VV nd) (VV nd) K).rank ≤
      (Pβ + Mβ).rank + (Pγ + Mγ).rank + Fintype.card nd := by
    rw [hcl, bd4_add]
    refine (rank_bd4_le _ _ _ _).trans ?_
    have h0 : (-1 + 1 : Matrix (Fin 1) (Fin 1) K) = 0 := neg_add_cancel _
    rw [h0, Matrix.rank_zero]
    have := rank_le_card_width (1 + 1 : Matrix nd nd K)
    omega
  have hcard : Fintype.card (VV nd) = 5 + Fintype.card nd := by
    simp [VV, Fintype.card_sum]; omega
  have hnr := nullity_add_rank (g + 1)
  rw [hcard] at hnr
  omega

/-- `R + J` has the rank of `1 - N` when `R² = 1` and `R J = -N` -/
theorem rank_R_add {m : Type*} [Fintype m] [DecidableEq m] (R J N : Matrix m m K) (hR : R * R = 1)
    (hRJ : R * J = -N) : (R + J).rank = (1 - N).rank := by
  have hJ : J = -(R * N) := by
    calc J = R * (R * J) := by rw [← mul_assoc, hR, one_mul]
      _ = R * (-N) := by rw [hRJ]
      _ = -(R * N) := by rw [mul_neg]
  have e : R + J = R * (1 - N) := by
    rw [hJ, mul_sub, mul_one]; abel
  rw [e]
  exact rank_mul_inv_left (1 - N) R R hR

/-- chars 6 (BCDF) / 14 (BCDE): free job inside; `5 ≤ U + rank(Pγ + Mγ)` -/
theorem unit_gamma2 (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : VV nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl a b) (hU : 1 ≤ ucount w)
    (P d Q : Matrix (VV nd) (VV nd) K) (Pγ Mγ : Matrix (Fin 2) (Fin 2) K)
    (hD : ((ev w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 (-1) 1 Pγ 1)
    (hJ : ((jobsP w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = P * d * Q)
    (hd : (d - 1).rank ≤ 1) (hcl : P * Q = bd4 1 (-1) Mγ 1) :
    5 ≤ ucount w + (Pγ + Mγ).rank := by
  have := unit_core2 h2 w hform hU P d Q 1 Pγ (-1) Mγ hD hJ hd hcl
  have h0 : (1 + -1 : Matrix (Fin 2) (Fin 2) K) = 0 := add_neg_cancel _
  rw [h0, Matrix.rank_zero] at this
  omega

/-- chars 9 (ACEF) / 11 (ABEF): free job in front; `5 ≤ U + rank(Pβ + Mβ)` -/
theorem unit_beta2 (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : VV nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl a b) (hU : 1 ≤ ucount w)
    (P d Q : Matrix (VV nd) (VV nd) K) (Pβ Mβ : Matrix (Fin 2) (Fin 2) K)
    (hD : ((ev w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 (-1) Pβ 1 1)
    (hJ : ((jobsP w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = P * d * Q)
    (hd : (d - 1).rank ≤ 1) (hcl : P * Q = bd4 1 Mβ (-1) 1) :
    5 ≤ ucount w + (Pβ + Mβ).rank := by
  have := unit_core2 h2 w hform hU P d Q Pβ 1 Mβ (-1) hD hJ hd hcl
  have h0 : (1 + -1 : Matrix (Fin 2) (Fin 2) K) = 0 := add_neg_cancel _
  rw [h0, Matrix.rank_zero] at this
  omega

end Item2

/-! ## §3. R53 order-free kill of #1 at `U = 4` -/
section R53
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

/-- conjugating a reflection by a unit gives a reflection (any `y·x`) -/
theorem conj_refl (c : (Matrix n n K)ˣ) (x y : n → K) :
    (c : Matrix n n K) * SpecTSUR.refl x y * ((c⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) =
      SpecTSUR.refl ((c : Matrix n n K) *ᵥ x) (y ᵥ* ((c⁻¹ : (Matrix n n K)ˣ) : Matrix n n K)) ∧
    (y ᵥ* ((c⁻¹ : (Matrix n n K)ˣ) : Matrix n n K)) ⬝ᵥ ((c : Matrix n n K) *ᵥ x) = y ⬝ᵥ x := by
  have hPP : (c : Matrix n n K) * ((c⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = 1 := c.mul_inv
  have hQQ : ((c⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) * (c : Matrix n n K) = 1 := c.inv_mul
  refine ⟨?_, ?_⟩
  · simp only [SpecTSUR.refl, mul_sub, sub_mul, Matrix.mul_one, Matrix.mul_vecMulVec,
      Matrix.vecMulVec_mul, hPP]
  · rw [Matrix.dotProduct_mulVec, Matrix.vecMul_vecMul, hQQ, Matrix.vecMul_one]

/-- **Order-free reduction (R53 item 1).** Any interleaving `c0 P c1 Q' c2` of two free reflections `P, Q'`
with clique members (collected as units `c0, c1, c2`) equals `σ₁ σ₂ · (c0 c1 c2)` with `σ₁ = P^{c0}`,
`σ₂ = Q'^{c0c1}` reflections: a pure group identity, no letter order is used. -/
theorem orderfree_form (c0 c1 c2 P Q' : (Matrix n n K)ˣ) (xA yA xB yB : n → K)
    (hP : (P : Matrix n n K) = SpecTSUR.refl xA yA) (hQ : (Q' : Matrix n n K) = SpecTSUR.refl xB yB)
    (hA : yA ⬝ᵥ xA = 2) (hB : yB ⬝ᵥ xB = 2) :
    ∃ x1 y1 x2 y2 : n → K, y1 ⬝ᵥ x1 = 2 ∧ y2 ⬝ᵥ x2 = 2 ∧
      ((c0 * P * c1 * Q' * c2 : (Matrix n n K)ˣ) : Matrix n n K) =
        SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 * ((c0 * c1 * c2 : (Matrix n n K)ˣ) : Matrix n n K) := by
  have hg : c0 * P * c1 * Q' * c2 = (c0 * P * c0⁻¹) * ((c0 * c1) * Q' * (c0 * c1)⁻¹) * (c0 * c1 * c2) := by
    group
  obtain ⟨e1, d1⟩ := conj_refl c0 xA yA
  obtain ⟨e2, d2⟩ := conj_refl (c0 * c1) xB yB
  have e1u : ((c0 * P * c0⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) =
      SpecTSUR.refl ((c0 : Matrix n n K) *ᵥ xA) (yA ᵥ* ((c0⁻¹ : (Matrix n n K)ˣ) : Matrix n n K)) := by
    rw [Units.val_mul, Units.val_mul, hP]; exact e1
  have e2u : ((c0 * c1 * Q' * (c0 * c1)⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) =
      SpecTSUR.refl (((c0 * c1 : (Matrix n n K)ˣ) : Matrix n n K) *ᵥ xB)
        (yB ᵥ* (((c0 * c1)⁻¹ : (Matrix n n K)ˣ) : Matrix n n K)) := by
    rw [Units.val_mul, Units.val_mul, hQ]; exact e2
  refine ⟨_, _, _, _, d1.trans hA, d2.trans hB, ?_⟩
  rw [hg, Units.val_mul, Units.val_mul, e1u, e2u]

/-- **Key lemma (R53 item 3).** Two reflections `σ₁ = I - x₁y₁ᵀ`, `σ₂ = I - x₂y₂ᵀ` (`y·x = 2`, char ≠ 2)
cannot have `N := σ₁σ₂ - I` with `N² = 0` and `rank N ≥ 2`: `image N ⊆ ⟨x₁,x₂⟩` forces `x₁,x₂` independent and
`image N = ⟨x₁,x₂⟩`, so `N x₁ = 0`, i.e. `σ₁σ₂ x₁ = x₁`; computing gives `(cs-2)x₁ - c x₂ = 0`
(`c = y₂·x₁`, `s = y₁·x₂`), hence `c = 0` and `2 = cs = 0`. -/
theorem two_refl_kill (h2 : (2 : K) ≠ 0) (x1 y1 x2 y2 : n → K) (h1 : y1 ⬝ᵥ x1 = 2) (h2' : y2 ⬝ᵥ x2 = 2)
    (Nm : Matrix n n K) (hN : Nm = SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 - 1) (hNN : Nm * Nm = 0)
    (hr : 2 ≤ Nm.rank) : False := by
  have hNw : ∀ w, Nm *ᵥ w = -((y2 ⬝ᵥ w) • x2) - (y1 ⬝ᵥ (w - (y2 ⬝ᵥ w) • x2)) • x1 := by
    intro w
    rw [hN, sub_mulVec, ← mulVec_mulVec, one_mulVec, refl_mulVec, refl_mulVec]
    abel
  set V : Submodule K (n → K) := Submodule.span K (Set.range ![x1, x2]) with hV
  have hx1 : x1 ∈ V := Submodule.subset_span ⟨0, rfl⟩
  have hx2 : x2 ∈ V := Submodule.subset_span ⟨1, rfl⟩
  have hle : LinearMap.range Nm.mulVecLin ≤ V := by
    rintro _ ⟨w, rfl⟩
    rw [mulVecLin_apply, hNw]
    exact V.sub_mem (V.neg_mem (V.smul_mem _ hx2)) (V.smul_mem _ hx1)
  have hVd : Module.finrank K V ≤ 2 := by
    have := finrank_range_le_card (R := K) ![x1, x2]
    simpa [Set.finrank] using this
  have hrk : 2 ≤ Module.finrank K (LinearMap.range Nm.mulVecLin) := hr
  have heq : LinearMap.range Nm.mulVecLin = V := Submodule.eq_of_le_of_finrank_le hle (by omega)
  have hVd2 : Module.finrank K V = 2 := by
    have := Submodule.finrank_mono hle
    omega
  have hli : LinearIndependent K ![x1, x2] := by
    rw [linearIndependent_iff_card_eq_finrank_span]
    simp only [Fintype.card_fin]
    simpa [Set.finrank] using hVd2.symm
  have hmem : x1 ∈ LinearMap.range Nm.mulVecLin := by rw [heq]; exact hx1
  obtain ⟨w, hw⟩ := hmem
  have hNx : Nm *ᵥ x1 = 0 := by
    have hw' : Nm *ᵥ w = x1 := hw
    rw [← hw', mulVec_mulVec, hNN, zero_mulVec]
  rw [hNw] at hNx
  rw [dotProduct_sub, dotProduct_smul, h1, smul_eq_mul] at hNx
  have := LinearIndependent.pair_iff.1 hli (-(2 - (y2 ⬝ᵥ x1) * (y1 ⬝ᵥ x2))) (-(y2 ⬝ᵥ x1)) (by
    rw [← hNx]; simp only [neg_smul, smul_sub]; module)
  have hc : y2 ⬝ᵥ x1 = 0 := by linear_combination -this.2
  apply h2
  have h3 := this.1
  rw [hc] at h3
  linear_combination -h3

/-- `refl x y - 1` has rank ≤ 1 (any index type) -/
theorem rank_refl_sub_one' (x y : n → K) : (SpecTSUR.refl x y - 1 : Matrix n n K).rank ≤ 1 := by
  have : (SpecTSUR.refl x y : Matrix n n K) - 1 = -vecMulVec x y := by
    rw [SpecTSUR.refl]; abel
  rw [this, rank_neg_eq]; exact rank_vecMulVec_le x y

/-- `N ∈ SL₂`, `rank(1 - N) ≤ 1` ⇒ `N` unipotent: `(N - 1)² = 0` (Cayley–Hamilton with `tr N = 2`) -/
theorem sub_one_sq_zero (N : Matrix (Fin 2) (Fin 2) K) (hdet : N.det = 1) (hr : (1 - N).rank ≤ 1) :
    (N - 1) * (N - 1) = 0 := by
  have h0 := det_zero_of_rank _ hr
  rw [det_one_sub2, hdet] at h0
  have hd : N 0 0 * N 1 1 - N 0 1 * N 1 0 = 1 := by rw [← hdet, Matrix.det_fin_two]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two, Matrix.sub_apply, Matrix.one_apply]
  · linear_combination (-(N 0 0)) * h0 - hd
  · linear_combination (-(N 0 1)) * h0
  · linear_combination (-(N 1 0)) * h0
  · linear_combination (-(N 1 1)) * h0 - hd

variable {nd : Type*} [Fintype nd] [DecidableEq nd]

theorem bd4_zero : (bd4 0 0 0 0 : Matrix (VV nd) (VV nd) K) = 0 := by
  ext (i | i | i | i) (j | j | j | j) <;> simp [bd4]

/-- **Kill core.** `σ₁σ₂ = I ⊕ N23 ⊕ N45 ⊕ I`, `det N = 1`, `rank(I - N23) = rank(I - N45) = 1` is impossible. -/
theorem kill_core (h2 : (2 : K) ≠ 0) (N23 N45 : Matrix (Fin 2) (Fin 2) K) (h23 : N23.det = 1)
    (h45 : N45.det = 1) (a1 : (1 - N23).rank = 1) (b1 : (1 - N45).rank = 1)
    (x1 y1 x2 y2 : VV nd → K) (hy1 : y1 ⬝ᵥ x1 = 2) (hy2 : y2 ⬝ᵥ x2 = 2)
    (hZ : SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 = (bd4 1 N23 N45 1 : Matrix (VV nd) (VV nd) K)) :
    False := by
  have hZ1 : (bd4 1 N23 N45 1 : Matrix (VV nd) (VV nd) K) - 1 = bd4 0 (N23 - 1) (N45 - 1) 0 := by
    rw [← bd4_one, bd4_sub]; simp
  have hnil : (bd4 0 (N23 - 1) (N45 - 1) 0 : Matrix (VV nd) (VV nd) K) *
      bd4 0 (N23 - 1) (N45 - 1) 0 = 0 := by
    rw [bd4_mul, sub_one_sq_zero N23 h23 a1.le, sub_one_sq_zero N45 h45 b1.le]
    simpa using bd4_zero (K := K) (nd := nd)
  have hrk : 2 ≤ (bd4 0 (N23 - 1) (N45 - 1) 0 : Matrix (VV nd) (VV nd) K).rank := by
    have h := rank_bd4_ge (0 : Matrix (Fin 1) (Fin 1) K) (N23 - 1) (N45 - 1) (0 : Matrix nd nd K)
    have e1 : (N23 - 1).rank = 1 := by rw [← neg_sub, rank_neg_eq, a1]
    have e2 : (N45 - 1).rank = 1 := by rw [← neg_sub, rank_neg_eq, b1]
    rw [e1, e2, Matrix.rank_zero, Matrix.rank_zero] at h
    omega
  exact two_refl_kill h2 x1 y1 x2 y2 hy1 hy2 _ (by rw [hZ, hZ1]) hnil hrk

/-- **R53 order-free kill, one character.** The unit-free word `c0 P c1 Q' c2` (free reflections `P, Q'`,
clique members `c0, c1, c2` in ANY positions) has `D = I ⊕ Dβ ⊕ Dγ ⊕ I`, clique total `K = jβ ⊕ jγ`
(`Jβ² = Jγ² = I`).  If `Dβ Jβ = N23`, `Dγ Jγ = N45` are unimodular with `rank(I - N) = 1` this is impossible.
(`Z = D K⁻¹ = D K = σ₁σ₂`, `Z23 = Dβ Jβ`, `Z45 = Dγ Jγ`: independent of the slots.) -/
theorem kill_word (h2 : (2 : K) ≠ 0) (N23 N45 : Matrix (Fin 2) (Fin 2) K) (h23 : N23.det = 1)
    (h45 : N45.det = 1) (a1 : (1 - N23).rank = 1) (b1 : (1 - N45).rank = 1)
    (Dβ Dγ Jβ Jγ : Matrix (Fin 2) (Fin 2) K) (hJβ : Jβ * Jβ = 1) (hJγ : Jγ * Jγ = 1)
    (hβ : Dβ * Jβ = N23) (hγ : Dγ * Jγ = N45)
    (c0 c1 c2 P Q' : (Matrix (VV nd) (VV nd) K)ˣ) (xA yA xB yB : VV nd → K)
    (hP : (P : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl xA yA)
    (hQ : (Q' : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl xB yB) (hA : yA ⬝ᵥ xA = 2) (hB : yB ⬝ᵥ xB = 2)
    (hD : ((c0 * P * c1 * Q' * c2 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 1 Dβ Dγ 1)
    (hK : ((c0 * c1 * c2 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) =
      jm23 Jβ * jm45 Jγ) : False := by
  obtain ⟨x1, y1, x2, y2, hy1, hy2, hform⟩ := orderfree_form c0 c1 c2 P Q' xA yA xB yB hP hQ hA hB
  rw [hK, hD] at hform
  have hKK : (jm23 Jβ * jm45 Jγ : Matrix (VV nd) (VV nd) K) * (jm23 Jβ * jm45 Jγ) = 1 := by
    rw [jm23_jm45, bd4_mul, hJβ, hJγ]; simp only [mul_one]; exact bd4_one
  have hZ : SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 = (bd4 1 N23 N45 1 : Matrix (VV nd) (VV nd) K) := by
    calc SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2
        = SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 * ((jm23 Jβ * jm45 Jγ) * (jm23 Jβ * jm45 Jγ)) := by
          rw [hKK, mul_one]
      _ = (SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 * (jm23 Jβ * jm45 Jγ)) * (jm23 Jβ * jm45 Jγ) := by
          simp only [Matrix.mul_assoc]
      _ = _ := by
          rw [← hform, jm23_jm45, bd4_mul, hβ, hγ]; simp
  exact kill_core h2 N23 N45 h23 h45 a1 b1 x1 y1 x2 y2 hy1 hy2 hZ

/-- the four unit-free characters 5 (ACDF), 7 (ABDF), 13 (ACDE), 15 (ABDE) give the SAME `Z`:
`D5 = R2⊕R2`, `D7 = R3⊕R2`, `D13 = R2⊕R3`, `D15 = R3⊕R3` against `K = JX1 ⊕ JX2` all give `N23 ⊕ N45`. -/
theorem Z_four (xC yC xF yF : Fin 2 → K) (hC : yC ⬝ᵥ xC = 2) (hF : yF ⬝ᵥ xF = 2)
    (JB JE : Matrix (Fin 2) (Fin 2) K) (hBC : JB * SpecTSUR.refl xC yC = -1)
    (hEF : JE * SpecTSUR.refl xF yF = -1) :
    R3 * JB = R2 * SpecTSUR.refl xC yC ∧ R3 * JE = R2 * SpecTSUR.refl xF yF :=
  ⟨(Nfacts xC yC hC JB hBC).2.1, (Nfacts xF yF hF JE hEF).2.1⟩

/-- **kill1_all: #1 has no realisation at `U = 4`, for every job order.**  Character data as hypotheses:
clique blocks `JC = refl xC yC`, `JF = refl xF yF`, `JB JC = -I`, `JE JF = -I` (Lemma TS); unit-free char 5 (ACDF) in
ORDER-FREE form (`c0 P c1 Q' c2`, any slots; chars 7, 13, 15 give the same `Z`, `Z_four`);
unit chars 6 (BCDF, free `D`, clique part `P Q = I ⊕ -I ⊕ JF`) and 9 (ACEF, free `A`, `P Q = I ⊕ JC ⊕ -I`),
words with transvection units, `ucount = 4`, `ev = D_μ`, `jobsP = P d Q`, `rank(d - 1) ≤ 1`.
Proof: char 5 gives `a + b ≤ 2` (`rank(Z - 1) ≤ 2`); chars 6/9 give `b ≥ 1`, `a ≥ 1` (item 2, JORDAN-U);
so `a = b = 1`, contradicting `kill_core`. -/
theorem kill1_all (h2 : (2 : K) ≠ 0) (xC yC xF yF : Fin 2 → K) (hC : yC ⬝ᵥ xC = 2) (hF : yF ⬝ᵥ xF = 2)
    (JB JE : Matrix (Fin 2) (Fin 2) K)
    (hBC : JB * SpecTSUR.refl xC yC = -1) (hEF : JE * SpecTSUR.refl xF yF = -1)
    -- unit-free character 5, order-free
    (c0 c1 c2 PA QD : (Matrix (VV nd) (VV nd) K)ˣ) (xA yA xD yD : VV nd → K)
    (hPA : (PA : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl xA yA)
    (hQD : (QD : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl xD yD) (hA : yA ⬝ᵥ xA = 2) (hD : yD ⬝ᵥ xD = 2)
    (h5 : ((c0 * PA * c1 * QD * c2 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 1 R2 R2 1)
    (hK5 : ((c0 * c1 * c2 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) =
      jm23 (SpecTSUR.refl xC yC) * jm45 (SpecTSUR.refl xF yF))
    -- unit characters 6 and 9
    (w6 w9 : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (hf6 : ∀ t, Sum.inl t ∈ w6 → ∃ a b : VV nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl a b)
    (hf9 : ∀ t, Sum.inl t ∈ w9 → ∃ a b : VV nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (VV nd) (VV nd) K) = SpecTSUR.refl a b)
    (P6 d6 Q6 P9 d9 Q9 : Matrix (VV nd) (VV nd) K)
    (hD6 : ((ev w6 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 (-1) 1 R3 1)
    (hJ6 : ((jobsP w6 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = P6 * d6 * Q6)
    (hd6 : (d6 - 1).rank ≤ 1) (hc6 : P6 * Q6 = bd4 1 (-1) (SpecTSUR.refl xF yF) 1)
    (hD9 : ((ev w9 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 (-1) R3 1 1)
    (hJ9 : ((jobsP w9 : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = P9 * d9 * Q9)
    (hd9 : (d9 - 1).rank ≤ 1) (hc9 : P9 * Q9 = bd4 1 (SpecTSUR.refl xC yC) (-1) 1)
    (hu6 : ucount w6 = 4) (hu9 : ucount w9 = 4) : False := by
  obtain ⟨eB, hB3, hC3, hB2, hdet23⟩ := Nfacts xC yC hC JB hBC
  obtain ⟨eE, hE3, hF3, hE2, hdet45⟩ := Nfacts xF yF hF JE hEF
  set JC := SpecTSUR.refl xC yC with hJC
  set JF := SpecTSUR.refl xF yF with hJF
  set N23 := (R2 : Matrix (Fin 2) (Fin 2) K) * JC with hN23
  set N45 := (R2 : Matrix (Fin 2) (Fin 2) K) * JF with hN45
  have hJC2 : JC * JC = 1 := refl_sq xC yC hC
  have hJF2 : JF * JF = 1 := refl_sq xF yF hF
  -- item 2: b ≥ 1 (char 6) and a ≥ 1 (char 9)
  have u6 := unit_gamma2 h2 w6 hf6 (by omega) P6 d6 Q6 R3 JF hD6 hJ6 hd6 hc6
  have u9 := unit_beta2 h2 w9 hf9 (by omega) P9 d9 Q9 R3 JC hD9 hJ9 hd9 hc9
  rw [rank_R_add R3 JF N45 R3_mul hF3, hu6] at u6
  rw [rank_R_add R3 JC N23 R3_mul hC3, hu9] at u9
  -- char 5: a + b ≤ 2 from rank(Z - 1) ≤ 2 and Z = I ⊕ N23 ⊕ N45
  obtain ⟨x1, y1, x2, y2, hy1, hy2, hform⟩ :=
    orderfree_form c0 c1 c2 PA QD xA yA xD yD hPA hQD hA hD
  rw [hK5, h5] at hform
  have hKK : (jm23 JC * jm45 JF : Matrix (VV nd) (VV nd) K) * (jm23 JC * jm45 JF) = 1 := by
    rw [jm23_jm45, bd4_mul, hJC2, hJF2]; simp only [mul_one]; exact bd4_one
  have hZ : SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 = (bd4 1 N23 N45 1 : Matrix (VV nd) (VV nd) K) := by
    calc SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2
        = SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 * ((jm23 JC * jm45 JF) * (jm23 JC * jm45 JF)) := by
          rw [hKK, mul_one]
      _ = (SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 * (jm23 JC * jm45 JF)) * (jm23 JC * jm45 JF) := by
          simp only [Matrix.mul_assoc]
      _ = _ := by
          rw [← hform, jm23_jm45, bd4_mul, hN23, hN45]; simp
  have hab : (1 - N23).rank + (1 - N45).rank ≤ 2 := by
    have e : (bd4 1 N23 N45 1 : Matrix (VV nd) (VV nd) K) - 1 = bd4 0 (N23 - 1) (N45 - 1) 0 := by
      rw [← bd4_one, bd4_sub]; simp
    have e2 : SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 - 1 =
        (SpecTSUR.refl x1 y1 - 1) * SpecTSUR.refl x2 y2 + (SpecTSUR.refl x2 y2 - 1) := by noncomm_ring
    have h1 : (SpecTSUR.refl x1 y1 * SpecTSUR.refl x2 y2 - 1 : Matrix (VV nd) (VV nd) K).rank ≤ 2 := by
      rw [e2]
      refine (rank_add_le' _ _).trans ?_
      have := rank_mul_le_left (SpecTSUR.refl x1 y1 - 1) (SpecTSUR.refl x2 y2 : Matrix (VV nd) (VV nd) K)
      have := rank_refl_sub_one' x1 y1 (K := K)
      have := rank_refl_sub_one' x2 y2 (K := K)
      omega
    rw [hZ, e] at h1
    have h := rank_bd4_ge (0 : Matrix (Fin 1) (Fin 1) K) (N23 - 1) (N45 - 1) (0 : Matrix nd nd K)
    have e1 : (N23 - 1).rank = (1 - N23).rank := by rw [← neg_sub, rank_neg_eq]
    have e2' : (N45 - 1).rank = (1 - N45).rank := by rw [← neg_sub, rank_neg_eq]
    rw [e1, e2', Matrix.rank_zero, Matrix.rank_zero] at h
    omega
  exact kill_core h2 N23 N45 hdet23 hdet45 (by omega) (by omega) x1 y1 x2 y2 hy1 hy2 hZ

end R53

end SpecJordan

#print axioms SpecJordan.jordan_a
#print axioms SpecJordan.jordan_le
#print axioms SpecJordan.jordan_ne_U
#print axioms SpecJordan.jordan_even
#print axioms SpecJordan.odd_counterexample
#print axioms SpecJordan.unit_core2
#print axioms SpecJordan.unit_gamma2
#print axioms SpecJordan.unit_beta2
#print axioms SpecJordan.orderfree_form
#print axioms SpecJordan.two_refl_kill
#print axioms SpecJordan.kill_core
#print axioms SpecJordan.kill_word
#print axioms SpecJordan.kill1_all
