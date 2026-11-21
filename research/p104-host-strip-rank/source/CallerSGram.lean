/-
CallerSGram (lane LEANSGRAM).  SCHERK's signed-Gram normal form (cards/WILD/NOVEL/scherk/SK.md items 1-2) over a field.
Setting.  A B : n x iota matrices (iota = stage columns, block function beta : iota -> N), stage t is
  V_t = 1 + A * Pi_t * B^T  (Pi_t = diagonal projector on the columns of block t), P_k = V_{k-1} ... V_0,
  G = B^T A,  Glow/Gdiag/Gup = block-strict-lower / block-diagonal / block-strict-upper part of G,
  H = (1 - Glow)^-1,  K = 2 + Gdiag + Gup - Glow.
(1) sgProd_eq     : P_k = 1 + A H B^T.                                    [product of rank-r updates]
(2) sgForward     : P_k = -1, char /= 2  ==>  rank K + n <= |iota|   (n = |iota| - 2  gives rank K <= 2),
                    plus rank G = n.
(3) sgConverse    : n + 2 = |iota|, rank K <= 2  ==>  P_k = -1  (char /= 2).  rank G <= n is automatic.
(4) CROSS (c = 1) : stages s /= t of a P_k = -1 frame with 2x2 blocks and K_ss, K_tt invertible:
                    K_st invertible, hence the block G_st has rank 2, hence >= 2 roles (rows of A,B) meet both.
(5) instance: k = 3, n = 4 over Q (the CallerSignInst design, reversed list order).
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Module
import Mathlib.Algebra.Field.Rat

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerSign
open Matrix Finset

section core
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] {n : ℕ}

def blkPi (β : ι → ℕ) (t : ℕ) : Matrix ι ι K := diagonal fun i => if β i = t then 1 else 0
def blkLo (β : ι → ℕ) (t : ℕ) : Matrix ι ι K := diagonal fun i => if β i < t then 1 else 0

def sgStage (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ) : Matrix (Fin n) (Fin n) K :=
  1 + A * blkPi β t * Bᵀ

/-- `P_t = V_{t-1} ... V_0` -/
def sgProd (A B : Matrix (Fin n) ι K) (β : ι → ℕ) : ℕ → Matrix (Fin n) (Fin n) K
  | 0 => 1
  | t + 1 => sgStage A B β t * sgProd A B β t

def sgG (A B : Matrix (Fin n) ι K) : Matrix ι ι K := Bᵀ * A
def sgLow (β : ι → ℕ) (G : Matrix ι ι K) : Matrix ι ι K := of fun i j => if β j < β i then G i j else 0
def sgDiag (β : ι → ℕ) (G : Matrix ι ι K) : Matrix ι ι K := of fun i j => if β i = β j then G i j else 0
def sgUp (β : ι → ℕ) (G : Matrix ι ι K) : Matrix ι ι K := of fun i j => if β i < β j then G i j else 0
/-- SK's `K = 2I + G_diag + G_up - G_low` -/
def sgK (β : ι → ℕ) (G : Matrix ι ι K) : Matrix ι ι K :=
  (2 : K) • (1 : Matrix ι ι K) + sgDiag β G + sgUp β G - sgLow β G

def sgT (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ) : Matrix ι (Fin n) K := blkPi β t * Bᵀ * sgProd A B β t
def sgW (B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ) : Matrix ι (Fin n) K := blkPi β t * Bᵀ

