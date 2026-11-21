/-
CallerGram (lane LEAN-GRAM).  GRAM RANK LAW of K9SWEEP K9.md item 1-2 in the abstract twist model of CallerSignCore/CallerPrefix.
(1) gram_rank: for a split A ++ B of a product -1 stage list with n = dim V satisfying 2(|A|+|B|) <= n + 2 (n = 2k-2 gives equality),
    the "Gram" map  x |-> (V_t x - x)_{t in B}  (this is Y_Suf^T on a stage V_t = I + X_t Y_t^T) has rank <= 2 on the host span
    of A (= column span of X_Pre).  Proof: its kernel on hostSup A contains fixedBy B, of dim >= n - 2|B| (obstruction_law),
    while dim hostSup A <= 2|A|.
(2) schur_core / gram_chart: linear-algebra core of the on-chart corollary.  A block matrix [[P,Q],[R,S]] of rank <= m with P
    invertible m x m has S = R P^-1 Q; with P = 1 (no shared role, G_{i0 t0} = I) this is G_it = G_it0 * G_i0t.  Converse
    gram_chart_rank: S = R Q  ==> rank <= m, so the hypothesis is satisfiable.
    NOT in the abstract model: the chart coordinates G_it = I + sum kap_r lam_r and the "no shared role => P = I" step.
(3) instance_gram: the k = 3 design of CallerSignInst, both splits.
-/
import Nov15.CallerPrefix
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerSign
open Module

section
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- the Gram/deviation map of a list: `x ↦ (V_t x - x)_t`; its kernel is `fixedBy`. -/
def dev (B : List (Stage K V)) : V →ₗ[K] (Fin B.length → V) :=
  LinearMap.pi (fun i => (B.get i).map - 1)

theorem ker_dev (B : List (Stage K V)) : LinearMap.ker (dev B) = fixedBy B := by
  ext x
  rw [mem_fixedBy, LinearMap.mem_ker]
  constructor
  · intro h s hs
    obtain ⟨i, rfl⟩ := List.mem_iff_get.mp hs
    have := congrFun h i
    simpa [dev, sub_eq_zero] using this
  · intro h
    ext i
    have := h _ (List.get_mem B i)
    simpa [dev, sub_eq_zero] using this

theorem finrank_hostSup_le (l : List (Stage K V)) (hd : ∀ s ∈ l, finrank K s.host ≤ 2) :
    finrank K (hostSup l) ≤ 2 * l.length := by
  induction l with
  | nil =>
    have : hostSup ([] : List (Stage K V)) ≤ ⊥ :=
      iSup₂_le (fun s hs => absurd hs (by simp))
    rw [le_bot_iff.mp this]; simp
  | cons a l ih =>
    have e : hostSup (a :: l) = a.host ⊔ hostSup l := by
      simp [hostSup, iSup_or, iSup_sup_eq]
    have ih' := ih (fun s hs => hd s (by simp [hs]))
    have ha := hd a (by simp)
    have := Submodule.finrank_add_le_finrank_add_finrank a.host (hostSup l)
    rw [e]
    simp only [List.length_cons]
    omega

/-- rank-nullity for a submodule containing part of the kernel -/
theorem finrank_map_le_of_le_ker {W : Type*} [AddCommGroup W] [Module K W]
    (f : V →ₗ[K] W) (S N : Submodule K V) (hN : N ≤ S) (hk : N ≤ LinearMap.ker f) :
    finrank K (S.map f) + finrank K N ≤ finrank K S := by
  have h1 := LinearMap.finrank_range_add_finrank_ker (f.domRestrict S)
  rw [LinearMap.range_domRestrict] at h1
  have h2 : finrank K (N.comap S.subtype) ≤ finrank K (LinearMap.ker (f.domRestrict S)) := by
    apply Submodule.finrank_mono
    intro x hx
    simp only [Submodule.mem_comap, Submodule.subtype_apply] at hx
    simpa using hk hx
  have h3 : finrank K (N.comap S.subtype) = finrank K N :=
    (Submodule.comapSubtypeEquivOfLe hN).finrank_eq
  have h4 : finrank K S = finrank K (↥S) := rfl
  omega

/-- GRAM RANK LAW: rank (Y_Suf^T X_Pre) <= 2 for every split. -/
theorem gram_rank (A B : List (Stage K V)) (h2 : (2 : K) ≠ 0)
    (hmod : ∀ s ∈ A ++ B, Mod s.map s.host) (hd : ∀ s ∈ A ++ B, finrank K s.host ≤ 2)
    (hp : prodList (A ++ B) = -1) (hn : 2 * (A.length + B.length) ≤ finrank K V + 2) :
    finrank K ((hostSup A).map (dev B)) ≤ 2 := by
  have hmA : ∀ s ∈ A, Mod s.map s.host := fun s hs => hmod s (by simp [hs])
  have hdA : ∀ s ∈ A, finrank K s.host ≤ 2 := fun s hs => hd s (by simp [hs])
  have L := obstruction_law A B h2 hmod hd hp
  have hN : fixedBy B ≤ hostSup A := fun x hx => (L.1 x hx).1
  have hk : fixedBy B ≤ LinearMap.ker (dev B) := by rw [ker_dev]
  have := finrank_map_le_of_le_ker (dev B) (hostSup A) (fixedBy B) hN hk
  have h5 := finrank_hostSup_le A hdA
  have h6 := L.2.2.2.1
  omega

end

