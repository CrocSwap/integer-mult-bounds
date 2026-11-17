/-
SPECBREAK RB6 survivor #0 kill steps .
Source: internal notes,AUDIT}.md.  See SpecLemmaU.md for exact statements.
-/
import Mathlib.LinearAlgebra.Determinant
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.Matrix.SchurComplement
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Abel

open Module LinearMap Matrix

set_option linter.unusedSectionVars false

namespace SpecLemmaU

/-! ## §1  LEMMA U, abstract form (auditor's derivation, not RB4's `rank_ge`) -/
section Abstract
variable {K W : Type*} [Field K] [AddCommGroup W] [Module K W] [FiniteDimensional K W]

/-- `Fix(Λ) ⊆ F1`: from `Λ w = w` get `D w = P w`, so `D w - w = P w - w ∈ V ⊆ F1`; with
`D w + w ∈ F1` this gives `2 w ∈ F1`. -/
theorem fix_le (h2 : (2 : K) ≠ 0) (F1 V : Submodule K W) (hVF : V ≤ F1) (D P Λ : W →ₗ[K] W)
    (hP : ∀ w, P w - w ∈ V) (hD : ∀ w, D w + w ∈ F1) (hΛ : ∀ w, P (Λ w) = D w) :
    ∀ w, Λ w = w → w ∈ F1 := by
  intro w hw
  have h1 : D w = P w := by rw [← hΛ, hw]
  have h3 : D w - w ∈ F1 := by rw [h1]; exact hVF (hP w)
  have h4 : (2 : K) • w ∈ F1 := by
    have := F1.sub_mem (hD w) h3
    have e : (D w + w) - (D w - w) = (2 : K) • w := by rw [two_smul]; abel
    rwa [e] at this
  have := F1.smul_mem (2 : K)⁻¹ h4
  rwa [smul_smul, inv_mul_cancel₀ h2, one_smul] at this

/-- `Λ ≡ -1 (mod F1)`. -/
theorem lam_neg_mod (F1 V : Submodule K W) (hVF : V ≤ F1) (D P Λ : W →ₗ[K] W)
    (hP : ∀ w, P w - w ∈ V) (hD : ∀ w, D w + w ∈ F1) (hΛ : ∀ w, P (Λ w) = D w) :
    ∀ w, Λ w + w ∈ F1 := by
  intro w
  have h1 : P (Λ w) - Λ w ∈ F1 := hVF (hP (Λ w))
  have := F1.add_mem (F1.neg_mem h1) (hD w)
  have e : -(P (Λ w) - Λ w) + (D w + w) = Λ w + w := by rw [← hΛ w]; abel
  rwa [e] at this

/-- **LEMMA U (abstract).**  `K` a field with `2 ≠ 0`, `W` finite-dimensional, `V ≤ F1` subspaces with
`codim F1 = c`, `im (P - 1) ⊆ V`, `D ≡ -1 (mod F1)` (i.e. `D w + w ∈ F1`), and `Λ = P⁻¹ D`
(stated as `P ∘ Λ = D`).  Then `rank (Λ - 1) ≥ c`, and equality forces `Λ² = 1`.
(No bound on `dim V` is used; `P` need not be invertible.) -/
theorem lemmaU (h2 : (2 : K) ≠ 0) (F1 V : Submodule K W) (hVF : V ≤ F1) (D P Λ : W →ₗ[K] W)
    (hP : ∀ w, P w - w ∈ V) (hD : ∀ w, D w + w ∈ F1) (hΛ : ∀ w, P (Λ w) = D w)
    (c : ℕ) (hc : finrank K W = finrank K F1 + c) :
    c ≤ finrank K (range (Λ - 1)) ∧ (finrank K (range (Λ - 1)) = c → ∀ w, Λ (Λ w) = w) := by
  have hker : ker (Λ - 1) ≤ F1 := by
    intro w hw
    refine fix_le h2 F1 V hVF D P Λ hP hD hΛ w ?_
    have : Λ w - w = 0 := by simpa using hw
    exact sub_eq_zero.1 this
  have hrn := LinearMap.finrank_range_add_finrank_ker (Λ - 1)
  have hle : finrank K (ker (Λ - 1)) ≤ finrank K F1 := Submodule.finrank_mono hker
  refine ⟨by omega, fun hr => ?_⟩
  have heq : ker (Λ - 1) = F1 :=
    Submodule.eq_of_le_of_finrank_le hker (by omega)
  have hfix : ∀ f ∈ F1, Λ f = f := by
    intro f hf
    have : f ∈ ker (Λ - 1) := by rw [heq]; exact hf
    have h0 : Λ f - f = 0 := by simpa using this
    exact sub_eq_zero.1 h0
  intro w
  have h5 := hfix _ (lam_neg_mod F1 V hVF D P Λ hP hD hΛ w)
  rw [map_add] at h5
  have : Λ (Λ w) + Λ w = Λ w + w := h5
  exact add_right_cancel (b := Λ w) (by rw [this, add_comm])