theorem sgG_split (β : ι → ℕ) (G : Matrix ι ι K) : G = sgLow β G + sgDiag β G + sgUp β G := by
  ext i j
  simp only [sgLow, sgDiag, sgUp, Matrix.add_apply, of_apply]
  rcases lt_trichotomy (β i) (β j) with h | h | h
  · simp [h, h.ne, not_lt.mpr h.le]
  · simp [h]
  · simp [h, h.ne', not_lt.mpr h.le]

theorem sgK_eq (β : ι → ℕ) (G : Matrix ι ι K) :
    sgK β G = G + (2 : K) • (1 - sgLow β G) := by
  have h := sgG_split β G
  unfold sgK
  generalize sgLow β G = L at *
  generalize sgDiag β G = D at *
  generalize sgUp β G = U at *
  rw [h]
  module

theorem isUnit_det_one_sub_low (β : ι → ℕ) (G : Matrix ι ι K) :
    IsUnit (1 - sgLow β G).det := by
  have hT : BlockTriangular (1 - sgLow β G) (fun i => OrderDual.toDual (β i)) := by
    intro i j hij
    have h : β i < β j := hij
    have h1 : ¬ (β j < β i) := not_lt.mpr h.le
    have hne : i ≠ j := fun e => by subst e; exact lt_irrefl _ h
    simp [sgLow, one_apply, hne, h1]
  rw [hT.det]
  have : ∀ a, ((1 - sgLow β G).toSquareBlock (fun i => OrderDual.toDual (β i)) a) = 1 := by
    intro a
    ext ⟨i, hi⟩ ⟨j, hj⟩
    have hij : β i = β j := by
      have := hi.trans hj.symm
      exact OrderDual.toDual.injective this
    have h1 : ¬ (β j < β i) := by rw [hij]; exact lt_irrefl _
    by_cases e : i = j
    · subst e; simp [toSquareBlock_def, sgLow, one_apply]
    · have e' : (⟨i, hi⟩ : {x // OrderDual.toDual (β x) = a}) ≠ ⟨j, hj⟩ := by
        intro h; exact e (congrArg Subtype.val h)
      simp [toSquareBlock_def, sgLow, one_apply, e, e', h1]
  simp [this]

/-! telescoping -/
theorem sgProd_eq_sum (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ) :
    sgProd A B β t = 1 + A * (∑ s ∈ range t, sgT A B β s) := by
  induction t with
  | zero => simp [sgProd]
  | succ t ih =>
    rw [sum_range_succ, sgProd, sgStage]
    generalize (∑ s ∈ range t, sgT A B β s) = S at ih ⊢
    simp only [sgT, Matrix.mul_assoc]
    rw [ih]
    simp only [Matrix.mul_add, Matrix.add_mul, Matrix.mul_one, Matrix.one_mul, Matrix.mul_assoc]
    abel

theorem blkLo_mul_blkPi (β : ι → ℕ) (t s : ℕ) :
    (blkLo β t : Matrix ι ι K) * blkPi β s = if s < t then blkPi β s else 0 := by
  unfold blkLo blkPi
  rw [diagonal_mul_diagonal]
  by_cases h : s < t
  · rw [if_pos h]; congr 1; ext i
    by_cases e : β i = s
    · simp [e, h]
    · simp [e]
  · rw [if_neg h]
    ext i j
    by_cases e : β i = s
    · have : ¬ β i < t := by rw [e]; exact h
      simp [diagonal_apply, this]
    · simp [diagonal_apply, e]

theorem sum_blkPi (β : ι → ℕ) (k : ℕ) (hβ : ∀ i, β i < k) :
    ∑ t ∈ range k, (blkPi β t : Matrix ι ι K) = 1 := by
  ext i j
  simp only [blkPi, Matrix.sum_apply, diagonal_apply, one_apply]
  by_cases e : i = j
  · subst e
    simp [hβ i]
  · simp [e]

theorem sgLow_sum (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k : ℕ) (hβ : ∀ i, β i < k) :
    sgLow β (sgG A B) = ∑ t ∈ range k, blkPi β t * sgG A B * blkLo β t := by
  ext i j
  simp only [sgLow, of_apply, Matrix.sum_apply, blkPi, blkLo, diagonal_mul, mul_diagonal]
  rw [sum_eq_single (β i)]
  · by_cases h : β j < β i <;> simp [h]
  · intro t _ ht
    simp [Ne.symm ht]
  · intro h; exact absurd (mem_range.2 (hβ i)) h

theorem sgProd_eq (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k : ℕ) (hβ : ∀ i, β i < k) :
    sgProd A B β k = 1 + A * (1 - sgLow β (sgG A B))⁻¹ * Bᵀ := by
  set G := sgG A B with hG
  set X : Matrix ι (Fin n) K := ∑ t ∈ range k, sgT A B β t with hX
  have h1 : sgProd A B β k = 1 + A * X := sgProd_eq_sum A B β k
  have hlow : sgLow β G * X = X - Bᵀ := by
    rw [hG, sgLow_sum A B β k hβ, Matrix.sum_mul]
    have key : ∀ t ∈ range k, blkPi β t * sgG A B * blkLo β t * X
        = sgT A B β t - sgW B β t := by
      intro t ht
      have ht' : t ≤ k := (mem_range.1 ht).le
      have e1 : blkLo β t * X = ∑ s ∈ range t, sgT A B β s := by
        rw [hX, Matrix.mul_sum]
        have : ∀ s ∈ range k, blkLo β t * sgT A B β s
            = if s < t then sgT A B β s else 0 := by
          intro s _
          simp only [sgT]
          rw [← Matrix.mul_assoc, ← Matrix.mul_assoc, blkLo_mul_blkPi]
          split_ifs <;> simp
        rw [sum_congr rfl this, ← sum_filter]
        congr 1; ext s; simp; omega
      have e2 : A * (∑ s ∈ range t, sgT A B β s) = sgProd A B β t - 1 := by
        have := sgProd_eq_sum A B β t
        rw [this]; abel
      calc blkPi β t * sgG A B * blkLo β t * X
          = blkPi β t * (Bᵀ * (A * (blkLo β t * X))) := by
            simp only [sgG, Matrix.mul_assoc]
        _ = sgT A B β t - sgW B β t := by
            rw [e1, e2]; simp only [sgT, sgW, Matrix.mul_sub, Matrix.mul_assoc, Matrix.mul_one]
    rw [sum_congr rfl key, sum_sub_distrib, hX]
    simp only [sgT, sgW]
    rw [← Matrix.sum_mul, sum_blkPi β k hβ, Matrix.one_mul]
  have hM : (1 - sgLow β G) * X = Bᵀ := by rw [Matrix.sub_mul, Matrix.one_mul, hlow]; abel
  have hX2 : X = (1 - sgLow β G)⁻¹ * Bᵀ := by
    rw [← hM, ← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ (isUnit_det_one_sub_low β G), Matrix.one_mul]
  rw [h1, hX2, ← Matrix.mul_assoc]


/-! ## forward direction and converse -/
section fwd
variable (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k : ℕ)

/-- the 2 = (1 + 1) trick: `A H B^T = -2` from `P_k = -1`. -/
theorem sg_AHB (hβ : ∀ i, β i < k) (hP : sgProd A B β k = -1) :
    A * (1 - sgLow β (sgG A B))⁻¹ * Bᵀ = (-2 : K) • (1 : Matrix (Fin n) (Fin n) K) := by
  have h := sgProd_eq A B β k hβ
  rw [hP] at h
  have : A * (1 - sgLow β (sgG A B))⁻¹ * Bᵀ = -1 - 1 := by
    calc _ = (1 + A * (1 - sgLow β (sgG A B))⁻¹ * Bᵀ) - 1 := by abel
      _ = -1 - 1 := by rw [← h]
  rw [this]; module

theorem sg_HM (β : ι → ℕ) (G : Matrix ι ι K) :
    (1 - sgLow β G)⁻¹ * (1 - sgLow β G) = 1 ∧ (1 - sgLow β G) * (1 - sgLow β G)⁻¹ = 1 :=
  ⟨Matrix.nonsing_inv_mul _ (isUnit_det_one_sub_low β G),
   Matrix.mul_nonsing_inv _ (isUnit_det_one_sub_low β G)⟩

theorem sg_isUnit_H (β : ι → ℕ) (G : Matrix ι ι K) : IsUnit ((1 - sgLow β G)⁻¹).det :=
  Matrix.isUnit_det_of_right_inverse (sg_HM β G).1

/-- Core identity for `D = G H`: `(K H) = D + 2`, and `D D = -2 D` when `A H B^T = -2`. -/
theorem sg_KH (β : ι → ℕ) (G : Matrix ι ι K) :
    sgK β G * (1 - sgLow β G)⁻¹ = G * (1 - sgLow β G)⁻¹ + (2 : K) • (1 : Matrix ι ι K) := by
  rw [sgK_eq, Matrix.add_mul, Matrix.smul_mul, (sg_HM β G).2]

theorem sg_DD (hAHB : A * (1 - sgLow β (sgG A B))⁻¹ * Bᵀ = (-2 : K) • (1 : Matrix (Fin n) (Fin n) K)) :
    (sgG A B * (1 - sgLow β (sgG A B))⁻¹) * (sgG A B * (1 - sgLow β (sgG A B))⁻¹)
      = (-2 : K) • (sgG A B * (1 - sgLow β (sgG A B))⁻¹) := by
  set H := (1 - sgLow β (sgG A B))⁻¹
  calc (sgG A B * H) * (sgG A B * H) = Bᵀ * (A * H * Bᵀ) * (A * H) := by
        simp only [sgG, Matrix.mul_assoc]
    _ = (-2 : K) • (sgG A B * H) := by
        rw [hAHB]; simp [sgG, Matrix.mul_assoc, Matrix.mul_smul, Matrix.smul_mul]

theorem rank_sg_ge (h2 : (2 : K) ≠ 0)
    (hAHB : A * (1 - sgLow β (sgG A B))⁻¹ * Bᵀ = (-2 : K) • (1 : Matrix (Fin n) (Fin n) K)) :
    n ≤ (sgG A B).rank := by
  classical
  set H := (1 - sgLow β (sgG A B))⁻¹
  have h4 : (4 : K) ≠ 0 := by
    have : (4 : K) = 2 * 2 := by norm_num
    rw [this]; exact mul_ne_zero h2 h2
  have e : (A * H) * sgG A B * (H * Bᵀ) = (4 : K) • (1 : Matrix (Fin n) (Fin n) K) := by
    calc (A * H) * sgG A B * (H * Bᵀ) = (A * H * Bᵀ) * (A * H * Bᵀ) := by
          simp only [sgG, Matrix.mul_assoc]
      _ = _ := by
          rw [hAHB]; simp only [Matrix.smul_mul, Matrix.mul_smul, Matrix.mul_one, smul_smul]
          norm_num
  have hr : ((4 : K) • (1 : Matrix (Fin n) (Fin n) K)).rank = n := by
    rw [Matrix.smul_one_eq_diagonal, Matrix.rank_diagonal]
    simp [h4]
  calc n = _ := hr.symm
    _ = ((A * H) * sgG A B * (H * Bᵀ)).rank := by rw [e]
    _ ≤ ((A * H) * sgG A B).rank := Matrix.rank_mul_le_left _ _
    _ ≤ (sgG A B).rank := Matrix.rank_mul_le_right _ _

theorem rank_sg_le : (sgG A B).rank ≤ n := by
  calc (sgG A B).rank ≤ Bᵀ.rank := Matrix.rank_mul_le_left _ _
    _ ≤ n := by simpa using Matrix.rank_le_card_width Bᵀ

/-- FORWARD DIRECTION of SK item 1: `P_k = -1` (char /= 2) gives `rank K + n <= |iota|`
    (so `rank K <= 2` when `n = |iota| - 2`) and `rank G = n`. -/
theorem sgForward (h2 : (2 : K) ≠ 0) (hβ : ∀ i, β i < k) (hP : sgProd A B β k = -1) :
    (sgK β (sgG A B)).rank + n ≤ Fintype.card ι ∧ (sgG A B).rank = n := by
  have hAHB := sg_AHB A B β k hβ hP
  have hDD := sg_DD A B β hAHB
  set H := (1 - sgLow β (sgG A B))⁻¹
  have hge := rank_sg_ge A B β h2 hAHB
  have hle := rank_sg_le A B
  refine ⟨?_, le_antisymm hle hge⟩
  have hz : (sgK β (sgG A B) * H) * (sgG A B * H) = 0 := by
    rw [sg_KH, Matrix.add_mul, hDD, Matrix.smul_mul, Matrix.one_mul]; module
  have := Matrix.rank_add_rank_le_card_of_mul_eq_zero hz
  rw [Matrix.rank_mul_eq_left_of_isUnit_det _ _ (sg_isUnit_H β _),
    Matrix.rank_mul_eq_left_of_isUnit_det _ _ (sg_isUnit_H β _)] at this
  omega

end fwd

/-! ## converse (SK says "<=>"; here the converse is proved: `rank K <= 2` alone suffices when n = |iota| - 2) -/
section conv
variable (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k : ℕ)

theorem mulVec_ext_zero {m o : Type*} [Fintype o] [DecidableEq o] (M : Matrix m o K)
    (h : ∀ x, M.mulVec x = 0) : M = 0 := by
  ext i j
  have := congrFun (h (Pi.single j 1)) i
  simpa [Matrix.mulVec_single_one] using this

theorem sgConverse (h2 : (2 : K) ≠ 0) (hβ : ∀ i, β i < k) (hn : n + 2 = Fintype.card ι)
    (hK : (sgK β (sgG A B)).rank ≤ 2) : sgProd A B β k = -1 := by
  classical
  set G := sgG A B with hG
  set H := (1 - sgLow β G)⁻¹ with hH
  set E := sgK β G * H with hE
  set D := G * H with hD
  have hED : E = D + (2 : K) • (1 : Matrix ι ι K) := sg_KH β G
  have hEr : E.rank ≤ 2 := by
    rw [hE, Matrix.rank_mul_eq_left_of_isUnit_det _ _ (sg_isUnit_H β _)]; exact hK
  have hDr : D.rank ≤ n := by
    rw [hD, Matrix.rank_mul_eq_left_of_isUnit_det _ _ (sg_isUnit_H β _)]; exact rank_sg_le A B
  let rE := LinearMap.range E.mulVecLin
  let rD := LinearMap.range D.mulVecLin
  have hfE : Module.finrank K rE = E.rank := rfl
  have hfD : Module.finrank K rD = D.rank := rfl
  have hsup : rE ⊔ rD = ⊤ := by
    rw [eq_top_iff]
    intro v _
    have e : v = E.mulVec ((2 : K)⁻¹ • v) - D.mulVec ((2 : K)⁻¹ • v) := by
      rw [hED, Matrix.add_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec, Matrix.mulVec_smul]
      ext i
      simp [h2]
    rw [e]
    exact Submodule.sub_mem _ (Submodule.mem_sup_left ⟨_, rfl⟩) (Submodule.mem_sup_right ⟨_, rfl⟩)
  have hdim := Submodule.finrank_sup_add_finrank_inf_eq rE rD
  rw [hsup, finrank_top, Module.finrank_fintype_fun_eq_card] at hdim
  have hinf : rE ⊓ rD = ⊥ := by
    apply Submodule.finrank_eq_zero.mp
    omega
  have hDge : n ≤ D.rank := by
    have : Module.finrank K ↥(rE ⊓ rD) = 0 := by rw [hinf]; simp
    omega
  have hcomm : E * D = D * E := by
    rw [hED]; simp only [Matrix.add_mul, Matrix.mul_add, Matrix.smul_mul, Matrix.mul_smul,
      Matrix.one_mul, Matrix.mul_one]
  have hz : E * D = 0 := by
    apply mulVec_ext_zero
    intro x
    have h1 : (E * D).mulVec x ∈ rE ⊓ rD := by
      constructor
      · exact ⟨D.mulVec x, by simp [Matrix.mulVec_mulVec]⟩
      · refine ⟨E.mulVec x, ?_⟩
        simp [Matrix.mulVec_mulVec, hcomm]
    rw [hinf] at h1
    simpa using h1
  have hDD : D * D = (-2 : K) • D := by
    rw [hED] at hz
    simp only [Matrix.add_mul, Matrix.smul_mul, Matrix.one_mul] at hz
    have : D * D = -((2 : K) • D) := eq_neg_of_add_eq_zero_left hz
    rw [this]; module
  have hGHG : G * H * G = (-2 : K) • G := by
    have h := congrArg (fun X => X * (1 - sgLow β G)) hDD
    simp only [hD, Matrix.smul_mul] at h
    have e1 : G * H * (G * H) * (1 - sgLow β G) = G * H * G := by
      calc G * H * (G * H) * (1 - sgLow β G) = G * H * G * (H * (1 - sgLow β G)) := by
            simp only [Matrix.mul_assoc]
        _ = G * H * G := by rw [(sg_HM β G).1, Matrix.mul_one]
    have e2 : G * H * (1 - sgLow β G) = G := by
      rw [Matrix.mul_assoc, (sg_HM β G).1, Matrix.mul_one]
    rw [e1, e2] at h
    exact h
  have hGr : n ≤ G.rank := by
    rw [hD, Matrix.rank_mul_eq_left_of_isUnit_det _ _ (sg_isUnit_H β _)] at hDge; exact hDge
  have hAs : LinearMap.range A.mulVecLin = ⊤ := by
    apply Submodule.eq_top_of_finrank_eq
    rw [Module.finrank_fintype_fun_eq_card, Fintype.card_fin]
    have h1 : n ≤ A.rank := hGr.trans (Matrix.rank_mul_le_right _ _)
    have h2' : A.rank ≤ n := by simpa using Matrix.rank_le_card_height A
    exact le_antisymm h2' h1
  have hBi : Function.Injective Bᵀ.mulVecLin := by
    have h1 : n ≤ Bᵀ.rank := hGr.trans (Matrix.rank_mul_le_left _ _)
    have h3 := LinearMap.finrank_range_add_finrank_ker Bᵀ.mulVecLin
    rw [Module.finrank_fintype_fun_eq_card, Fintype.card_fin] at h3
    have h4 : Module.finrank K (LinearMap.ker Bᵀ.mulVecLin) = 0 := by
      have : Module.finrank K (LinearMap.range Bᵀ.mulVecLin) = Bᵀ.rank := rfl
      omega
    exact LinearMap.ker_eq_bot.mp (Submodule.finrank_eq_zero.mp h4)
  set Y : Matrix (Fin n) (Fin n) K := A * H * Bᵀ + (2 : K) • 1 with hY
  have hBYA : Bᵀ * Y * A = 0 := by
    have : Bᵀ * Y * A = G * H * G + (2 : K) • G := by
      simp only [hY, hG, sgG, Matrix.mul_add, Matrix.add_mul, Matrix.mul_assoc, Matrix.mul_smul,
        Matrix.smul_mul, Matrix.mul_one, Matrix.one_mul]
    rw [this, hGHG]; module
  have hY0 : Y = 0 := by
    apply mulVec_ext_zero
    intro w
    have hw : w ∈ LinearMap.range A.mulVecLin := by rw [hAs]; trivial
    obtain ⟨u, rfl⟩ := hw
    apply hBi
    have : Bᵀ.mulVec (Y.mulVec (A.mulVec u)) = (Bᵀ * Y * A).mulVec u := by
      simp only [Matrix.mulVec_mulVec, Matrix.mul_assoc]
    simp only [Matrix.mulVecLin_apply]
    rw [this, hBYA]; simp
  have hAHB : A * H * Bᵀ = (-2 : K) • (1 : Matrix (Fin n) (Fin n) K) := by
    have : A * H * Bᵀ = Y - (2 : K) • 1 := by simp [hY]
    rw [this, hY0]; module
  rw [sgProd_eq A B β k hβ]
  change 1 + A * H * Bᵀ = -1
  rw [hAHB]; module

end conv
end core

/-! ## CROSS law, pair-coverage case (c = 1) -/
section cross
open Matrix
variable {K : Type*} [Field K] {n k m : ℕ}

/-- (stage s, stage t) block of a matrix indexed by `Fin k × Fin m` -/
def blkOf (M : Matrix (Fin k × Fin m) (Fin k × Fin m) K) (s t : Fin k) : Matrix (Fin m) (Fin m) K :=
  Matrix.of fun a b => M (s, a) (t, b)

/-- Schur core (copied from CallerGram.schur_core): rank <= m with invertible top-left block => zero Schur complement. -/
theorem schur_core' {m : Type*} [Fintype m] [DecidableEq m] (P Q R S : Matrix m m K) (hP : IsUnit P.det)
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
  have hT : Module.finrank K T = Fintype.card m := by
    rw [LinearMap.finrank_range_of_inj hinj]
    simp
  have hle : T ≤ LinearMap.range G.mulVecLin := LinearMap.range_comp_le_range _ _
  have hW : Module.finrank K (LinearMap.range G.mulVecLin) ≤ Module.finrank K T := by
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

/-- If `rank M <= m` and the diagonal blocks `M_ss`, `M_tt` are invertible, so is `M_st`
    (SK item 1: "every block K_st is invertible"; the argument is `M_tt = M_ts M_ss^-1 M_st`). -/
theorem blk_unit (M : Matrix (Fin k × Fin m) (Fin k × Fin m) K) (hr : M.rank ≤ m) (s t : Fin k)
    (hs : IsUnit (blkOf M s s).det) (ht : IsUnit (blkOf M t t).det) : IsUnit (blkOf M s t).det := by
  have hF : fromBlocks (blkOf M s s) (blkOf M s t) (blkOf M t s) (blkOf M t t)
      = M.submatrix (Sum.elim (fun a => (s, a)) (fun a => (t, a)))
          (Sum.elim (fun a => (s, a)) (fun a => (t, a))) := by
    ext (i | i) (j | j) <;> simp [blkOf]
  have hrank : (fromBlocks (blkOf M s s) (blkOf M s t) (blkOf M t s) (blkOf M t t)).rank
      ≤ Fintype.card (Fin m) := by
    rw [hF]
    simpa using (Matrix.rank_submatrix_le M _ _).trans hr
  have h := schur_core' _ _ _ _ hs hrank
  have hd : (blkOf M t t).det = (blkOf M t s).det * ((blkOf M s s)⁻¹).det * (blkOf M s t).det := by
    rw [h, Matrix.det_mul, Matrix.det_mul]
  rw [hd] at ht
  exact (IsUnit.mul_iff.mp ht).2


/-- block relation between `G` and `K` off the diagonal. -/
theorem blk_G_K (G : Matrix (Fin k × Fin m) (Fin k × Fin m) K) (s t : Fin k) (hst : s ≠ t) :
    (s < t ∧ blkOf G s t = blkOf (sgK (fun i => (i.1 : ℕ)) G) s t) ∨
    (t < s ∧ blkOf G s t = - blkOf (sgK (fun i => (i.1 : ℕ)) G) s t) := by
  rcases lt_or_gt_of_ne hst with h | h
  · left
    refine ⟨h, ?_⟩
    ext a b
    have h' : (s : ℕ) < t := h
    simp [blkOf, sgK, sgDiag, sgUp, sgLow, one_apply, hst, h, not_lt.mpr h.le, Fin.val_ne_of_ne hst, h'.ne, h'.ne']
  · right
    refine ⟨h, ?_⟩
    ext a b
    have h' : (t : ℕ) < s := h
    simp [blkOf, sgK, sgDiag, sgUp, sgLow, one_apply, hst, h, not_lt.mpr h.le, Fin.val_ne_of_ne hst, h'.ne, h'.ne']

theorem blk_G_unit (G : Matrix (Fin k × Fin m) (Fin k × Fin m) K) (s t : Fin k) (hst : s ≠ t)
    (h : IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) G) s t).det) : IsUnit (blkOf G s t).det := by
  rcases blk_G_K G s t hst with ⟨_, e⟩ | ⟨_, e⟩
  · rw [e]; exact h
  · rw [e, Matrix.det_neg]; exact (IsUnit.pow _ (IsUnit.neg isUnit_one)).mul h

/-- the roles (rows of `A`,`B`) touching stage `s` -/
def meets (A B : Matrix (Fin n) (Fin k × Fin m) K) (r : Fin n) (s : Fin k) : Prop :=
  ∃ a, A r (s, a) ≠ 0 ∨ B r (s, a) ≠ 0

open Classical in
/-- roles meeting both stages -/
noncomputable def coverSet (A B : Matrix (Fin n) (Fin k × Fin m) K) (s t : Fin k) : Finset (Fin n) :=
  Finset.univ.filter fun r => meets A B r s ∧ meets A B r t

/-- each role contributes rank <= 1 to a Gram block: rank G_st <= #roles meeting both s and t -/
theorem rank_blk_le_cover (A B : Matrix (Fin n) (Fin k × Fin m) K) (s t : Fin k) :
    (blkOf (sgG A B) s t).rank ≤ (coverSet A B s t).card := by
  classical
  set S := coverSet A B s t with hS
  let Bs : Matrix (Fin m) S K := Matrix.of fun a r => B r.1 (s, a)
  let At : Matrix S (Fin m) K := Matrix.of fun r b => A r.1 (t, b)
  have e : blkOf (sgG A B) s t = Bs * At := by
    ext a b
    simp only [blkOf, sgG, Matrix.of_apply, Matrix.mul_apply, Matrix.transpose_apply, Bs, At]
    rw [Finset.sum_coe_sort S (fun r => B r (s, a) * A r (t, b))]
    symm
    apply Finset.sum_subset (Finset.subset_univ _)
    intro r _ hr
    simp only [hS, coverSet, Finset.mem_filter, Finset.mem_univ, true_and, not_and_or] at hr
    rcases hr with hr | hr
    · have : B r (s, a) = 0 := by
        by_contra hne; exact hr ⟨a, Or.inr hne⟩
      simp [this]
    · have : A r (t, b) = 0 := by
        by_contra hne; exact hr ⟨b, Or.inl hne⟩
      simp [this]
  rw [e]
  refine (Matrix.rank_mul_le_left _ _).trans ?_
  simpa using Matrix.rank_le_card_width Bs

/-- CROSS, c = 1 (PAIR COVERAGE from the product alone): in a `P_k = -1` frame with `n + m = k m`,
    char /= 2 and invertible diagonal blocks `K_tt` (SK's `lambda /= -1`), any two distinct stages
    are met by at least `m` common roles (`m = 2`: at least two). -/
theorem sgPairCoverage (A B : Matrix (Fin n) (Fin k × Fin m) K) (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B (fun i => (i.1 : ℕ)) k = -1) (hn : n + m = k * m)
    (hdiag : ∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) t t).det)
    (s t : Fin k) (hst : s ≠ t) :
    m ≤ (coverSet A B s t).card := by
  have hF := (sgForward A B (fun i => (i.1 : ℕ)) k h2 (fun i => i.1.isLt) hP).1
  simp only [Fintype.card_prod, Fintype.card_fin] at hF
  have hr : (sgK (fun i => (i.1 : ℕ)) (sgG A B)).rank ≤ m := by omega
  have hu := blk_unit _ hr s t (hdiag s) (hdiag t)
  have hu' := blk_G_unit _ s t hst hu
  have := Matrix.rank_of_isUnit _ ((Matrix.isUnit_iff_isUnit_det _).mpr hu')
  have h3 := rank_blk_le_cover A B s t
  simp only [Fintype.card_fin] at this
  omega

end cross


/-! ## non-vacuity: k = 3, m = 2, n = 4 over Q (CallerSignInst design, stages in product order) -/
section inst
open Matrix

/-- stage `t` is `I + (u_t v_t^T) ⊗ I_2`, `u = column of A_t`, `v = column of B_t` -/
def uu : Fin 3 → Fin 2 → ℚ := ![![1, 2], ![0, 1], ![1, 0]]
def vv : Fin 3 → Fin 2 → ℚ := ![![-1/3, -2/3], ![1, 0], ![-5/2, 1]]

def A3 : Matrix (Fin 4) (Fin 3 × Fin 2) ℚ :=
  Matrix.of fun r c => uu c.1 ⟨r.val / 2, by have := r.isLt; omega⟩ * (if r.val % 2 = c.2.val then 1 else 0)
def B3 : Matrix (Fin 4) (Fin 3 × Fin 2) ℚ :=
  Matrix.of fun r c => vv c.1 ⟨r.val / 2, by have := r.isLt; omega⟩ * (if r.val % 2 = c.2.val then 1 else 0)

theorem prod_A3B3 : sgProd A3 B3 (fun i => (i.1 : ℕ)) 3 = -1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [sgProd, sgStage, blkPi, A3, B3, uu, vv, Matrix.mul_apply, Matrix.add_apply, Matrix.one_apply,
      Matrix.diagonal_apply, Fintype.sum_prod_type, Fin.sum_univ_succ] <;> norm_num

theorem diag_unit_A3B3 :
    ∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A3 B3)) t t).det := by
  intro t
  rw [isUnit_iff_ne_zero]
  fin_cases t <;>
    simp [Matrix.det_fin_two, blkOf, sgK, sgDiag, sgUp, sgLow, sgG, A3, B3, uu, vv, Matrix.mul_apply,
      Matrix.one_apply, Fin.sum_univ_succ, Matrix.transpose_apply] <;> norm_num