/-! (2) linear-algebra core of the on-chart corollary -/
section schur
open Matrix
variable {m : Type*} [Fintype m] [DecidableEq m] {K : Type*} [Field K]

/-- Schur core: a block matrix of rank <= m with invertible top-left block has vanishing Schur complement. -/
theorem schur_core (P Q R S : Matrix m m K) (hP : IsUnit P.det)
    (hr : (fromBlocks P Q R S).rank ≤ Fintype.card m) : S = R * P⁻¹ * Q := by
  set G := fromBlocks P Q R S with hG
  let ι : (m → K) →ₗ[K] (m ⊕ m → K) :=
    { toFun := fun x => Sum.elim x 0
      map_add' := by intro x y; ext (i | i) <;> simp
      map_smul' := by intro c x; ext (i | i) <;> simp }
  let T := LinearMap.range (G.mulVecLin ∘ₗ ι)
  have hinj : Function.Injective (G.mulVecLin ∘ₗ ι) := by
    intro x y hxy
    have h' : P.mulVec x = P.mulVec y := by
      ext i
      have := congrFun hxy (Sum.inl i)
      simpa [ι, hG, fromBlocks_mulVec] using this
    have := congrArg (fun v => P⁻¹.mulVec v) h'
    simpa [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul _ hP] using this
  have hT : finrank K T = Fintype.card m := by
    rw [LinearMap.finrank_range_of_inj hinj]
    simp
  have hle : T ≤ LinearMap.range G.mulVecLin := LinearMap.range_comp_le_range _ _
  have hW : finrank K (LinearMap.range G.mulVecLin) ≤ finrank K T := by
    rw [hT]; exact hr
  have heq := Submodule.eq_of_le_of_finrank_le hle hW
  have key : ∀ y : m → K, S.mulVec y = (R * P⁻¹ * Q).mulVec y := by
    intro y
    have hy : G.mulVecLin (Sum.elim 0 y) ∈ T := by
      rw [heq]; exact LinearMap.mem_range_self _ _
    obtain ⟨x, hx⟩ := hy
    have e : G.mulVec (Sum.elim x 0) = G.mulVec (Sum.elim 0 y) := by simpa [ι] using hx
    rw [hG, fromBlocks_mulVec, fromBlocks_mulVec] at e
    have e1 : P.mulVec x = Q.mulVec y := by
      ext i; have := congrFun e (Sum.inl i); simpa using this
    have e2 : R.mulVec x = S.mulVec y := by
      ext i; have := congrFun e (Sum.inr i); simpa using this
    have hx' : x = (P⁻¹ * Q).mulVec y := by
      have := congrArg (fun v => P⁻¹.mulVec v) e1
      simpa [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul _ hP] using this
    rw [← e2, hx', Matrix.mulVec_mulVec, Matrix.mul_assoc]
  ext i j
  have := congrFun (key (Pi.single j 1)) i
  simpa [Matrix.mulVec_single_one] using this

/-- chart corollary: with `P = 1` (no shared role) the Schur product `G_it = G_it0 * G_i0t`. -/
theorem gram_chart (Q R S : Matrix m m K)
    (hr : (fromBlocks (1 : Matrix m m K) Q R S).rank ≤ Fintype.card m) : S = R * Q := by
  have := schur_core 1 Q R S (by simp) hr
  simpa using this

/-- converse: the factored form really has rank <= m (hypothesis is satisfiable). -/
theorem gram_chart_rank (Q R : Matrix m m K) :
    (fromBlocks (1 : Matrix m m K) Q R (R * Q)).rank ≤ Fintype.card m := by
  have e : fromBlocks (1 : Matrix m m K) Q R (R * Q)
      = (Matrix.of (Sum.elim (fun i => (1 : Matrix m m K) i) (fun i => R i)) : Matrix (m ⊕ m) m K) *
        (Matrix.of fun (a : m) (j : m ⊕ m) => Sum.elim (fun b => (1 : Matrix m m K) a b) (fun b => Q a b) j) := by
    ext (i | i) (j | j) <;> simp [Matrix.mul_apply, Matrix.one_apply]
  rw [e]
  exact (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_le_card_width _)
end schur

/-! (3) non-vacuity: k = 3, n = 4 design of CallerSignInst -/
theorem instance_gram :
    finrank ℝ ((hostSup [s1]).map (dev [s2, s3])) ≤ 2 ∧
    finrank ℝ ((hostSup [s1, s2]).map (dev [s3])) ≤ 2 := by
  have hmod : ∀ s ∈ [s1, s2, s3], Mod s.map s.host := by
    intro s hs; simp at hs; rcases hs with rfl | rfl | rfl
    exacts [mod_s1, mod_s2, mod_s3]
  have hd : ∀ s ∈ [s1, s2, s3], finrank ℝ s.host ≤ 2 := by
    intro s hs; simp at hs; rcases hs with rfl | rfl | rfl <;> exact H_dim _ _
  have h2 : (2 : ℝ) ≠ 0 := by norm_num
  constructor
  · exact gram_rank [s1] [s2, s3] h2 (by simpa using hmod) (by simpa using hd) prod_s
      (by simp [finrank_W4])
  · exact gram_rank [s1, s2] [s3] h2 (by simpa using hmod) (by simpa using hd) prod_s
      (by simp [finrank_W4])

end CallerSign

#print axioms CallerSign.gram_rank
#print axioms CallerSign.schur_core
#print axioms CallerSign.gram_chart
#print axioms CallerSign.instance_gram
