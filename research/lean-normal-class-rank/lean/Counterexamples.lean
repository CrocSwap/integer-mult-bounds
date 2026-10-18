import NormalClassRank

open Matrix Module
namespace NormalClassRank.Controls

def equalClass : Matrix (Fin 1) (Fin 1) ℚ := 1

theorem equal_class_compatible :
    ∀ i j : Fin 1, equalClass i j ≠ 0 → (0 : ℕ) = 0 := by simp

theorem equal_class_violates_rank :
    ¬ Fintype.card (Fin 1) ≤ 2 * (1-equalClass).rank := by
  norm_num [equalClass]

def allOnes : Matrix (Fin 3) (Fin 3) ℚ := Matrix.vecMulVec (fun _ => 1) (fun _ => 1)
def incompatible : Matrix (Fin 3) (Fin 3) ℚ := 1 - allOnes

theorem incompatible_diagonal_zero (i : Fin 3) : incompatible i i = 0 := by
  simp [incompatible, allOnes, Matrix.sub_apply, Matrix.vecMulVec_apply]

theorem incompatible_violates_rank :
    ¬ Fintype.card (Fin 3) ≤ 2 * (1-incompatible).rank := by
  have he : 1-incompatible = allOnes := by unfold incompatible; abel
  have hr : allOnes.rank ≤ 1 := Matrix.rank_vecMulVec_le _ _
  rw [he]
  norm_num only [Fintype.card_fin]
  omega

def cycle : Matrix (Fin 2) (Fin 2) ℚ := !![0, 1; 1, 0]
def alpha (i : Fin 2) : ℕ := i.val
def beta (i : Fin 2) : ℕ := 1-i.val

theorem cycle_distinct (i : Fin 2) : alpha i ≠ beta i := by
  fin_cases i <;> norm_num [alpha, beta]

theorem cycle_compatible : ∀ i j, cycle i j ≠ 0 → beta i = alpha j := by
  intro i j h
  fin_cases i <;> fin_cases j <;> norm_num [cycle, alpha, beta] at *

theorem cycle_rank : (1-cycle).rank = 1 := by
  have he : 1-cycle = Matrix.vecMulVec (![1,-1] : Fin 2 → ℚ) ![1,-1] := by
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [cycle, Matrix.vecMulVec_apply]
  have hu : (1-cycle).rank ≤ 1 := by rw [he]; exact Matrix.rank_vecMulVec_le _ _
  have hl := normal_class_rank cycle alpha beta cycle_distinct cycle_compatible
  norm_num only [Fintype.card_fin] at hl
  omega

theorem cycle_kernel : finrank ℚ (LinearMap.ker (1-cycle).mulVecLin) = 1 := by
  have h := LinearMap.finrank_range_add_finrank_ker (1-cycle).mulVecLin
  change (1-cycle).rank + _ = _ at h
  rw [cycle_rank, Module.finrank_pi] at h
  norm_num at h
  omega

end NormalClassRank.Controls
