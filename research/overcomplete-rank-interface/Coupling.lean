import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Basic

/-
SPDX-License-Identifier: Apache-2.0
The rank conclusions of DreamingOfClouds's Lemma OC (PR2277), formalized
for ywz65 with OpenAI Codex assistance. No geometric cost theorem is claimed.
-/
open Matrix Module
set_option linter.unusedSectionVars false

namespace OvercompleteRank
variable {K T M : Type*} [Field K] [Fintype T] [Fintype M]
  [DecidableEq T] [DecidableEq M]

theorem cross_idempotent (X Y : Matrix T M K) (h : X * Y.transpose = 1) :
    (Y.transpose * X) * (Y.transpose * X) = Y.transpose * X := by
  calc
    _ = Y.transpose * (X * Y.transpose) * X := by simp only [Matrix.mul_assoc]
    _ = _ := by rw [h, Matrix.mul_one]

theorem factor_rank (X Y : Matrix T M K) (h : X * Y.transpose = 1) :
    X.rank = Fintype.card T := by
  apply le_antisymm
  · rw [← Matrix.rank_transpose]
    exact Matrix.rank_le_card_width _
  · have hh := Matrix.rank_mul_le_left X Y.transpose
    simpa only [h, Matrix.rank_one] using hh

theorem cross_rank (X Y : Matrix T M K) (h : X * Y.transpose = 1) :
    (Y.transpose * X).rank = Fintype.card T := by
  have hX := factor_rank X Y h
  have hx : X * (Y.transpose * X) = X := by rw [← Matrix.mul_assoc, h, Matrix.one_mul]
  apply le_antisymm
  · simpa only [hX] using Matrix.rank_mul_le_right Y.transpose X
  · have hh := Matrix.rank_mul_le_right X (Y.transpose * X)
    simpa only [hx, hX] using hh

theorem rank_add_le (A B : Matrix M M K) : (A + B).rank ≤ A.rank + B.rank := by
  rw [Matrix.rank, Matrix.mulVecLin_add]
  exact (Submodule.finrank_mono (LinearMap.range_add_le A.mulVecLin B.mulVecLin)).trans
    (Submodule.finrank_add_le_finrank_add_finrank _ _)

theorem complement_rank (X Y : Matrix T M K) (h : X * Y.transpose = 1) :
    (1 - Y.transpose * X).rank = Fintype.card M - Fintype.card T := by
  have hc := cross_rank X Y h
  have hz : (Y.transpose * X) * (1 - Y.transpose * X) = 0 := by
    rw [Matrix.mul_sub, Matrix.mul_one, cross_idempotent X Y h, sub_self]
  have hu := Matrix.rank_add_rank_le_card_of_mul_eq_zero hz
  have hl := rank_add_le (Y.transpose * X) (1 - Y.transpose * X)
  have hs : Y.transpose * X + (1 - Y.transpose * X) = 1 := by abel
  rw [hs, Matrix.rank_one, hc] at hl
  rw [hc] at hu
  omega

theorem one_extra_rank (X Y : Matrix T M K) (h : X * Y.transpose = 1)
    (hm : Fintype.card M = Fintype.card T + 1) :
    (1 - Y.transpose * X).rank = 1 := by
  rw [complement_rank X Y h, hm]
  omega

theorem rank_one_factorization (A : Matrix M M K) (hr : A.rank = 1) :
    ∃ a b : M → K, A = Matrix.vecMulVec a b ∧ a ≠ 0 ∧ b ≠ 0 := by
  classical
  have hn : A ≠ 0 := by
    intro hz
    rw [hz, Matrix.rank_zero] at hr
    omega
  have hex : ∃ j, A.col j ≠ 0 := by
    by_contra h
    push Not at h
    apply hn
    ext i j
    exact congrFun (h j) i
  obtain ⟨j, hj⟩ := hex
  let S := Submodule.span K (Set.range A.col)
  have hs : Module.finrank K S = 1 := by
    simpa only [Matrix.rank_eq_finrank_span_cols] using hr
  have hm (k : M) : A.col k ∈ S := Submodule.subset_span ⟨k, rfl⟩
  let a : S := ⟨A.col j, hm j⟩
  have ha : a ≠ 0 := by
    intro h
    apply hj
    exact congrArg Subtype.val h
  have hc (k : M) : ∃ c : K, c • a = (⟨A.col k, hm k⟩ : S) :=
    exists_smul_eq_of_finrank_eq_one hs ha _
  choose b hb using hc
  have hf : A = Matrix.vecMulVec (A.col j) b := by
    ext i k
    have hi := congrFun (congrArg Subtype.val (hb k)) i
    simpa only [a, Submodule.coe_smul, Pi.smul_apply, smul_eq_mul,
      Matrix.col_apply, Matrix.vecMulVec_apply, mul_comm] using hi.symm
  refine ⟨A.col j, b, hf, hj, ?_⟩
  intro hz
  apply hn
  rw [hf, hz]
  ext i k
  simp