/-- the pair-coverage law on the explicit design: every two stages are met by >= 2 common roles. -/
theorem inst_pair_coverage : ∀ s t : Fin 3, s ≠ t → 2 ≤ (coverSet A3 B3 s t).card :=
  fun s t hst => sgPairCoverage A3 B3 (by norm_num) prod_A3B3 (by norm_num) diag_unit_A3B3 s t hst

/-- the forward law on the explicit design: rank K <= 2 and rank G = 4 -/
theorem inst_forward :
    (sgK (fun i => (i.1 : ℕ)) (sgG A3 B3)).rank ≤ 2 ∧ (sgG A3 B3).rank = 4 := by
  have h := sgForward A3 B3 (fun i => (i.1 : ℕ)) 3 (by norm_num) (fun i => i.1.isLt) prod_A3B3
  simp only [Fintype.card_prod, Fintype.card_fin] at h
  exact ⟨by omega, h.2⟩

/-- the converse closes the loop on the design: `rank K <= 2` alone recovers `P_3 = -1`. -/
theorem inst_converse : sgProd A3 B3 (fun i => (i.1 : ℕ)) 3 = -1 :=
  sgConverse A3 B3 (fun i => (i.1 : ℕ)) 3 (by norm_num) (fun i => i.1.isLt) (by simp)
    inst_forward.1

end inst

#print axioms sgProd_eq
#print axioms sgForward
#print axioms sgConverse
#print axioms sgPairCoverage
#print axioms prod_A3B3
#print axioms inst_pair_coverage
#print axioms inst_forward
#print axioms inst_converse
end CallerSign
