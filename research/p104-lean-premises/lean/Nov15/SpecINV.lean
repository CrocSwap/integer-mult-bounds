/-
SPECBREAK R43 Lemma INV (involution + unit rank) and Lemma SPLIT, Source: internal notes §1-5, AUDIT43.md. See SpecINV.md.
Builds on Nov15/SpecTSUR.lean (pp, zv, Zm, sum_ZY, UR_lower, ev/jobsP/uconj/ucount, UR_upper).
-/
import Nov15.SpecTSUR
import Mathlib.LinearAlgebra.Matrix.SchurComplement
import Mathlib.FieldTheory.Finite.Basic

open Matrix Finset SpecTSUR

set_option linter.unusedSectionVars false

namespace SpecINV

variable {K : Type*} [Field K]

/-! ## §1. Lemma INV -/
section Inv
variable {n : Type*} [Fintype n] [DecidableEq n]

theorem one_sub_pp (x y : ℕ → n → K) (U : ℕ) :
    1 - pp x y U = Zm x y U * (Matrix.of fun a (i : Fin U) => y i a)ᵀ := by
  rw [pp_eq, sub_sub_cancel, sum_ZY]

/-- **Lemma INV.** char ≠ 2; `g = T_0 ⋯ T_{U-1}` with `T_i = I - x_i y_iᵀ` (transvection, `y_i·x_i = 0`);
`g² = I` ⇒ `rank(I - g) ≤ U - 1`. (Only `y_0·x_0 = 0` is used: the first factor.) -/
theorem inv_rank [DecidableEq K] (h2 : (2 : K) ≠ 0) (U : ℕ) (x y : ℕ → n → K)
    (hq : ∀ i < U, y i ⬝ᵥ x i = 0) (hg : pp x y U * pp x y U = 1) :
    (1 - pp x y U).rank ≤ U - 1 := by
  rcases Nat.eq_zero_or_pos U with rfl | hU
  · simp [pp]
  set Z := Zm x y U with hZ
  set Qm : Matrix n (Fin U) K := Matrix.of fun a (i : Fin U) => y i a with hQm
  have hA : 1 - pp x y U = Z * Qmᵀ := one_sub_pp x y U
  have hle : (1 - pp x y U).rank ≤ U := by
    rw [hA]
    exact (rank_mul_le_left _ _).trans (by simpa using Z.rank_le_card_width)
  by_contra hcon
  have hU' : (1 - pp x y U).rank = U := by omega
  have hrZ : Z.rank = U := by
    have h1 : (1 - pp x y U).rank ≤ Z.rank := by rw [hA]; exact rank_mul_le_left _ _
    have h3 : Z.rank ≤ U := by simpa using Z.rank_le_card_width
    omega
  have hrQ : Qm.rank = U := by
    have h1 : (1 - pp x y U).rank ≤ Qmᵀ.rank := by rw [hA]; exact rank_mul_le_right _ _
    rw [Matrix.rank_transpose] at h1
    have h3 : Qm.rank ≤ U := by simpa using Qm.rank_le_card_width
    omega
  obtain ⟨L, hL⟩ := exists_left_inv Z hrZ
  obtain ⟨L2, hL2⟩ := exists_left_inv Qm hrQ
  have hR : Qmᵀ * L2ᵀ = 1 := by
    rw [← Matrix.transpose_mul, hL2, Matrix.transpose_one]
  have hsq : (1 - pp x y U) * (1 - pp x y U) = (1 - pp x y U) + (1 - pp x y U) := by
    calc (1 - pp x y U) * (1 - pp x y U)
        = 1 - pp x y U - pp x y U + pp x y U * pp x y U := by noncomm_ring
      _ = _ := by rw [hg]; abel
  have hmid : Qmᵀ * Z = 1 + 1 := by
    have e1 : L * ((Z * Qmᵀ) * (Z * Qmᵀ)) * L2ᵀ = Qmᵀ * Z := by
      calc L * ((Z * Qmᵀ) * (Z * Qmᵀ)) * L2ᵀ
          = (L * Z) * (Qmᵀ * Z) * (Qmᵀ * L2ᵀ) := by simp only [Matrix.mul_assoc]
        _ = _ := by rw [hL, hR]; simp
    have e2 : L * ((Z * Qmᵀ) + (Z * Qmᵀ)) * L2ᵀ = 1 + 1 := by
      calc L * ((Z * Qmᵀ) + (Z * Qmᵀ)) * L2ᵀ
          = (L * Z) * (Qmᵀ * L2ᵀ) + (L * Z) * (Qmᵀ * L2ᵀ) := by
            simp only [Matrix.mul_add, Matrix.add_mul, Matrix.mul_assoc]
        _ = _ := by rw [hL, hR]; simp
    rw [← e1, ← e2, ← hA, hsq]
  have h00 := congrFun (congrFun hmid ⟨0, hU⟩) ⟨0, hU⟩
  have hz0 : zv x y 0 = x 0 := by simp [zv, pp]
  have hdot : (Qmᵀ * Z) ⟨0, hU⟩ ⟨0, hU⟩ = y 0 ⬝ᵥ x 0 := by
    simp only [Matrix.mul_apply, hQm, hZ, Zm, Matrix.transpose_apply, Matrix.of_apply, dotProduct]
    simp [hz0]
  rw [hdot, hq 0 hU] at h00
  simp only [Matrix.add_apply, Matrix.one_apply_eq] at h00
  apply h2
  linear_combination -h00


/-! ### cons / shift: from a list of transvections to a `pp` product -/

/-- prepend a vector to a sequence -/
def shift (a : n → K) (x : ℕ → n → K) : ℕ → n → K
  | 0 => a
  | j + 1 => x j

theorem pp_shift (a b : n → K) (x y : ℕ → n → K) (m : ℕ) :
    pp (shift a x) (shift b y) (m + 1) = refl a b * pp x y m := by
  induction m with
  | zero => simp [pp, shift]
  | succ m ih =>
    rw [pp, ih, pp, Matrix.mul_assoc]
    rfl

theorem prod_units_pp (l : List (Matrix n n K)ˣ)
    (h : ∀ t ∈ l, ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = refl a b) :
    ∃ x y : ℕ → n → K, (∀ i < l.length, y i ⬝ᵥ x i = 0) ∧
      ((l.prod : (Matrix n n K)ˣ) : Matrix n n K) = pp x y l.length := by
  induction l with
  | nil => exact ⟨fun _ => 0, fun _ => 0, by simp, by simp [pp]⟩
  | cons t l ih =>
    obtain ⟨a, b, hab, ht⟩ := h t (by simp)
    obtain ⟨x, y, hxy, hp⟩ := ih fun u hu => h u (by simp [hu])
    refine ⟨shift a x, shift b y, ?_, ?_⟩
    · intro i hi
      cases i with
      | zero => simpa [shift] using hab
      | succ j => exact hxy j (by simpa using hi)
    · simp only [List.prod_cons, Units.val_mul, List.length_cons]
      rw [pp_shift, ht, hp]