theorem complement_idempotent (X Y : Matrix T M K) (h : X * Y.transpose = 1) :
    (1 - Y.transpose * X) * (1 - Y.transpose * X) = 1 - Y.transpose * X := by
  simp only [Matrix.sub_mul, Matrix.mul_sub, Matrix.one_mul,
    Matrix.mul_one, cross_idempotent X Y h]
  abel

theorem outer_idempotent_normalized (a b : M → K) (ha : a ≠ 0) (hb : b ≠ 0)
    (h : Matrix.vecMulVec a b * Matrix.vecMulVec a b = Matrix.vecMulVec a b) :
    dotProduct b a = 1 := by
  classical
  have hai : ∃ i, a i ≠ 0 := by
    by_contra hh
    push Not at hh
    exact ha (funext hh)
  have hbj : ∃ j, b j ≠ 0 := by
    by_contra hh
    push Not at hh
    exact hb (funext hh)
  obtain ⟨i, hi⟩ := hai
  obtain ⟨j, hj⟩ := hbj
  rw [Matrix.vecMulVec_mul_vecMulVec] at h
  have he := congrArg (fun A : Matrix M M K => A i j) h
  simp only [Matrix.vecMulVec_apply, Pi.smul_apply, smul_eq_mul] at he
  apply mul_right_cancel₀ (mul_ne_zero hi hj)
  calc
    dotProduct b a * (a i * b j) = a i * (dotProduct b a * b j) := by ring
    _ = a i * b j := he
    _ = 1 * (a i * b j) := by ring

theorem one_extra_factorization (X Y : Matrix T M K) (h : X * Y.transpose = 1)
    (hm : Fintype.card M = Fintype.card T + 1) :
    ∃ a b : M → K, 1 - Y.transpose * X = Matrix.vecMulVec a b ∧
      dotProduct b a = 1 := by
  obtain ⟨a, b, hf, ha, hb⟩ := rank_one_factorization _ (one_extra_rank X Y h hm)
  refine ⟨a, b, hf, outer_idempotent_normalized a b ha hb ?_⟩
  rw [← hf]
  exact complement_idempotent X Y h

theorem one_extra_entries (X Y : Matrix T M K) (h : X * Y.transpose = 1)
    (hm : Fintype.card M = Fintype.card T + 1) :
    ∃ a b : M → K, dotProduct b a = 1 ∧
      (∀ i j, i ≠ j → (Y.transpose * X) i j = -(a i * b j)) ∧
      (∀ i, (Y.transpose * X) i i = 1 - a i * b i) := by
  obtain ⟨a, b, hf, hn⟩ := one_extra_factorization X Y h hm
  refine ⟨a, b, hn, ?_, ?_⟩
  · intro i j hij
    have he := congrArg (fun A : Matrix M M K => A i j) hf
    simp only [Matrix.sub_apply, Matrix.one_apply_ne hij,
      Matrix.vecMulVec_apply, zero_sub] at he
    exact neg_eq_iff_eq_neg.mp he
  · intro i
    have he := congrArg (fun A : Matrix M M K => A i i) hf
    simp only [Matrix.sub_apply, Matrix.one_apply_eq, Matrix.vecMulVec_apply] at he
    calc
      (Y.transpose * X) i i = 1 - (1 - (Y.transpose * X) i i) := by abel
      _ = 1 - a i * b i := by rw [he]

#print axioms factor_rank
#print axioms cross_rank
#print axioms complement_rank
#print axioms rank_one_factorization
#print axioms one_extra_factorization
#print axioms one_extra_entries

end OvercompleteRank