end Abstract


/-! ## §2  LEMMA U in RB6 coordinates `Fin 4 ⊕ ι` (C4 = e1..e4, F1 = {C4-coordinates = 0} = <e5,e6,E'>) -/
section Mat
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- `D = -1` on the four `C4` coordinates, `d` (= `-1` on `e5`, `+1` on `e6`, `E'`) on the rest. -/
def Dm (K : Type*) [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] (d : ι → K) :
    Matrix (Fin 4 ⊕ ι) (Fin 4 ⊕ ι) K :=
  diagonal (Sum.elim (fun _ => (-1 : K)) d)

theorem Dm_mul_Dm (d : ι → K) (hd : ∀ j, d j * d j = 1) : Dm K d * Dm K d = 1 := by
  rw [Dm, diagonal_mul_diagonal, ← diagonal_one]; congr 1; funext a
  rcases a with a | a <;> simp [hd]

/-- the projection to the `C4` coordinates. -/
noncomputable def piC (K : Type*) [Field K] (ι : Type*) :
    (Fin 4 ⊕ ι → K) →ₗ[K] (Fin 4 → K) :=
  LinearMap.funLeft K K (Sum.inl : Fin 4 → Fin 4 ⊕ ι)

theorem finrank_ker_piC : finrank K (Fin 4 ⊕ ι → K) = finrank K (ker (piC K ι)) + 4 := by
  have hs : Function.Surjective (piC K ι) :=
    LinearMap.funLeft_surjective_of_injective K K _ Sum.inl_injective
  have h := LinearMap.finrank_range_add_finrank_ker (piC K ι)
  rw [LinearMap.range_eq_top.2 hs, finrank_top, Module.finrank_fin_fun] at h
  omega

