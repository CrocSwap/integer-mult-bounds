/-
CallerTightNeed (lane TIGHTPAD, Nov 20).  Item (1): the tightness hypothesis n + 2 = |iota| CANNOT be dropped from the
RC2 block-invertibility step (CallerSGram.sgPairCoverage / CallerAsm.G_blk_unit_ord / word_hG), even when the weaker
n + 2 <= |iota| (what role_count_lam supplies) holds and every other hypothesis holds.

Witness: the DIRECT SUM of two copies of the k = 2, n = 2 Q = 0 frame of CallerTightDeg (V_0 = 2, V_1 = -1/2 on each copy;
copy 0 = roles 0,1 / stages 0,1, copy 1 = roles 2,3 / stages 2,3).  P = -1, every diagonal K-block invertible
(3 I or 1/2 I), char 0, |iota| = 8 = 2k (Q = 0), n = 4, so n + 2 = 6 < 8 (non-tight, e' = 2).
  * `sumD_prod`, `sumD_diag`              : all hypotheses of sgPairCoverage except hn.
  * `sumD_cover_empty`, `sumD_not_cover`  : stages 0 and 2 have NO common role, so the CROSS / RC2 pair conclusion fails.
  * `sumD_G_singular`                     : the Gram block G_{0,2} = 0 (not invertible): RC2's hG fails.
  * `pairCoverage_needs_tight`            : packaged refutation of "sgPairCoverage with n + 2 <= k m".
Word level ([P] paper, notes TP.md): the same direct sum of legal words is legal and keeps every hypothesis of word_hp_B
except tightness; m >= 109 copies of CallerQZero.C1W give cHat = 107.91 > HP(3m)  (and m >= 26 copies refute the
untight word_hpq), so the padding lemma is false.
Kernel only.
-/
import Nov15.CallerSGram

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerTight
open Finset Matrix CallerSign

def aD : Fin 2 → ℚ := ![1, -3/2]
/-- role r (copy r/2, local r%2), column (s, a) (copy s/2, local stage s%2). -/
def AD : Matrix (Fin 4) (Fin 4 × Fin 2) ℚ :=
  Matrix.of fun r c => if r.val / 2 = c.1.val / 2 ∧ r.val % 2 = c.2.val then aD ⟨c.1.val % 2, Nat.mod_lt _ (by norm_num)⟩ else 0
def BD : Matrix (Fin 4) (Fin 4 × Fin 2) ℚ :=
  Matrix.of fun r c => if r.val / 2 = c.1.val / 2 ∧ r.val % 2 = c.2.val then 1 else 0

/-- stage t is diagonal: 1 + a_{t%2} on the two roles of copy t/2, 1 elsewhere. -/
def dD (t : ℕ) : Fin 4 → ℚ := fun r => if r.val / 2 = t / 2 then 1 + aD ⟨t % 2, Nat.mod_lt _ (by norm_num)⟩ else 1

theorem sumD_stage (t : ℕ) (ht : t < 4) :
    sgStage AD BD (fun i => (i.1 : ℕ)) t = Matrix.diagonal (dD t) := by
  ext i j
  interval_cases t <;> fin_cases i <;> fin_cases j <;>
    simp [sgStage, blkPi, AD, BD, aD, dD, Matrix.mul_apply, Matrix.one_apply,
      Matrix.diagonal_apply, Fintype.sum_prod_type, Fin.sum_univ_succ]

theorem sumD_prod : sgProd AD BD (fun i => (i.1 : ℕ)) 4 = -1 := by
  simp only [sgProd, sumD_stage 0 (by norm_num), sumD_stage 1 (by norm_num), sumD_stage 2 (by norm_num),
    sumD_stage 3 (by norm_num), Matrix.mul_one, Matrix.diagonal_mul_diagonal]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [dD, aD, Matrix.diagonal_apply] <;> norm_num

theorem sumD_diag : ∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG AD BD)) t t).det := by
  intro t
  rw [isUnit_iff_ne_zero]
  fin_cases t <;>
    simp [Matrix.det_fin_two, blkOf, sgK, sgDiag, sgUp, sgLow, sgG, AD, BD, aD, Matrix.mul_apply,
      Matrix.one_apply, Fin.sum_univ_succ, Matrix.transpose_apply] <;> norm_num

/-- non-tight: n + m = 6 < k m = 8, while n + 2 <= |iota| (the role_count_lam form) holds. -/
theorem sumD_nontight : 4 + 2 < 4 * 2 ∧ 4 + 2 ≤ Fintype.card (Fin 4 × Fin 2) := by simp

theorem sumD_cover_empty : coverSet AD BD 0 2 = ∅ := by
  classical
  ext r
  simp only [coverSet, meets, Finset.mem_filter, Finset.mem_univ, true_and, Finset.notMem_empty, iff_false]
  fin_cases r <;> simp [AD, BD]

theorem sumD_not_cover : ¬ (2 ≤ (coverSet AD BD 0 2).card) := by
  rw [sumD_cover_empty]; simp

theorem sumD_G_singular : ¬ IsUnit (blkOf (sgG AD BD) 0 2).det := by
  rw [isUnit_iff_ne_zero, not_not]
  simp [Matrix.det_fin_two, blkOf, sgG, AD, BD, aD, Matrix.mul_apply, Fin.sum_univ_succ, Matrix.transpose_apply]

/-- the refutation, packaged: sgPairCoverage with `n + m = k m` weakened to `n + m <= k m` is false. -/
theorem pairCoverage_needs_tight :
    ¬ (∀ (A B : Matrix (Fin 4) (Fin 4 × Fin 2) ℚ), sgProd A B (fun i => (i.1 : ℕ)) 4 = -1 →
        4 + 2 ≤ 4 * 2 →
        (∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) t t).det) →
        ∀ s t : Fin 4, s ≠ t → 2 ≤ (coverSet A B s t).card) := by
  intro h
  exact sumD_not_cover (h AD BD sumD_prod (by norm_num) sumD_diag 0 2 (by decide))

/-- control: each copy alone is tight and the law holds inside a copy (stages 0,1 share both roles 0,1). -/
theorem sumD_cover_inside : 2 ≤ (coverSet AD BD 0 1).card := by
  classical
  have hm : ∀ r : Fin 4, (meets AD BD r 0 ∧ meets AD BD r 1) → r ∈ coverSet AD BD 0 1 := by
    intro r h; unfold coverSet; exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, h⟩
  have : ({0, 1} : Finset (Fin 4)) ⊆ coverSet AD BD 0 1 := by
    intro r hr
    simp only [Finset.mem_insert, Finset.mem_singleton] at hr
    rcases hr with rfl | rfl
    · exact hm 0 ⟨⟨0, Or.inr (by simp [BD])⟩, ⟨0, Or.inr (by simp [BD])⟩⟩
    · exact hm 1 ⟨⟨1, Or.inr (by simp [BD])⟩, ⟨1, Or.inr (by simp [BD])⟩⟩
  exact le_trans (by decide) (Finset.card_le_card this)

end CallerTight

#print axioms CallerTight.sumD_prod
#print axioms CallerTight.sumD_diag
#print axioms CallerTight.sumD_not_cover
#print axioms CallerTight.sumD_G_singular
#print axioms CallerTight.pairCoverage_needs_tight
#print axioms CallerTight.sumD_cover_inside