/-- conjugating a transvection by a unit gives a transvection -/
theorem conj_form (P t : (Matrix n n K)ˣ)
    (h : ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = refl a b) :
    ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ ((P * t * P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = refl a b := by
  obtain ⟨a, b, hab, ht⟩ := h
  refine ⟨(P : Matrix n n K) *ᵥ a, b ᵥ* ((P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K), ?_, ?_⟩
  · rw [Matrix.dotProduct_mulVec, Matrix.vecMul_vecMul]
    have : ((P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) * (P : Matrix n n K) = 1 := P.inv_mul
    rw [this, Matrix.vecMul_one]
    exact hab
  · have hPP : (P : Matrix n n K) * ((P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = 1 := P.mul_inv
    simp only [Units.val_mul, ht, SpecTSUR.refl, mul_sub, sub_mul, Matrix.mul_one, Matrix.mul_vecMulVec,
      Matrix.vecMulVec_mul, hPP]

end Inv

/-! ## §2. INV for words, and the combined bound `d + |k - r₁| ≤ U - 1` -/
section Word
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

theorem uconj_forms : ∀ (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ)) (pre : (Matrix n n K)ˣ),
    (∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = refl a b) →
    ∀ c ∈ uconj w pre, ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (c : Matrix n n K) = refl a b
  | [], _, _ => by simp [uconj]
  | .inl t :: w, pre, h => by
    intro c hc
    simp only [uconj, List.mem_cons] at hc
    rcases hc with rfl | hc
    · exact conj_form pre t (h t (by simp))
    · exact uconj_forms w pre (fun t ht => h t (by simp [ht])) c hc
  | .inr j :: w, pre, h => by
    exact uconj_forms w (pre * j) (fun t ht => h t (by simp [ht]))

/-- **INV for words.** `g = ∏ (conjugated units)` is a product of `U` transvections; if `g² = I` then
`rank(I - g) ≤ U - 1`. -/
theorem inv_word (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = refl a b)
    (hg : (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K) *
      (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K) = 1) :
    (1 - (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K)).rank ≤ ucount w - 1 := by
  obtain ⟨x, y, hxy, hp⟩ := prod_units_pp (uconj w 1) (uconj_forms w 1 hform)
  rw [length_uconj] at hxy hp
  rw [hp] at hg ⊢
  exact inv_rank h2 _ x y hxy hg

/-- `D, J` commuting involutions ⇒ `rank(D - J) ≤ U - 1` (INV applied to `g = D J⁻¹`). -/
theorem inv_DJ (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = refl a b)
    (hD2 : ev w * ev w = 1) (hJ2 : jobsP w * jobsP w = 1) (hc : ev w * jobsP w = jobsP w * ev w) :
    (((ev w : (Matrix n n K)ˣ) : Matrix n n K) - ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)).rank
      ≤ ucount w - 1 := by
  have h1 := ev_move w 1
  simp only [one_mul] at h1
  have hJinv : (jobsP w)⁻¹ = jobsP w := inv_eq_of_mul_eq_one_right hJ2
  have hgu : (uconj w 1).prod = ev w * jobsP w := by
    have : (uconj w 1).prod = ev w * (jobsP w)⁻¹ := eq_mul_inv_of_mul_eq h1.symm
    rw [this, hJinv]
  have hg2 : (uconj w 1).prod * (uconj w 1).prod = 1 := by
    rw [hgu]
    calc ev w * jobsP w * (ev w * jobsP w) = ev w * (jobsP w * ev w) * jobsP w := by group
      _ = ev w * (ev w * jobsP w) * jobsP w := by rw [hc]
      _ = (ev w * ev w) * (jobsP w * jobsP w) := by group
      _ = 1 := by rw [hD2, hJ2]; simp
  have hg2' : (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K) *
      (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K) = 1 := by
    rw [← Units.val_mul, hg2]; rfl
  have hINV := inv_word h2 w hform hg2'
  have e : ((ev w : (Matrix n n K)ˣ) : Matrix n n K) - ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) =
      -((1 - (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K)) *
        ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)) := by
    rw [h1]; simp [sub_mul]
  rw [e, rank_neg_eq]
  exact (rank_mul_le_left _ _).trans hINV

end Word

/-! ## §3. Corollary: `U ≥ 5` for the six R42 survivors -/
section Cor
variable {n₁ nd : Type*} [Fintype n₁] [Fintype nd] [DecidableEq n₁] [DecidableEq nd] [DecidableEq K]

/-- **Corollary (UR_lower + INV).** In the UR_combined setting, if moreover `D, J` are commuting
involutions and the units are transvections, then `d + |k - r₁| ≤ U - 1`. -/
theorem UR_inv_combined (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n₁ → K)
    (hg : ∀ i < k, ∀ j < k, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (s₁ : n₁ → K) (sd : nd → K) (hs₁ : ∀ a, s₁ a = 1 ∨ s₁ a = -1) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (w : List ((Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ ⊕ (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n₁ ⊕ nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) = refl a b)
    (hD : ((ev w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (diagonal s₁) 0 0 (diagonal sd))
    (hJ : ((jobsP w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (pp x y k) 0 0 1)
    (hD2 : ev w * ev w = 1) (hJ2 : jobsP w * jobsP w = 1) (hc : ev w * jobsP w = jobsP w * ev w) :
    (univ.filter fun a => sd a = -1).card +
      ((k - (univ.filter fun a => s₁ a = -1).card) + ((univ.filter fun a => s₁ a = -1).card - k))
    ≤ ucount w - 1 := by
  have hl := UR_lower h2 k x y hg s₁ sd hs₁ hsd
  have hu := inv_DJ h2 w hform hD2 hJ2 hc
  rw [hD, hJ] at hu
  exact hl.trans hu

/-- the arithmetic: bound `4` (both patterns of the six survivors) forces `U ≥ 5`. -/
theorem six_arith (U d k r : ℕ) (hb : d + ((k - r) + (r - k)) ≤ U - 1)
    (h : (d = 1 ∧ k = 3 ∧ r = 0) ∨ (d = 2 ∧ k = 3 ∧ r = 1)) : 5 ≤ U := by
  rcases h with ⟨rfl, rfl, rfl⟩ | ⟨rfl, rfl, rfl⟩ <;> omega

/-- **R26 #10-#14 (pattern d = 1, k = 3, r₁ = 0) and #8 (d = 2, k = 3, r₁ = 1)**: character data as
hypotheses; conclusion `5 ≤ U`, in particular `U = 3, 4` are impossible. -/
theorem six_survivors (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n₁ → K)
    (hg : ∀ i < k, ∀ j < k, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (s₁ : n₁ → K) (sd : nd → K) (hs₁ : ∀ a, s₁ a = 1 ∨ s₁ a = -1) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (w : List ((Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ ⊕ (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n₁ ⊕ nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) = refl a b)
    (hD : ((ev w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (diagonal s₁) 0 0 (diagonal sd))
    (hJ : ((jobsP w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (pp x y k) 0 0 1)
    (hD2 : ev w * ev w = 1) (hJ2 : jobsP w * jobsP w = 1) (hc : ev w * jobsP w = jobsP w * ev w)
    (hpat : ((univ.filter fun a => sd a = -1).card = 1 ∧ k = 3 ∧
        (univ.filter fun a => s₁ a = -1).card = 0) ∨
      ((univ.filter fun a => sd a = -1).card = 2 ∧ k = 3 ∧
        (univ.filter fun a => s₁ a = -1).card = 1)) :
    5 ≤ ucount w :=
  six_arith _ _ _ _ (UR_inv_combined h2 k x y hg s₁ sd hs₁ hsd w hform hD hJ hD2 hJ2 hc) hpat

end Cor

/-! ## §4. Lemma SPLIT (hub job `H` sharing a tight set with every other job)

Tight sets + Lemma TS give the pairing hypotheses `y_H·x_j = 0 = y_j·x_H` (j ≠ H), `y_H·x_H = 2`
(taken as hypotheses below). -/
section Split
variable {n : Type*} [Fintype n] [DecidableEq n]

theorem refl_mulVec (a b v : n → K) : refl a b *ᵥ v = v - (b ⬝ᵥ v) • a := by
  rw [SpecTSUR.refl, sub_mulVec, one_mulVec, vecMulVec_mulVec, op_smul_eq_smul]

theorem vecMul_refl (a b v : n → K) : v ᵥ* refl a b = v - (v ⬝ᵥ a) • b := by
  rw [SpecTSUR.refl, Matrix.vecMul_sub, Matrix.vecMul_one, vecMul_vecMulVec]

/-- the hub vector `x_H`: the ordered product of the jobs sends it to `-x_H` if `H` is among the
first `k` jobs, else fixes it (all other jobs fix `x_H`, `y_H·x_H = 2`). -/
theorem hub_mulVec (x y : ℕ → n → K) (h0 : ℕ) (hh : y h0 ⬝ᵥ x h0 = 2) (k0 : ℕ)
    (hx : ∀ i, i < k0 → i ≠ h0 → y i ⬝ᵥ x h0 = 0) (k : ℕ) (hk0 : k ≤ k0) :
    pp x y k *ᵥ x h0 = if h0 < k then -x h0 else x h0 := by
  induction k with
  | zero => simp [pp]
  | succ k ih =>
    have ih := ih (by omega)
    rw [pp, ← Matrix.mulVec_mulVec, refl_mulVec]
    by_cases hk : k = h0
    · subst hk
      rw [hh, show x k - (2 : K) • x k = -x k by module, Matrix.mulVec_neg, ih]
      simp
    · rw [hx k (by omega) hk, zero_smul, sub_zero, ih]
      have : (h0 < k + 1) ↔ (h0 < k) := by omega
      simp [this]

/-- the hub functional `y_H`: `y_H ᵥ* (ordered product) = ∓ y_H`, so `ker y_H` is `J`-invariant. -/
theorem hub_vecMul (x y : ℕ → n → K) (h0 : ℕ) (hh : y h0 ⬝ᵥ x h0 = 2) (k0 : ℕ)
    (hy : ∀ i, i < k0 → i ≠ h0 → y h0 ⬝ᵥ x i = 0) (k : ℕ) (hk0 : k ≤ k0) :
    y h0 ᵥ* pp x y k = (if h0 < k then (-1 : K) else 1) • y h0 := by
  induction k with
  | zero => simp [pp]
  | succ k ih =>
    have ih := ih (by omega)
    rw [pp, ← Matrix.vecMul_vecMul, ih, Matrix.smul_vecMul, vecMul_refl]
    by_cases hk : k = h0
    · subst hk
      rw [hh]
      simp only [lt_self_iff_false, if_false, Nat.lt_succ_self, if_true]
      module
    · have hlt : (h0 < k + 1) ↔ (h0 < k) := by omega
      simp [hy k (by omega) hk, hlt]


theorem det_refl (a b : n → K) : (refl a b).det = 1 - b ⬝ᵥ a := by
  have : refl a b = 1 + replicateCol Unit (-a) * replicateRow Unit b := by
    rw [← vecMulVec_eq Unit, SpecTSUR.refl, Matrix.neg_vecMulVec, sub_eq_add_neg]
  rw [this, det_one_add_replicateCol_mul_replicateRow, dotProduct_neg]
  ring

/-- `det J = (-1)^k` for `k` reflections with `y_i·x_i = 2` -/
theorem det_pp (x y : ℕ → n → K) (k : ℕ) (hy : ∀ i < k, y i ⬝ᵥ x i = 2) :
    (pp x y k).det = (-1) ^ k := by
  induction k with
  | zero => simp [pp]
  | succ k ih =>
    rw [pp, Matrix.det_mul, ih (fun i hi => hy i (by omega)), det_refl, hy k (by omega), pow_succ]
    ring

variable [DecidableEq K]

theorem rank_zero_mulVec (M : Matrix n n K) (h : M.rank = 0) (v : n → K) : M *ᵥ v = 0 := by
  have h0 := Submodule.finrank_eq_zero.1 (show Module.finrank K (LinearMap.range M.mulVecLin) = 0 from h)
  have hv : M *ᵥ v ∈ LinearMap.range M.mulVecLin := ⟨v, rfl⟩
  rw [h0] at hv
  simpa using hv

theorem eps_mulVec (J : Matrix n n K) (h : n → K) (σ ε : K) (hJh : J *ᵥ h = σ • h) :
    ((ε • 1 - J : Matrix n n K)) *ᵥ h = (ε - σ) • h := by
  rw [sub_mulVec, Matrix.smul_mulVec, one_mulVec, hJh]; module

/-- **SPLIT key.** If `rank(ε - J) ≤ 1` and `ε ≠ σ` then `ε - J` is the rank-one matrix
`((ε - σ)/2) x_H y_Hᵀ`. -/
theorem split_key (h2 : (2 : K) ≠ 0) (J : Matrix n n K) (h η : n → K) (σ ε : K)
    (hηh : η ⬝ᵥ h = 2) (hJh : J *ᵥ h = σ • h) (hηJ : η ᵥ* J = σ • η)
    (hεσ : ε ≠ σ) (hr : ((ε • 1 - J : Matrix n n K)).rank ≤ 1) :
    (ε • 1 - J : Matrix n n K) = vecMulVec (((ε - σ) / 2) • h) η := by
  set M : Matrix n n K := ε • 1 - J with hM
  have hMh : M *ᵥ h = (ε - σ) • h := eps_mulVec J h σ ε hJh
  have hh0 : h ≠ 0 := by
    rintro rfl
    simp at hηh
    exact h2 hηh.symm
  have hεσ' : ε - σ ≠ 0 := sub_ne_zero.2 hεσ
  have hw0 : M *ᵥ h ≠ 0 := by rw [hMh]; exact smul_ne_zero hεσ' hh0
  have hspan : Submodule.span K {M *ᵥ h} = LinearMap.range M.mulVecLin := by
    apply Submodule.eq_of_le_of_finrank_le
    · rw [Submodule.span_singleton_le_iff_mem]; exact ⟨h, rfl⟩
    · rw [finrank_span_singleton hw0]; exact hr
  rw [Matrix.ext_iff_mulVec]
  intro v
  set v' : n → K := v - ((η ⬝ᵥ v) / 2) • h with hv'def
  have hv' : η ⬝ᵥ v' = 0 := by
    rw [hv'def, dotProduct_sub, dotProduct_smul, hηh]
    simp only [smul_eq_mul]; field_simp; ring
  have hMv' : M *ᵥ v' ∈ Submodule.span K {M *ᵥ h} := by rw [hspan]; exact ⟨v', rfl⟩
  obtain ⟨c, hc⟩ := Submodule.mem_span_singleton.1 hMv'
  have hη0 : η ⬝ᵥ (M *ᵥ v') = 0 := by
    rw [hM, sub_mulVec, dotProduct_sub, Matrix.smul_mulVec, one_mulVec, dotProduct_smul,
      Matrix.dotProduct_mulVec, hηJ, smul_dotProduct, hv']
    simp
  have hcc : c * ((ε - σ) * 2) = 0 := by
    have := hη0
    rw [← hc, dotProduct_smul, hMh, dotProduct_smul, hηh] at this
    simpa [smul_eq_mul, mul_assoc] using this
  have hc0 : c = 0 := by
    rcases mul_eq_zero.1 hcc with h | h
    · exact h
    · rcases mul_eq_zero.1 h with h | h
      · exact absurd h hεσ'
      · exact absurd h h2
  have hMv'0 : M *ᵥ v' = 0 := by rw [← hc, hc0, zero_smul]
  have hv : v = v' + ((η ⬝ᵥ v) / 2) • h := by rw [hv'def]; abel
  have hMv : M *ᵥ v = ((η ⬝ᵥ v) / 2) • ((ε - σ) • h) := by
    conv_lhs => rw [hv]
    rw [Matrix.mulVec_add, hMv'0, Matrix.mulVec_smul, hMh, zero_add]
  rw [hMv, vecMulVec_mulVec]
  simp only [op_smul_eq_smul, smul_smul, smul_eq_mul]
  congr 1
  ring

/-- determinant of the rank-one `J` produced by `split_key`: `det J · ε = σ ε^N`. -/
theorem split_det (h2 : (2 : K) ≠ 0) (J : Matrix n n K) (h η : n → K) (σ ε : K)
    (hηh : η ⬝ᵥ h = 2) (hε : ε ≠ 0)
    (hM : (ε • 1 - J : Matrix n n K) = vecMulVec (((ε - σ) / 2) • h) η) :
    J.det * ε = σ * ε ^ Fintype.card n := by
  have hJ : J = ε • (1 + replicateCol Unit ((-((ε - σ) / 2 / ε)) • h) * replicateRow Unit η) := by
    have h1 : J = ε • 1 - vecMulVec (((ε - σ) / 2) • h) η := by
      rw [← hM]; abel
    rw [← vecMulVec_eq Unit, h1]
    ext i j
    by_cases hij : i = j
    · subst hij
      simp only [Matrix.sub_apply, Matrix.smul_apply, Matrix.one_apply_eq, vecMulVec_apply,
        Pi.smul_apply, smul_eq_mul, Matrix.add_apply, Pi.neg_apply]
      field_simp
      ring
    · simp only [Matrix.sub_apply, Matrix.smul_apply, Matrix.one_apply_ne hij, vecMulVec_apply,
        Pi.smul_apply, smul_eq_mul, Matrix.add_apply, Pi.neg_apply]
      field_simp
      ring
  rw [hJ, Matrix.det_smul, det_one_add_replicateCol_mul_replicateRow, dotProduct_smul, hηh]
  simp only [smul_eq_mul]
  field_simp
  ring


/-- **Lemma SPLIT (rank form).** Hub vector `h = x_H`, hub functional `η = y_H` (`η·h = 2`), `J h = σ h`,
`η J = σ η` (so `V = ⟨x_H⟩ ⊕ ker η`, both `J`-invariant). For a scalar `D = ε ≠ 0`:
`rank(ε - J) ≥ [x_H term: ε ≠ σ] + [det term: det J ≠ σ ε^{N-1}, written as `det J · ε ≠ σ ε^N`]`. -/
theorem split_rank_ge (h2 : (2 : K) ≠ 0) (J : Matrix n n K) (h η : n → K) (σ ε : K)
    (hηh : η ⬝ᵥ h = 2) (hJh : J *ᵥ h = σ • h) (hηJ : η ᵥ* J = σ • η) (hε : ε ≠ 0) :
    (if ε ≠ σ then 1 else 0) + (if J.det * ε ≠ σ * ε ^ Fintype.card n then 1 else 0)
      ≤ (ε • 1 - J : Matrix n n K).rank := by
  have hh0 : h ≠ 0 := by
    rintro rfl
    simp at hηh
    exact h2 hηh.symm
  by_cases ha : ε = σ
  · subst ha
    by_cases hb : J.det * ε ≠ ε * ε ^ Fintype.card n
    · simp only [ne_eq, not_true_eq_false, if_false, hb, not_false_eq_true, if_true, zero_add]
      by_contra hcon
      have h0 : (ε • 1 - J : Matrix n n K).rank = 0 := by omega
      have hz : (ε • 1 - J : Matrix n n K) = 0 :=
        Matrix.ext_iff_mulVec.2 fun v => by simpa using rank_zero_mulVec _ h0 v
      have hJ : J = ε • 1 := by rw [← sub_eq_zero, ← neg_sub, hz, neg_zero]
      apply hb
      rw [hJ, Matrix.det_smul]; simp; ring
    · simp [hb]
  · by_cases hb : J.det * ε ≠ σ * ε ^ Fintype.card n
    · rw [if_pos ha, if_pos hb]
      by_contra hcon
      have hr : (ε • 1 - J : Matrix n n K).rank ≤ 1 := by omega
      exact hb (split_det h2 J h η σ ε hηh hε (split_key h2 J h η σ ε hηh hJh hηJ ha hr))
    · rw [if_pos ha, if_neg hb]
      by_contra hcon
      have h0 : (ε • 1 - J : Matrix n n K).rank = 0 := by omega
      have := rank_zero_mulVec _ h0 h
      rw [eps_mulVec J h σ ε hJh] at this
      exact smul_ne_zero (sub_ne_zero.2 ha) hh0 this


/-- hub data ⇒ `J h = σ h`, `η J = σ η` and `det J = (-1)^k` for `J = pp x y k`. -/
theorem hub_data (x y : ℕ → n → K) (h0 k : ℕ) (hh : y h0 ⬝ᵥ x h0 = 2)
    (hx : ∀ i, i < k → i ≠ h0 → y i ⬝ᵥ x h0 = 0) (hy : ∀ i, i < k → i ≠ h0 → y h0 ⬝ᵥ x i = 0)
    (hk : ∀ i, i < k → y i ⬝ᵥ x i = 2) :
    pp x y k *ᵥ x h0 = (if h0 < k then (-1 : K) else 1) • x h0 ∧
    y h0 ᵥ* pp x y k = (if h0 < k then (-1 : K) else 1) • y h0 ∧
    (pp x y k).det = (-1) ^ k := by
  refine ⟨?_, hub_vecMul x y h0 hh k hy k le_rfl, det_pp x y k hk⟩
  rw [hub_mulVec x y h0 hh k hx k le_rfl]
  split_ifs <;> simp

end Split

section SplitDJ
variable {n₁ nd : Type*} [Fintype n₁] [Fintype nd] [DecidableEq n₁] [DecidableEq nd] [DecidableEq K]

/-- **SPLIT on `V₁ ⊕ dark`.** `D = ε ⊕ diag sd`, `J = (ordered product of the `k` active jobs) ⊕ I`; hub job
`h0` pairs trivially with all other active jobs. Then `rank(D - J) ≥ d + [ε ≠ σ] + [det term]`,
`σ = -1` iff `H` is active. -/
theorem split_DJ_rank (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n₁ → K) (h0 : ℕ)
    (hh : y h0 ⬝ᵥ x h0 = 2)
    (hx : ∀ i, i < k → i ≠ h0 → y i ⬝ᵥ x h0 = 0) (hy : ∀ i, i < k → i ≠ h0 → y h0 ⬝ᵥ x i = 0)
    (hk : ∀ i, i < k → y i ⬝ᵥ x i = 2) (ε : K) (hε : ε = 1 ∨ ε = -1)
    (sd : nd → K) (hsd : ∀ a, sd a = 1 ∨ sd a = -1) :
    (univ.filter fun a => sd a = -1).card +
      ((if ε ≠ (if h0 < k then (-1 : K) else 1) then 1 else 0) +
       (if (-1) ^ k * ε ≠ (if h0 < k then (-1 : K) else 1) * ε ^ Fintype.card n₁ then 1 else 0))
    ≤ (fromBlocks (ε • (1 : Matrix n₁ n₁ K)) 0 0 (diagonal sd) -
        fromBlocks (pp x y k) 0 0 1).rank := by
  have hε0 : ε ≠ 0 := by rcases hε with rfl | rfl <;> simp
  obtain ⟨h1, h2', h3⟩ := hub_data x y h0 k hh hx hy hk
  have hsp := split_rank_ge h2 (pp x y k) (x h0) (y h0) _ ε hh h1 h2' hε0
  rw [h3] at hsp
  have hBr : ((diagonal sd : Matrix nd nd K) - 1).rank = (univ.filter fun a => sd a = -1).card := by
    rw [← neg_sub, rank_neg_eq]; exact rank_one_sub_diag h2 sd hsd
  have eD : fromBlocks (ε • (1 : Matrix n₁ n₁ K)) 0 0 (diagonal sd) - fromBlocks (pp x y k) 0 0 1 =
      fromBlocks (ε • 1 - pp x y k) 0 0 (diagonal sd - 1) := by
    ext (i | i) (j | j) <;> simp
  rw [eD]
  have := rank_fromBlocks_diag_ge (ε • 1 - pp x y k) ((diagonal sd : Matrix nd nd K) - 1)
  omega

/-- **R26 #2 (hub E) and #3 (hub F)**, `d = 2` dark targets, `V₁` of dimension 3. The surviving
characters are of two shapes: `H ∉ S` (`k = 3`, `ε = -1`, `H` index ≥ k; μ = 1, 6 resp. 9, 14) and
`H ∈ S` (`k = 4`, `ε = +1`; μ = 11, 12). Character data as hypotheses; `rank(D - J) ≥ 4`, so `U ≥ 4`
(`U = 3` dead). -/
theorem split_R26_2_3 (h2 : (2 : K) ≠ 0) (hcard : Fintype.card n₁ = 3) (k : ℕ)
    (x y : ℕ → n₁ → K) (h0 : ℕ) (hh : y h0 ⬝ᵥ x h0 = 2)
    (hx : ∀ i, i < k → i ≠ h0 → y i ⬝ᵥ x h0 = 0) (hy : ∀ i, i < k → i ≠ h0 → y h0 ⬝ᵥ x i = 0)
    (hk : ∀ i, i < k → y i ⬝ᵥ x i = 2) (ε : K) (sd : nd → K) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (hd : (univ.filter fun a => sd a = -1).card = 2)
    (hpat : (k = 3 ∧ 3 ≤ h0 ∧ ε = -1) ∨ (k = 4 ∧ h0 < 4 ∧ ε = 1)) :
    4 ≤ (fromBlocks (ε • (1 : Matrix n₁ n₁ K)) 0 0 (diagonal sd) -
        fromBlocks (pp x y k) 0 0 1).rank := by
  have hε : ε = 1 ∨ ε = -1 := by rcases hpat with ⟨_, _, h⟩ | ⟨_, _, h⟩ <;> simp [h]
  have hb := split_DJ_rank h2 k x y h0 hh hx hy hk ε hε sd hsd
  have hne : (1 : K) ≠ -1 := by intro h; apply h2; linear_combination h
  have hne' : (-1 : K) ≠ 1 := fun h => hne h.symm
  rw [hd, hcard] at hb
  rcases hpat with ⟨rfl, h3, rfl⟩ | ⟨rfl, h4, rfl⟩
  · have hlt : ¬ h0 < 3 := by omega
    have hA : (-1 : K) ≠ 1 := hne'
    have hB : (-1 : K) ^ 3 * -1 ≠ 1 * (-1) ^ 3 := by
      intro h; apply h2; linear_combination h
    rw [if_neg hlt, if_pos hA, if_pos hB] at hb
    omega
  · have hA : (1 : K) ≠ -1 := hne
    have hB : (-1 : K) ^ 4 * 1 ≠ -1 * 1 ^ 3 := by
      intro h; apply h2; linear_combination h
    rw [if_pos h4, if_pos hA, if_pos hB] at hb
    omega

end SplitDJ

/-! ## §5. The `U = 4` equality step (R43 item 4, audit §3): `K` of dimension 2, eigenvalues `ε` and
`det/ε` distinct ⇒ `J_K` involution ⇒ `g` involution ⇒ INV. Formalised in coordinates adapted to
`V₁ = ⟨x_H⟩ ⊕ K` (`Fin 1 ⊕ Fin 2`), where `J = σ ⊕ J_K ⊕ I_dark`. -/
section Equality
variable [DecidableEq K]

/-- a `2×2` matrix with `det = -1` and `rank(ε - J) ≤ 1`, `ε = ±1`, is an involution. -/
theorem two_by_two_invol (h2 : (2 : K) ≠ 0) (J : Matrix (Fin 2) (Fin 2) K) (ε : K)
    (hε : ε = 1 ∨ ε = -1) (hdet : J.det = -1) (hr : (ε • 1 - J : Matrix (Fin 2) (Fin 2) K).rank ≤ 1) :
    J * J = 1 := by
  have hε2 : ε * ε = 1 := by rcases hε with rfl | rfl <;> norm_num
  have hd0 : (ε • 1 - J : Matrix (Fin 2) (Fin 2) K).det = 0 := by
    by_contra hne
    have hu : IsUnit (ε • 1 - J : Matrix (Fin 2) (Fin 2) K) :=
      (Matrix.isUnit_iff_isUnit_det _).2 (isUnit_iff_ne_zero.2 hne)
    have := Matrix.rank_of_isUnit _ hu
    simp at this
    omega
  rw [Matrix.det_fin_two] at hd0 hdet
  simp only [Matrix.sub_apply, Matrix.smul_apply, Matrix.one_apply_eq, Matrix.one_apply_ne,
    ne_eq, Fin.zero_eq_one_iff, OfNat.ofNat_ne_one, not_false_eq_true, Fin.one_eq_zero_iff,
    smul_eq_mul, mul_one, mul_zero, zero_sub] at hd0
  have hkey : ε * (J 0 0 + J 1 1) = 0 := by linear_combination (-1) * hd0 + hε2 + hdet
  have hsum : J 0 0 + J 1 1 = 0 := by
    have : ε ≠ 0 := by rintro rfl; simp at hε2
    exact (mul_eq_zero.1 hkey).resolve_left this
  ext i j
  fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Fin.sum_univ_two]
  · linear_combination (J 0 0) * hsum - hdet
  · linear_combination (J 0 1) * hsum
  · linear_combination (J 1 0) * hsum
  · linear_combination (J 1 1) * hsum - hdet


theorem rank_scalar_one (c : K) (hc : c ≠ 0) :
    ((c • 1 : Matrix (Fin 1) (Fin 1) K)).rank = 1 := by
  have hu : IsUnit (c • 1 : Matrix (Fin 1) (Fin 1) K) := by
    rw [Matrix.isUnit_iff_isUnit_det]; simp [hc]
  simpa using Matrix.rank_of_isUnit _ hu

theorem rank_ge_one_of_ne (JK : Matrix (Fin 2) (Fin 2) K) (ε : K) (hb : JK.det ≠ ε ^ 2) :
    1 ≤ (ε • 1 - JK : Matrix (Fin 2) (Fin 2) K).rank := by
  by_contra hcon
  have h0 : (ε • 1 - JK : Matrix (Fin 2) (Fin 2) K).rank = 0 := by omega
  have hz : (ε • 1 - JK : Matrix (Fin 2) (Fin 2) K) = 0 :=
    Matrix.ext_iff_mulVec.2 fun v => by simpa using rank_zero_mulVec _ h0 v
  have hJ : JK = ε • 1 := by rw [← sub_eq_zero, ← neg_sub, hz, neg_zero]
  apply hb
  rw [hJ, Matrix.det_smul]; simp

section U4
variable {nd : Type*} [Fintype nd] [DecidableEq nd]

/-- **LEMMA SPLIT, `U = 4` equality step** (R26 #2 / #3, `d = 2`), in coordinates adapted to
`V₁ = ⟨x_H⟩ ⊕ K` (`Fin 1 ⊕ Fin 2`): `D = ε ⊕ diag sd`, `J = (σ ⊕ J_K) ⊕ I`, `ε ≠ σ` (x_H term),
`det J_K ≠ ε^{dim K}` (det term). If `U = d + 2` the word cannot exist: the slack forces
`rank(ε - J_K) ≤ 1`, so `J_K² = I` (`two_by_two_invol`), `g` is an involution, and INV gives
`rank(D - J) ≤ U - 1 = d + 1 < d + 2`. -/
theorem split_U4 (h2 : (2 : K) ≠ 0) (σ ε : K) (hσ : σ = 1 ∨ σ = -1) (hε : ε = 1 ∨ ε = -1)
    (hεσ : ε ≠ σ) (JK : Matrix (Fin 2) (Fin 2) K) (hdetK : JK.det = 1 ∨ JK.det = -1)
    (hb : JK.det ≠ ε ^ 2) (sd : nd → K) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (w : List ((Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K)ˣ ⊕
      (Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : (Fin 1 ⊕ Fin 2) ⊕ nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K) = refl a b)
    (hD : ((ev w : (Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K)ˣ) :
        Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K) =
      fromBlocks (ε • (1 : Matrix (Fin 1 ⊕ Fin 2) (Fin 1 ⊕ Fin 2) K)) 0 0 (diagonal sd))
    (hJ : ((jobsP w : (Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K)ˣ) :
        Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K) =
      fromBlocks (fromBlocks (σ • (1 : Matrix (Fin 1) (Fin 1) K)) 0 0 JK) 0 0 1) :
    ucount w ≠ (univ.filter fun a => sd a = -1).card + 2 := by
  intro hU
  have hσσ : σ * σ = 1 := by rcases hσ with rfl | rfl <;> norm_num
  have hεε : ε * ε = 1 := by rcases hε with rfl | rfl <;> norm_num
  have hsd2 : ∀ a, sd a * sd a = 1 := fun a => by rcases hsd a with h | h <;> rw [h] <;> norm_num
  have hε0 : ε ≠ 0 := by rintro rfl; simp at hεε
  have hεσ' : ε - σ ≠ 0 := sub_ne_zero.2 hεσ
  have hunits : ∀ t, Sum.inl t ∈ w → ((t : Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K) - 1).rank ≤ 1 := by
    intro t ht
    obtain ⟨a, b, -, hab⟩ := hform t ht
    have : (t : Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K) - 1 = -vecMulVec a b := by
      rw [hab, SpecTSUR.refl]; abel
    rw [this, rank_neg_eq]
    exact rank_vecMulVec_le a b
  have hup := UR_upper w hunits
  rw [hD, hJ, hU] at hup
  have hBr : ((diagonal sd : Matrix nd nd K) - 1).rank = (univ.filter fun a => sd a = -1).card := by
    rw [← neg_sub, rank_neg_eq]; exact rank_one_sub_diag h2 sd hsd
  have e1 : (ε • (1 : Matrix (Fin 1 ⊕ Fin 2) (Fin 1 ⊕ Fin 2) K) -
      fromBlocks (σ • (1 : Matrix (Fin 1) (Fin 1) K)) 0 0 JK) =
      fromBlocks ((ε - σ) • (1 : Matrix (Fin 1) (Fin 1) K)) 0 0 (ε • 1 - JK) := by
    ext (i | i) (j | j) <;> simp [Matrix.one_apply, sub_smul]
  have eD : fromBlocks (ε • (1 : Matrix (Fin 1 ⊕ Fin 2) (Fin 1 ⊕ Fin 2) K)) 0 0 (diagonal sd) -
      fromBlocks (fromBlocks (σ • (1 : Matrix (Fin 1) (Fin 1) K)) 0 0 JK) 0 0 1 =
      fromBlocks (fromBlocks ((ε - σ) • (1 : Matrix (Fin 1) (Fin 1) K)) 0 0 (ε • 1 - JK)) 0 0
        (diagonal sd - 1) := by
    rw [← e1]; ext (i | i) (j | j) <;> simp
  have hr1 := rank_fromBlocks_diag_ge ((ε - σ) • (1 : Matrix (Fin 1) (Fin 1) K)) (ε • 1 - JK)
  have hr2 := rank_fromBlocks_diag_ge
    (fromBlocks ((ε - σ) • (1 : Matrix (Fin 1) (Fin 1) K)) 0 0 (ε • 1 - JK))
    ((diagonal sd : Matrix nd nd K) - 1)
  rw [eD] at hup
  have hr3 := rank_scalar_one (ε - σ) hεσ'
  have hK1 : (ε • 1 - JK : Matrix (Fin 2) (Fin 2) K).rank ≤ 1 := by omega
  have hdet : JK.det = -1 := by
    rcases hdetK with h | h
    · exfalso; apply hb; rw [h]; rcases hε with rfl | rfl <;> norm_num
    · exact h
  have hJK : JK * JK = 1 := two_by_two_invol h2 JK ε hε hdet hK1
  have hJ2 : jobsP w * jobsP w = 1 := by
    apply Units.ext
    rw [Units.val_mul, hJ]
    simp [Matrix.fromBlocks_multiply, hJK, smul_smul, hσσ]
  have hD2 : ev w * ev w = 1 := by
    apply Units.ext
    rw [Units.val_mul, hD]
    simp only [Matrix.fromBlocks_multiply, Matrix.zero_mul, Matrix.mul_zero, add_zero,
      Matrix.smul_mul, Matrix.mul_smul, Matrix.one_mul, smul_smul, hεε, one_smul,
      Matrix.diagonal_mul_diagonal]
    have : (fun a => sd a * sd a) = fun _ => (1 : K) := funext hsd2
    simp [this]
  have hc : ev w * jobsP w = jobsP w * ev w := by
    apply Units.ext
    rw [Units.val_mul, Units.val_mul, hD, hJ]
    simp [Matrix.fromBlocks_multiply, Matrix.smul_mul, Matrix.mul_smul]
  have hinv := inv_DJ h2 w hform hD2 hJ2 hc
  rw [hD, hJ, hU] at hinv
  have hne : 1 ≤ (ε • 1 - JK : Matrix (Fin 2) (Fin 2) K).rank := rank_ge_one_of_ne JK ε hb
  rw [eD] at hinv
  omega

end U4
end Equality

/-! ## §6. Necessity of the hypotheses (counterexamples) -/
section Sanity
open Matrix

instance : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

/-- `y·x = 0` cannot be dropped: `1 - 2·[1]` over ℚ (`n = Fin 1`) is an involution with
`rank(I - g) = 1 > U - 1 = 0`. -/
theorem inv_needs_transvection : ∃ (x y : ℕ → Fin 1 → ℚ),
    y 0 ⬝ᵥ x 0 ≠ 0 ∧ pp x y 1 * pp x y 1 = 1 ∧ ¬ (1 - pp x y 1).rank ≤ 1 - 1 := by
  refine ⟨fun _ => ![1], fun _ => ![2], by simp [dotProduct], ?_, ?_⟩
  · ext i j; fin_cases i; fin_cases j
    simp [pp, SpecTSUR.refl, Matrix.mul_apply, vecMulVec_apply]; norm_num
  · intro h
    have h0 : (1 - pp (fun _ => ![1]) (fun _ => (![2] : Fin 1 → ℚ)) 1 : Matrix (Fin 1) (Fin 1) ℚ).rank = 0 := by
      omega
    have := rank_zero_mulVec _ h0 ![1]
    have h1 := congrFun this 0
    simp [pp, SpecTSUR.refl, mulVec, dotProduct, vecMulVec_apply] at h1

/-- `char ≠ 2` cannot be dropped: over `ZMod 2`, `x = e₀, y = e₁` (`y·x = 0`), `g = I - x yᵀ` is an
involution with `rank(I - g) = 1 > U - 1 = 0`. -/
theorem inv_needs_char : ∃ (x y : ℕ → Fin 2 → ZMod 2),
    y 0 ⬝ᵥ x 0 = 0 ∧ pp x y 1 * pp x y 1 = 1 ∧ ¬ (1 - pp x y 1).rank ≤ 1 - 1 := by
  refine ⟨fun _ => ![1, 0], fun _ => ![0, 1], by simp [dotProduct, Fin.sum_univ_two], ?_, ?_⟩
  · ext i j; fin_cases i <;> fin_cases j <;>
      simp [pp, SpecTSUR.refl, Matrix.mul_apply, vecMulVec_apply, Fin.sum_univ_two] <;> decide
  · intro h
    have h0 : (1 - pp (fun _ => (![1, 0] : Fin 2 → ZMod 2)) (fun _ => (![0, 1] : Fin 2 → ZMod 2)) 1 :
        Matrix (Fin 2) (Fin 2) (ZMod 2)).rank = 0 := by omega
    have := rank_zero_mulVec _ h0 ![0, 1]
    have h1 := congrFun this 0
    simp [pp, SpecTSUR.refl, mulVec, dotProduct, vecMulVec_apply, Fin.sum_univ_two] at h1

end Sanity

/-! ## §7. `split_U4` basis-free: the change of basis 
`split_U4` is stated in coordinates adapted to `V₁ = ⟨x_H⟩ ⊕ K ⊕ dark`.  Here: `Phi B` (coordinates in a
basis `B` of `n → K`, an algebra equivalence), transport of words (`mapW`), the adapted-basis form
`split_U4_basis`, and the basis-free form `split_U4_free`, which BUILDS the adapted basis from the
decomposition `DirectSum.IsInternal ![A, K₀, W]`. -/
section BasisFree
open Module

section BasisChange
variable {n : Type*} [Fintype n] [DecidableEq n] {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- coordinates of a matrix in the basis `B` of `n → K` -/
noncomputable def Phi (B : Basis ι K (n → K)) : Matrix n n K ≃ₐ[K] Matrix ι ι K :=
  (Matrix.toLinAlgEquiv' (R := K) (n := n)).trans (LinearMap.toMatrixAlgEquiv B)

theorem Phi_apply (B : Basis ι K (n → K)) (M : Matrix n n K) (i j : ι) :
    Phi B M i j = B.repr (M *ᵥ B j) i := by
  simp [Phi, LinearMap.toMatrixAlgEquiv_apply, LinearMap.toMatrix_apply]


theorem Phi_of_eigen (B : Basis ι K (n → K)) (M : Matrix n n K) (c : ι → K)
    (h : ∀ j, M *ᵥ B j = c j • B j) : Phi B M = diagonal c := by
  ext i j
  rw [Phi_apply, h, map_smul]
  by_cases hij : i = j
  · subst hij; simp
  · simp [Matrix.diagonal_apply, Finsupp.single_apply, hij, Ne.symm hij]

theorem Phi_refl (B : Basis ι K (n → K)) (a β : n → K) :
    Phi B (refl a β) = refl (fun i => B.repr a i) (fun j => β ⬝ᵥ B j) := by
  ext i j
  rw [Phi_apply, refl_mulVec]
  simp [SpecTSUR.refl, vecMulVec_apply, Matrix.one_apply, Finsupp.single_apply, eq_comm, mul_comm]

theorem dot_Phi (B : Basis ι K (n → K)) (a β : n → K) :
    (fun j => β ⬝ᵥ B j) ⬝ᵥ (fun i => B.repr a i) = β ⬝ᵥ a := by
  have h1 : β ⬝ᵥ a = ∑ i, B.repr a i * (β ⬝ᵥ B i) := by
    conv_lhs => rw [← B.sum_repr a]
    rw [dotProduct_sum]; simp [dotProduct_smul]
  rw [h1]; simp [dotProduct, mul_comm]


/-! word transport along a monoid hom -/
def mapW {G H : Type*} (f : G → H) : List (G ⊕ G) → List (H ⊕ H)
  | [] => []
  | .inl a :: w => .inl (f a) :: mapW f w
  | .inr a :: w => .inr (f a) :: mapW f w

theorem ev_mapW {G H : Type*} [Group G] [Group H] (f : G →* H) :
    ∀ w : List (G ⊕ G), ev (mapW f w) = f (ev w)
  | [] => by simp [mapW, ev]
  | .inl a :: w => by simp [mapW, ev, ev_mapW f w]
  | .inr a :: w => by simp [mapW, ev, ev_mapW f w]

theorem jobsP_mapW {G H : Type*} [Group G] [Group H] (f : G →* H) :
    ∀ w : List (G ⊕ G), jobsP (mapW f w) = f (jobsP w)
  | [] => by simp [mapW, jobsP]
  | .inl a :: w => by simp [mapW, jobsP, jobsP_mapW f w]
  | .inr a :: w => by simp [mapW, jobsP, jobsP_mapW f w]

theorem ucount_mapW {G H : Type*} (f : G → H) :
    ∀ w : List (G ⊕ G), ucount (mapW f w) = ucount w
  | [] => by simp [mapW, ucount]
  | .inl a :: w => by simp [mapW, ucount, ucount_mapW f w]
  | .inr a :: w => by simp [mapW, ucount, ucount_mapW f w]

theorem mem_mapW {G H : Type*} (f : G → H) :
    ∀ (w : List (G ⊕ G)) (t' : H), Sum.inl t' ∈ mapW f w → ∃ t, Sum.inl t ∈ w ∧ t' = f t
  | [], t', h => by simp [mapW] at h
  | .inl a :: w, t', h => by
    simp only [mapW, List.mem_cons, Sum.inl.injEq, reduceCtorEq, or_false] at h
    rcases h with h | h
    · exact ⟨a, by simp, h⟩
    · obtain ⟨t, ht, e⟩ := mem_mapW f w t' h
      exact ⟨t, by simp [ht], e⟩
  | .inr a :: w, t', h => by
    simp only [mapW, List.mem_cons, reduceCtorEq, false_or] at h
    obtain ⟨t, ht, e⟩ := mem_mapW f w t' h
    exact ⟨t, by simp [ht], e⟩


end BasisChange

section BasisU4
variable {n : Type*} [Fintype n] [DecidableEq n] {nd : Type*} [Fintype nd] [DecidableEq nd] [DecidableEq K]

theorem split_U4_basis (h2 : (2 : K) ≠ 0) (σ ε : K) (hσ : σ = 1 ∨ σ = -1) (hε : ε = 1 ∨ ε = -1)
    (hεσ : ε ≠ σ) (B : Basis ((Fin 1 ⊕ Fin 2) ⊕ nd) K (n → K))
    (JK : Matrix (Fin 2) (Fin 2) K) (hdetK : JK.det = 1 ∨ JK.det = -1)
    (hb : JK.det ≠ ε ^ 2) (sd : nd → K) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = refl a b)
    (hD1 : ∀ i, ((ev w : (Matrix n n K)ˣ) : Matrix n n K) *ᵥ B (Sum.inl i) = ε • B (Sum.inl i))
    (hD2 : ∀ a, ((ev w : (Matrix n n K)ˣ) : Matrix n n K) *ᵥ B (Sum.inr a) = sd a • B (Sum.inr a))
    (hJ1 : ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) *ᵥ B (Sum.inl (Sum.inl 0)) = σ • B (Sum.inl (Sum.inl 0)))
    (hJ2 : ∀ j, ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) *ᵥ B (Sum.inl (Sum.inr j)) =
      ∑ i, JK i j • B (Sum.inl (Sum.inr i)))
    (hJ3 : ∀ a, ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) *ᵥ B (Sum.inr a) = B (Sum.inr a)) :
    ucount w ≠ (univ.filter fun a => sd a = -1).card + 2 := by
  let f : (Matrix n n K)ˣ →* (Matrix ((Fin 1 ⊕ Fin 2) ⊕ nd) ((Fin 1 ⊕ Fin 2) ⊕ nd) K)ˣ :=
    Units.map (Phi B : Matrix n n K →* _)
  have hf : ∀ u : (Matrix n n K)ˣ, (f u : Matrix _ _ K) = Phi B (u : Matrix n n K) := fun u => rfl
  have key := split_U4 h2 σ ε hσ hε hεσ JK hdetK hb sd hsd (mapW f w) ?_ ?_ ?_
  · rwa [ucount_mapW] at key
  · intro t' ht'
    obtain ⟨t, ht, rfl⟩ := mem_mapW f w t' ht'
    obtain ⟨a, β, hβ, hab⟩ := hform t ht
    refine ⟨fun i => B.repr a i, fun j => β ⬝ᵥ B j, ?_, ?_⟩
    · rw [dot_Phi]; exact hβ
    · rw [hf, hab, Phi_refl]
  · rw [ev_mapW, hf]
    have := Phi_of_eigen B ((ev w : (Matrix n n K)ˣ) : Matrix n n K) (Sum.elim (fun _ => ε) sd) (by
      rintro (i | a)
      · simpa using hD1 i
      · simpa using hD2 a)
    rw [this]
    ext (i | i) (j | j) <;> simp [Matrix.diagonal_apply, Matrix.one_apply]
  · rw [jobsP_mapW, hf]
    ext i j
    rw [Phi_apply]
    rcases j with (j | j) | j
    · obtain rfl : j = 0 := Subsingleton.elim _ _
      rw [hJ1]
      rcases i with (i | i) | i
      · obtain rfl : i = 0 := Subsingleton.elim _ _
        simp
      · simp
      · simp
    · rw [hJ2]
      rcases i with (i | i) | i
      · simp
      · simp [Finsupp.single_apply]
        fin_cases i <;> simp
      · simp
    · rw [hJ3]
      rcases i with (i | i) | i
      · simp
      · simp
      · simp [Finsupp.single_apply, Matrix.one_apply, eq_comm]

end BasisU4

/-! ### From a direct-sum decomposition to an adapted basis -/
section Free
variable {n : Type*} [Fintype n] [DecidableEq n] {nd : Type} [Fintype nd] [DecidableEq nd] [DecidableEq K]

/-- index bookkeeping: `(Fin 1 ⊕ Fin 2) ⊕ nd ≃ Σ i : Fin 3, ![Fin 1, Fin 2, nd] i` -/
def idxEquiv (nd : Type) : ((Fin 1 ⊕ Fin 2) ⊕ nd) ≃ Σ i : Fin 3, (![Fin 1, Fin 2, nd] i) where
  toFun := Sum.elim (Sum.elim (fun a => ⟨0, a⟩) (fun a => ⟨1, a⟩)) (fun a => ⟨2, a⟩)
  invFun := fun p => match p with
    | ⟨0, a⟩ => Sum.inl (Sum.inl a)
    | ⟨1, a⟩ => Sum.inl (Sum.inr a)
    | ⟨2, a⟩ => Sum.inr a
  left_inv := by rintro ((a | a) | a) <;> rfl
  right_inv := by rintro ⟨i, a⟩; fin_cases i <;> rfl


/-- **`split_U4`, basis-free.** `V = A ⊕ K₀ ⊕ W` (`DirectSum.IsInternal ![A, K₀, W]`), `A = ⟨x_H⟩` of
dimension 1, `K₀` of dimension 2, `V₁ = A ⊕ K₀`; `D = ev w` is `ε` on `V₁` and has the ±1 eigenbasis
`bW` (eigenvalues `sd`) on the dark part `W`; `J = jobsP w` is `σ` on `A`, preserves `K₀`, and is the
identity on `W`.  The `x_H` term `ε ≠ σ` and the det term `det(J|K₀) ≠ ε²` are the hypotheses of
`split_U4`; then `U ≠ d + 2`, `d = #{sd = -1}`.  The adapted basis is built from the decomposition. -/
theorem split_U4_free (h2 : (2 : K) ≠ 0) (σ ε : K) (hσ : σ = 1 ∨ σ = -1) (hε : ε = 1 ∨ ε = -1)
    (hεσ : ε ≠ σ) (A K0 W : Submodule K (n → K)) (hint : DirectSum.IsInternal ![A, K0, W])
    (hA : Module.finrank K A = 1) (hK0 : Module.finrank K K0 = 2)
    (bW : Module.Basis nd K W) (sd : nd → K) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = refl a b)
    (D J : Matrix n n K) (hD : ((ev w : (Matrix n n K)ˣ) : Matrix n n K) = D)
    (hJ : ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) = J)
    (hDA : ∀ v ∈ A, D *ᵥ v = ε • v) (hDK : ∀ v ∈ K0, D *ᵥ v = ε • v)
    (hDW : ∀ a, D *ᵥ (bW a : n → K) = sd a • (bW a : n → K))
    (hJA : ∀ v ∈ A, J *ᵥ v = σ • v) (hJK : ∀ v ∈ K0, J.mulVecLin v ∈ K0)
    (hJW : ∀ v ∈ W, J *ᵥ v = v)
    (hdetK : LinearMap.det (J.mulVecLin.restrict hJK) = 1 ∨ LinearMap.det (J.mulVecLin.restrict hJK) = -1)
    (hb : LinearMap.det (J.mulVecLin.restrict hJK) ≠ ε ^ 2) :
    ucount w ≠ (univ.filter fun a => sd a = -1).card + 2 := by
  classical
  let bA : Module.Basis (Fin 1) K A := Module.finBasisOfFinrankEq K A hA
  let bK : Module.Basis (Fin 2) K K0 := Module.finBasisOfFinrankEq K K0 hK0
  let vb : ∀ i : Fin 3, Module.Basis (![Fin 1, Fin 2, nd] i) K (![A, K0, W] i) := fun i =>
    match i with
    | 0 => bA
    | 1 => bK
    | 2 => bW
  let b' := hint.collectedBasis vb
  let B : Module.Basis ((Fin 1 ⊕ Fin 2) ⊕ nd) K (n → K) := b'.reindex (idxEquiv nd).symm
  have hB : ∀ j, B j = b' (idxEquiv nd j) := fun j => by simp [B]
  let fK := J.mulVecLin.restrict hJK
  let JK : Matrix (Fin 2) (Fin 2) K := LinearMap.toMatrix bK bK fK
  have hJKdet : JK.det = LinearMap.det fK := LinearMap.det_toMatrix bK fK
  refine split_U4_basis h2 σ ε hσ hε hεσ B JK (by rw [hJKdet]; exact hdetK)
    (by rw [hJKdet]; exact hb) sd hsd w hform ?_ ?_ ?_ ?_ ?_
  · intro i
    rw [hD, hB]
    rcases i with i | i
    · exact hDA _ (hint.collectedBasis_mem vb (idxEquiv nd (Sum.inl (Sum.inl i))))
    · exact hDK _ (hint.collectedBasis_mem vb (idxEquiv nd (Sum.inl (Sum.inr i))))
  · intro a
    rw [hD, hB]
    have e3 : b' (idxEquiv nd (Sum.inr a)) = (bW a : n → K) := by
      simp [b', idxEquiv, vb]
      rfl
    rw [e3]
    exact hDW a
  · rw [hJ, hB]
    exact hJA _ (hint.collectedBasis_mem vb (idxEquiv nd (Sum.inl (Sum.inl 0))))
  · intro j
    rw [hJ, hB]
    have e1 : b' (idxEquiv nd (Sum.inl (Sum.inr j))) = (bK j : n → K) := by
      simp [b', idxEquiv, vb]
      rfl
    have e2 : ∀ i, b' (idxEquiv nd (Sum.inl (Sum.inr i))) = (bK i : n → K) := fun i => by
      simp [b', idxEquiv, vb]
      rfl
    rw [e1]
    have hfK : J.mulVecLin (bK j : n → K) = ((fK (bK j) : K0) : n → K) := rfl
    have hsum : fK (bK j) = ∑ i, JK i j • bK i := by
      conv_lhs => rw [← bK.sum_repr (fK (bK j))]
      refine Finset.sum_congr rfl fun i _ => ?_
      simp [JK, LinearMap.toMatrix_apply]
    have : J *ᵥ (bK j : n → K) = ((fK (bK j) : K0) : n → K) := hfK
    rw [this, hsum]
    simp [hB, e2]
  · intro a
    rw [hJ, hB]
    exact hJW _ (hint.collectedBasis_mem vb (idxEquiv nd (Sum.inr a)))

end Free


end BasisFree

end SpecINV

#print axioms SpecINV.inv_rank
#print axioms SpecINV.inv_word
#print axioms SpecINV.inv_DJ
#print axioms SpecINV.UR_inv_combined
#print axioms SpecINV.six_survivors
#print axioms SpecINV.hub_data
#print axioms SpecINV.split_key
#print axioms SpecINV.split_rank_ge
#print axioms SpecINV.split_DJ_rank
#print axioms SpecINV.split_R26_2_3
#print axioms SpecINV.two_by_two_invol
#print axioms SpecINV.split_U4
#print axioms SpecINV.inv_needs_transvection
#print axioms SpecINV.inv_needs_char
#print axioms SpecINV.Phi_refl
#print axioms SpecINV.split_U4_basis
#print axioms SpecINV.split_U4_free