/-- **LEMMA U, matrix form.**  `char ≠ 2`; `D = Dm d` with `d² = 1`; `P` invertible with
`(P - 1) w` having zero `C4`-coordinates for all `w` (this is "`V ⊆ F1`", i.e. `proj_C4 X0 = 0`).
Then `rank (P⁻¹ D - 1) ≥ 4`, and rank `= 4` ⇒ `(P⁻¹ D)² = 1`. -/
theorem lemmaU_mat (h2 : (2 : K) ≠ 0) (d : ι → K) (hd : ∀ j, d j * d j = 1)
    (P : Matrix (Fin 4 ⊕ ι) (Fin 4 ⊕ ι) K) (hdet : IsUnit P.det)
    (hPV : ∀ (w : Fin 4 ⊕ ι → K) (i : Fin 4), (P *ᵥ w - w) (Sum.inl i) = 0) :
    4 ≤ (P⁻¹ * Dm K d - 1).rank ∧
      ((P⁻¹ * Dm K d - 1).rank = 4 → (P⁻¹ * Dm K d) * (P⁻¹ * Dm K d) = 1) := by
  set F1 : Submodule K (Fin 4 ⊕ ι → K) := ker (piC K ι) with hF1
  have memF1 : ∀ w, w ∈ F1 ↔ ∀ i : Fin 4, w (Sum.inl i) = 0 := by
    intro w
    simp only [hF1, LinearMap.mem_ker, piC, LinearMap.funLeft_apply]
    exact ⟨fun h i => congrFun h i, fun h => funext h⟩
  have hP : ∀ w, (Matrix.toLin' P) w - w ∈ F1 := fun w => by
    rw [memF1]; intro i; simpa [Matrix.toLin'_apply] using hPV w i
  have hD : ∀ w, (Matrix.toLin' (Dm K d)) w + w ∈ F1 := fun w => by
    rw [memF1]; intro i
    simp [Dm, Matrix.toLin'_apply, Matrix.mulVec_diagonal]
  have hΛ : ∀ w, (Matrix.toLin' P) ((Matrix.toLin' (P⁻¹ * Dm K d)) w) = (Matrix.toLin' (Dm K d)) w := by
    intro w
    show P *ᵥ ((P⁻¹ * Dm K d) *ᵥ w) = Dm K d *ᵥ w
    rw [Matrix.mulVec_mulVec, ← Matrix.mul_assoc, Matrix.mul_nonsing_inv _ hdet, Matrix.one_mul]
  have hsub : Matrix.toLin' (P⁻¹ * Dm K d) - 1 = Matrix.toLin' (P⁻¹ * Dm K d - 1) := by
    rw [map_sub, Matrix.toLin'_one]; rfl
  have hrk : (P⁻¹ * Dm K d - 1).rank = finrank K (range (Matrix.toLin' (P⁻¹ * Dm K d) - 1)) := by
    rw [hsub]; rfl
  obtain ⟨h1, h3⟩ := lemmaU h2 F1 F1 le_rfl (Matrix.toLin' (Dm K d)) (Matrix.toLin' P)
    (Matrix.toLin' (P⁻¹ * Dm K d)) hP hD hΛ 4 finrank_ker_piC
  refine ⟨hrk ▸ h1, fun hr => ?_⟩
  have := h3 (hrk ▸ hr)
  apply Matrix.toLin'.injective
  rw [Matrix.toLin'_mul, Matrix.toLin'_one]
  exact LinearMap.ext fun w => this w

/-- **LEMMA U, transpose case.**  Same conclusions when instead the `C4`-*columns* of `P - 1`
vanish (`Y0` vanishes on `C4`). -/
theorem lemmaU_mat_T (h2 : (2 : K) ≠ 0) (d : ι → K) (hd : ∀ j, d j * d j = 1)
    (P : Matrix (Fin 4 ⊕ ι) (Fin 4 ⊕ ι) K) (hdet : IsUnit P.det)
    (hPc : ∀ (j : Fin 4 ⊕ ι) (i : Fin 4), P j (Sum.inl i) = (1 : Matrix (Fin 4 ⊕ ι) (Fin 4 ⊕ ι) K) j (Sum.inl i)) :
    4 ≤ (P⁻¹ * Dm K d - 1).rank ∧
      ((P⁻¹ * Dm K d - 1).rank = 4 → (P⁻¹ * Dm K d) * (P⁻¹ * Dm K d) = 1) := by
  have hdetT : IsUnit Pᵀ.det := by rwa [Matrix.det_transpose]
  have hPV : ∀ (w : Fin 4 ⊕ ι → K) (i : Fin 4), (Pᵀ *ᵥ w - w) (Sum.inl i) = 0 := by
    intro w i
    have : (Pᵀ *ᵥ w) (Sum.inl i) = w (Sum.inl i) := by
      simp only [Matrix.mulVec, dotProduct, Matrix.transpose_apply]
      rw [← Finset.sum_erase_add _ _ (Finset.mem_univ (Sum.inl i : Fin 4 ⊕ ι))]
      have : ∀ j ∈ Finset.univ.erase (Sum.inl i : Fin 4 ⊕ ι), P j (Sum.inl i) * w j = 0 := by
        intro j hj
        rw [hPc j i]; simp [Matrix.one_apply, Finset.ne_of_mem_erase hj]
      rw [Finset.sum_eq_zero this, hPc]; simp
    simp [this]
  have hDt : (Dm K d)ᵀ = Dm K d := by simp [Dm, diagonal_transpose]
  obtain ⟨h1, h3⟩ := lemmaU_mat h2 d hd Pᵀ hdetT hPV
  -- ranks agree
  have hrank : (P⁻¹ * Dm K d - 1).rank = (Pᵀ⁻¹ * Dm K d - 1).rank := by
    have hD2 : IsUnit (Dm K d).det := by
      have := Dm_mul_Dm d hd
      have h := congrArg Matrix.det this
      rw [Matrix.det_mul, Matrix.det_one] at h
      exact IsUnit.of_mul_eq_one _ h
    have e : ∀ Q : Matrix (Fin 4 ⊕ ι) (Fin 4 ⊕ ι) K, IsUnit Q.det →
        Q⁻¹ * Dm K d - 1 = Q⁻¹ * (Dm K d - Q) := by
      intro Q hQ
      rw [Matrix.mul_sub, Matrix.nonsing_inv_mul _ hQ]
    rw [e P hdet, e Pᵀ hdetT,
      Matrix.rank_mul_eq_right_of_isUnit_det _ _ (Matrix.isUnit_nonsing_inv_det P hdet),
      Matrix.rank_mul_eq_right_of_isUnit_det _ _ (Matrix.isUnit_nonsing_inv_det Pᵀ hdetT),
      ← Matrix.rank_transpose (Dm K d - Pᵀ)]
    simp [hDt]
  refine ⟨hrank ▸ h1, fun hr => ?_⟩
  have h4 := h3 (hrank ▸ hr)
  have hDD := Dm_mul_Dm d hd
  rw [← Matrix.transpose_nonsing_inv] at h4
  have h5 := congrArg Matrix.transpose h4
  rw [Matrix.transpose_mul, Matrix.transpose_mul, Matrix.transpose_transpose, Matrix.transpose_one,
    hDt] at h5
  calc P⁻¹ * Dm K d * (P⁻¹ * Dm K d)
      = Dm K d * (Dm K d * P⁻¹ * (Dm K d * P⁻¹)) * Dm K d := by
        simp only [Matrix.mul_assoc]
        rw [← Matrix.mul_assoc (Dm K d) (Dm K d), hDD, Matrix.one_mul]
    _ = 1 := by rw [h5, Matrix.mul_one, hDD]

end Mat

/-! ## §3  Sylvester step: `P_ABCD = Z ⇒ p0 + q0 ≤ 2` -/
section Syl
variable {K : Type*} [Field K]

/-- Sylvester's rank inequality `rank A + rank B ≤ rank (A B) + k`. -/
theorem sylvester {m n o : Type*} [Fintype m] [Fintype n] [Fintype o] [DecidableEq n]
    (A : Matrix m n K) (B : Matrix n o K) :
    A.rank + B.rank ≤ (A * B).rank + Fintype.card n := by
  set fA := A.mulVecLin
  set fB := B.mulVecLin
  have hAB : (A * B).rank = finrank K (range (fA ∘ₗ fB)) := by
    rw [← Matrix.mulVecLin_mul]; rfl
  have hA : A.rank = finrank K (range fA) := rfl
  have hB : B.rank = finrank K (range fB) := rfl
  set g : range fB →ₗ[K] (m → K) := fA.domRestrict (range fB)
  have hrg : range g = range (fA ∘ₗ fB) := by
    ext x; constructor
    · rintro ⟨⟨_, ⟨y, rfl⟩⟩, rfl⟩; exact ⟨y, rfl⟩
    · rintro ⟨y, rfl⟩; exact ⟨⟨fB y, ⟨y, rfl⟩⟩, rfl⟩
  have h1 := LinearMap.finrank_range_add_finrank_ker g
  have hk : finrank K (ker g) ≤ finrank K (ker fA) := by
    rw [← Submodule.finrank_map_subtype_eq (range fB) (ker g)]
    refine Submodule.finrank_mono ?_
    rintro w ⟨⟨s, hs⟩, hsk, rfl⟩
    simpa [g] using hsk
  have h2 := LinearMap.finrank_range_add_finrank_ker fA
  have hc : finrank K (n → K) = Fintype.card n := by simp
  rw [hrg] at h1
  omega

/-- **Sylvester step.**  `X, Y : ι × 4`, `N` invertible (unitriangular in the paper), with
`rank (X N Yᵀ) = r`, `rank X = r + p0`, `rank Y = r + q0` (`p0 = dim span x / im(XNYᵀ)`, etc.).
Then `p0 + q0 + r ≤ 4`.  For `r = 2` this is `p0 + q0 ≤ 2`. -/
theorem sylvester_step {ι : Type*} [Fintype ι] (X Y : Matrix ι (Fin 4) K)
    (N : Matrix (Fin 4) (Fin 4) K) (hN : IsUnit N.det) (r p0 q0 : ℕ)
    (hr : (X * N * Yᵀ).rank = r) (hp : X.rank = r + p0) (hq : Y.rank = r + q0) :
    p0 + q0 + r ≤ 4 := by
  have h := sylvester X (N * Yᵀ)
  rw [← Matrix.mul_assoc, hr, Matrix.rank_mul_eq_right_of_isUnit_det _ _ hN, Matrix.rank_transpose,
    hp, hq] at h
  simp at h
  omega

/-- `r ≤ rank X`: the column space of `X N Yᵀ` lies in that of `X`. -/
theorem rank_le_left {ι : Type*} [Fintype ι] (X Y : Matrix ι (Fin 4) K)
    (N : Matrix (Fin 4) (Fin 4) K) : (X * N * Yᵀ).rank ≤ X.rank :=
  (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_left _ _)

theorem rank_le_right {ι : Type*} [Fintype ι] (X Y : Matrix ι (Fin 4) K)
    (N : Matrix (Fin 4) (Fin 4) K) : (X * N * Yᵀ).rank ≤ Y.rank := by
  exact (Matrix.rank_mul_le_right _ _).trans (le_of_eq (Matrix.rank_transpose Y))

/-- `Z = -1` on two coordinates `i5 ≠ i6`, `+1` elsewhere. -/
def Zm (K : Type*) [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] (i5 i6 : ι) : Matrix ι ι K :=
  diagonal (fun i => if i = i5 ∨ i = i6 then (-1 : K) else 1)

/-- `rank (1 - Z) = 2` (char ≠ 2). -/
theorem rank_one_sub_Zm {ι : Type*} [Fintype ι] [DecidableEq ι] (h2 : (2 : K) ≠ 0)
    (i5 i6 : ι) (h56 : i5 ≠ i6) : ((1 : Matrix ι ι K) - Zm K i5 i6).rank = 2 := by
  classical
  have e : (1 : Matrix ι ι K) - Zm K i5 i6 =
      diagonal (fun i => if i = i5 ∨ i = i6 then (2 : K) else 0) := by
    ext a b
    by_cases hab : a = b
    · subst hab
      by_cases h : a = i5 ∨ a = i6 <;> simp [Zm, h] <;> norm_num
    · simp [Zm, hab, Matrix.one_apply, diagonal_apply]
  rw [e, Matrix.rank_diagonal]
  have : (Finset.univ.filter fun i : ι => (if i = i5 ∨ i = i6 then (2 : K) else 0) ≠ 0) = {i5, i6} := by
    ext i; simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_insert, Finset.mem_singleton]
    by_cases h : i = i5 ∨ i = i6 <;> simp [h, h2]
  rw [Fintype.card_subtype, this, Finset.card_pair h56]

/-- **Step (2) of survivor #0.**  If `P = 1 - X N Yᵀ = Z` (`P_ABCD = Z`), with `N` invertible, and
`rank X = 2 + p0`, `rank Y = 2 + q0`, then `p0 + q0 ≤ 2`.  (`2 ≤ rank X, rank Y` is automatic by
`rank_le_left`/`rank_le_right`, so `p0, q0` are the natural-number excesses over `e56`.) -/
theorem p0_q0_le_two {ι : Type*} [Fintype ι] [DecidableEq ι] (h2 : (2 : K) ≠ 0)
    (i5 i6 : ι) (h56 : i5 ≠ i6) (X Y : Matrix ι (Fin 4) K) (N : Matrix (Fin 4) (Fin 4) K)
    (hN : IsUnit N.det) (hP : (1 : Matrix ι ι K) - X * N * Yᵀ = Zm K i5 i6) (p0 q0 : ℕ)
    (hp : X.rank = 2 + p0) (hq : Y.rank = 2 + q0) : p0 + q0 ≤ 2 := by
  have e : X * N * Yᵀ = 1 - Zm K i5 i6 := by rw [← hP]; abel
  have hr : (X * N * Yᵀ).rank = 2 := by rw [e]; exact rank_one_sub_Zm h2 i5 i6 h56
  have := sylvester_step X Y N hN 2 p0 q0 hr hp hq
  omega

end Syl

/-! ## §4  The 3 × 3 core on `V = <e5, e6, u>` -/
section Core
variable {K : Type*} [Field K]

/-- rank `≤ 1` matrices are `a cᵀ`. -/
theorem rank_le_one_decomp {m n : Type*} [Fintype m] [Fintype n] [DecidableEq n]
    (M : Matrix m n K) (h : M.rank ≤ 1) : ∃ (a : m → K) (c : n → K), M = vecMulVec a c := by
  have h1 : finrank K (range M.mulVecLin) ≤ 1 := h
  obtain ⟨v, hv⟩ := finrank_le_one_iff.1 h1
  have : ∀ j, ∃ cj : K, ∀ i, M i j = cj * (v : m → K) i := by
    intro j
    obtain ⟨cj, hcj⟩ := hv ⟨M *ᵥ Pi.single j 1, ⟨Pi.single j 1, rfl⟩⟩
    refine ⟨cj, fun i => ?_⟩
    have := congrFun (congrArg Subtype.val hcj) i
    simpa [Matrix.mulVec_single_one] using this.symm
  choose c hc using this
  exact ⟨v, c, by ext i j; simp [vecMulVec_apply, hc j i, mul_comm]⟩

/-- `rank (A + B) ≤ rank A + rank B`. -/
theorem rank_add_le_mat {m n : Type*} [Fintype m] [Fintype n] (A B : Matrix m n K) :
    (A + B).rank ≤ A.rank + B.rank := by
  have h : range (A + B).mulVecLin ≤ range A.mulVecLin ⊔ range B.mulVecLin := by
    rintro _ ⟨w, rfl⟩
    exact Submodule.mem_sup.2 ⟨A *ᵥ w, ⟨w, rfl⟩, B *ᵥ w, ⟨w, rfl⟩, by simp [add_mulVec]⟩
  exact (Submodule.finrank_mono h).trans (Submodule.finrank_add_le_finrank_add_finrank _ _)

/-- `det P|_V = det (1 - G T)` for `P = 1 - Vt T Ytᵀ`, `G = Ytᵀ Vt` (Sylvester determinant identity). -/
theorem det_core {ι : Type*} [Fintype ι] [DecidableEq ι] (Vt Yt : Matrix ι (Fin 3) K)
    (T : Matrix (Fin 3) (Fin 3) K) :
    ((1 : Matrix ι ι K) - Vt * T * Ytᵀ).det = (1 - T * (Ytᵀ * Vt)).det := by
  rw [Matrix.det_one_sub_mul_comm, ← Matrix.mul_assoc, Matrix.det_one_sub_mul_comm,
    ← Matrix.mul_assoc]

/-- `diag(1,1,k)`. -/
def Gm (k : K) : Matrix (Fin 3) (Fin 3) K := diagonal ![1, 1, k]
def Dq : Matrix (Fin 3) (Fin 3) K := diagonal ![2, 0, 2]
def Dp : Matrix (Fin 3) (Fin 3) K := diagonal ![0, 2, 0]

/-- the 3×3 part of `Msys` in the "neither `u_E` nor `η_E`" case. -/
def Mcore (T : Matrix (Fin 3) (Fin 3) K) (k : K) : Matrix (Fin 3) (Fin 3) K := T * Gm k - Dq

/-- `Msys ≠ 0` for `k ≠ 0` (this is where `det P|_V = -1` is used; char ≠ 2). -/
theorem core_neither_ne_zero (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) (k : K)
    (hdet : (1 - T * Gm k).det = -1) : Mcore T k ≠ 0 := by
  intro h0
  have : T * Gm k = Dq := sub_eq_zero.1 h0
  rw [this] at hdet
  simp [Dq, Matrix.det_fin_three, Matrix.one_apply, diagonal_apply] at hdet
  apply h2
  linear_combination hdet

/-- `Msys ≠ 0` for `k = 0` (third column is `-2 e3`). -/
theorem core_k0_ne_zero (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) :
    Mcore T 0 ≠ 0 := by
  intro h0
  have := congrFun (congrFun h0 2) 2
  simp [Mcore, Gm, Dq, Matrix.mul_apply, Fin.sum_univ_three, diagonal_apply] at this
  exact h2 this

/-- `diag(2,-2,2) = Dq - Dp`. -/
def Dl3 : Matrix (Fin 3) (Fin 3) K := diagonal ![2, -2, 2]

theorem rank_Dl3 (h2 : (2 : K) ≠ 0) : (Dl3 : Matrix (Fin 3) (Fin 3) K).rank = 3 := by
  have hu : IsUnit (Dl3 : Matrix (Fin 3) (Fin 3) K).det := by
    rw [Dl3, det_diagonal]
    simp [Fin.prod_univ_three, h2]
  have := Matrix.rank_of_isUnit (Dl3 : Matrix (Fin 3) (Fin 3) K)
    ((Matrix.isUnit_iff_isUnit_det _).2 hu)
  simpa using this

theorem tg_eq (T : Matrix (Fin 3) (Fin 3) K) (k : K) :
    (T - Dp) * Gm k = Mcore T k + Dl3 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Mcore, Gm, Dq, Dp, Dl3, Matrix.mul_apply, Fin.sum_univ_three, diagonal_apply] <;> ring

theorem rank_le_two_of_det_zero (R : Matrix (Fin 3) (Fin 3) K) (h : R.det = 0) : R.rank ≤ 2 := by
  obtain ⟨v, hv0, hv⟩ := Matrix.exists_mulVec_eq_zero_iff.2 h
  have h1 := LinearMap.finrank_range_add_finrank_ker R.mulVecLin
  have h3 : 0 < finrank K (ker R.mulVecLin) :=
    Module.finrank_pos_iff_exists_ne_zero.2
      ⟨⟨v, LinearMap.mem_ker.2 hv⟩, fun h' => hv0 (congrArg Subtype.val h')⟩
  have h4 : finrank K (Fin 3 → K) = 3 := by simp
  have : R.rank = finrank K (range R.mulVecLin) := rfl
  omega

/-- **3×3 core, "neither" case, `k ≠ 0`.**  If `det (1 - T G) = -1` and `rank Msys ≤ 1` then
`rank (T - diag(0,2,0)) = 2`, i.e. `nullity = 1` (so `dim E_-1 = 3 + 1 = 4`).  The proof is the
rank-one determinant identity `det(M + diag(2,-2,2)) = 4 s - 8 = 0`, `s = tr(S M)`. -/
theorem core_neither_rank (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) (k : K) (hk : k ≠ 0)
    (hdet : (1 - T * Gm k).det = -1) (hM : (Mcore T k).rank ≤ 1) :
    (T - Dp).rank = 2 := by
  obtain ⟨a, c, hM'⟩ := rank_le_one_decomp _ hM
  have hG : IsUnit (Gm k).det := by
    rw [Gm, det_diagonal]; simp [Fin.prod_univ_three]; exact hk
  have hR : (T - Dp).rank = (Mcore T k + Dl3).rank := by
    rw [← tg_eq, Matrix.rank_mul_eq_left_of_isUnit_det _ _ hG]
  have hTG : T * Gm k = vecMulVec a c + Dq := by
    rw [← hM']; simp [Mcore]
  have hdet0 : (Mcore T k + Dl3).det = 0 := by
    rw [hTG] at hdet
    rw [hM']
    simp [Dq, Dl3, Matrix.det_fin_three, vecMulVec_apply, Matrix.one_apply, diagonal_apply] at hdet ⊢
    linear_combination (-4 : K) * hdet
  have hle : (Mcore T k + Dl3).rank ≤ 2 := rank_le_two_of_det_zero _ hdet0
  have hge : 2 ≤ (Mcore T k + Dl3).rank := by
    have h1 := rank_add_le_mat (Mcore T k + Dl3) (-(Mcore T k))
    have e : Mcore T k + Dl3 + -(Mcore T k) = Dl3 := by abel
    rw [e, rank_Dl3 h2] at h1
    have h2' : (-(Mcore T k)).rank ≤ 1 := by
      have : -(Mcore T k) = vecMulVec (-a) c := by rw [hM']; ext i j; simp [vecMulVec_apply]
      rw [this]; exact Matrix.rank_vecMulVec_le _ _
    omega
  omega

theorem rank_pos_of_ne_zero {m n : Type*} [Fintype m] [Fintype n] [DecidableEq n]
    (M : Matrix m n K) (h : M ≠ 0) : 0 < M.rank := by
  by_contra hr
  have h0 : finrank K (range M.mulVecLin) = 0 := by
    have : M.rank = finrank K (range M.mulVecLin) := rfl
    omega
  have hb : range M.mulVecLin = ⊥ := Submodule.finrank_eq_zero.1 h0
  apply h; ext i j
  have : M *ᵥ Pi.single j 1 = 0 := by
    have hm : M *ᵥ Pi.single j 1 ∈ range M.mulVecLin := ⟨Pi.single j 1, rfl⟩
    rw [hb] at hm; simpa using hm
  simpa [Matrix.mulVec_single_one] using congrFun this i

/-- `dim ker(Λ-1) + dim ker(Λ+1) = dim W` (char ≠ 2) forces `Λ² = 1`. -/
theorem invol_of_dims {W : Type*} [AddCommGroup W] [Module K W] [FiniteDimensional K W]
    (h2 : (2 : K) ≠ 0) (Λ : W →ₗ[K] W)
    (h : finrank K (ker (Λ - 1)) + finrank K (ker (Λ + 1)) = finrank K W) : ∀ w, Λ (Λ w) = w := by
  have hd : ker (Λ - 1) ⊓ ker (Λ + 1) = ⊥ := by
    rw [eq_bot_iff]
    intro w ⟨h1, h3⟩
    have e1 : Λ w = w := sub_eq_zero.1 (by simpa using h1)
    have e2 : Λ w = -w := eq_neg_of_add_eq_zero_left (by simpa using h3)
    have : (2 : K) • w = 0 := by rw [two_smul]; nth_rewrite 1 [← e1]; rw [e2]; abel
    simpa [h2] using this
  have hfs := Submodule.finrank_sup_add_finrank_inf_eq (ker (Λ - 1)) (ker (Λ + 1))
  rw [hd, finrank_bot] at hfs
  have htop : ker (Λ - 1) ⊔ ker (Λ + 1) = ⊤ :=
    Submodule.eq_top_of_finrank_eq (by omega)
  intro w
  have hw : w ∈ ker (Λ - 1) ⊔ ker (Λ + 1) := by rw [htop]; trivial
  obtain ⟨x, hx, y, hy, rfl⟩ := Submodule.mem_sup.1 hw
  have ex : Λ x = x := sub_eq_zero.1 (by simpa using hx)
  have ey : Λ y = -y := eq_neg_of_add_eq_zero_left (by simpa using hy)
  simp [ex, ey]

/-- `det P|_V = -1` transported to the core (`P = 1 - Vt T Ytᵀ`, `Ytᵀ Vt = diag(1,1,k)`). -/
theorem core_det_neg {ι : Type*} [Fintype ι] [DecidableEq ι] (Vt Yt : Matrix ι (Fin 3) K)
    (T : Matrix (Fin 3) (Fin 3) K) (k : K) (hG : Ytᵀ * Vt = Gm k)
    (hP : ((1 : Matrix ι ι K) - Vt * T * Ytᵀ).det = -1) : (1 - T * Gm k).det = -1 := by
  rw [← hG, ← det_core, hP]

/-- **3×3 core, "neither" case: rank ≥ 4, equality ⇒ involution.**  Here `Λ` is the unit-character
operator; the two coordinate identities `hrk`, `hE` (`rank(D-P) = 3 + rank Msys`,
`dim E_-1(Λ) = 3 + nullity(T - diag(0,2,0))`) are the RB6 item-3 formulas, checked exactly over Q
by the audit (and numerically by chkT.py) but NOT re-derived here: they are named hypotheses. -/
theorem core_neither_involution {W : Type*} [AddCommGroup W] [Module K W] [FiniteDimensional K W]
    (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) (k : K) (hk : k ≠ 0)
    (hdet : (1 - T * Gm k).det = -1) (Λ : W →ₗ[K] W)
    (hrk : finrank K (range (Λ - 1)) = 3 + (Mcore T k).rank)
    (hE : finrank K (ker (Λ + 1)) = 3 + (3 - (T - Dp).rank)) :
    4 ≤ finrank K (range (Λ - 1)) ∧ (finrank K (range (Λ - 1)) = 4 → ∀ w, Λ (Λ w) = w) := by
  have hpos := rank_pos_of_ne_zero _ (core_neither_ne_zero h2 T k hdet)
  refine ⟨by omega, fun h4 => ?_⟩
  have hM : (Mcore T k).rank ≤ 1 := by omega
  have hr := core_neither_rank h2 T k hk hdet hM
  have hrn := LinearMap.finrank_range_add_finrank_ker (Λ - 1)
  apply invol_of_dims h2 Λ
  omega

/-- **3×3 core, `k = 0`: rank ≥ 4** (third column of `Msys` is `-2 e3`). -/
theorem core_k0_rank_ge {W : Type*} [AddCommGroup W] [Module K W] [FiniteDimensional K W]
    (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) (Λ : W →ₗ[K] W)
    (hrk : finrank K (range (Λ - 1)) = 3 + (Mcore T 0).rank) : 4 ≤ finrank K (range (Λ - 1)) := by
  have := rank_pos_of_ne_zero _ (core_k0_ne_zero h2 T)
  omega

end Core

end SpecLemmaU

#print axioms SpecLemmaU.lemmaU
#print axioms SpecLemmaU.lemmaU_mat
#print axioms SpecLemmaU.lemmaU_mat_T
#print axioms SpecLemmaU.sylvester
#print axioms SpecLemmaU.p0_q0_le_two
#print axioms SpecLemmaU.core_neither_rank
#print axioms SpecLemmaU.core_neither_involution
#print axioms SpecLemmaU.core_k0_rank_ge
#print axioms SpecLemmaU.core_det_neg
