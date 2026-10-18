import CyclicSchur
import Init.Grind.CommRing.Int

/- The examples below reject index and coefficient errors in the exact reduction. -/
namespace CyclicSchur.Controls

def data8 (i : Nat) : Int :=
  match i with
  | 0 => -11
  | 1 => -12
  | 2 => -13
  | 3 => 2
  | 4 => 1
  | 5 => 0
  | 6 => -1
  | _ => -2

def two (_ : Nat) : Int := 2
def solution8 (i : Nat) : Int := i + 1
def ends8 (k : Nat) : Int := k + 6

theorem reference_solution : ScalarSolution 8 3 data8 two solution8 := by
  have h : ∀ i : Fin 8, solution8 i = data8 i + two i * solution8 ((i + 8 - 3) % 8) :=
    by decide
  intro i hi
  exact h ⟨i, hi⟩

theorem reference_closure :
    ScalarSolution 3 (childStride 8 3) (childData 8 3 (by decide) data8 two)
      (childCoefficient 8 3 (by decide) two) ends8 := by
  have h := ((scalar_schur_iff (by decide : 0 < 3) (by decide : 3 ≤ 8)
    data8 two solution8).mp reference_solution).1
  have he : tail 8 3 solution8 = ends8 := by
    funext k
    simp only [tail, endpoint, solution8, ends8]
    omega
  rw [he] at h
  exact h

/- The positive remainder gives stride two. The correct child stride is one. -/
theorem wrong_child_sign_rejected :
    ¬ ScalarSolution 3 (8 % 3) (childData 8 3 (by decide) data8 two)
      (childCoefficient 8 3 (by decide) two) ends8 := by
  intro h
  have bad := h 0 (by decide)
  simp [ends8, childData, childCoefficient, zeroSeed, chainProduct, endpoint, data8, two] at bad

/- Starting the tail one entry early changes the closure right-hand side. -/
theorem wrong_tail_rejected :
    ¬ ScalarSolution 3 (childStride 8 3)
      (fun k => zeroSeed 3 (by decide) data8 two (8 - 3 - 1 + k))
      (fun k => chainProduct 3 (by decide) two (8 - 3 - 1 + k)) ends8 := by
  intro h
  have bad := h 0 (by decide)
  simp [ends8, childStride, zeroSeed, chainProduct, data8, two] at bad

/- A chain product includes the coefficient at the chain start. -/
theorem missing_start_factor_rejected :
    ¬ ScalarSolution 3 (childStride 8 3) (childData 8 3 (by decide) data8 two)
      (fun k => chainProduct 3 (by decide) two (endpoint 8 3 k) / 2) ends8 := by
  intro h
  have bad := h 0 (by decide)
  simp [ends8, childStride, childData, childCoefficient, zeroSeed, chainProduct,
    endpoint, data8, two] at bad

/- A source pass must read the updated predecessor. -/
theorem stale_predecessor_rejected :
    data8 6 + two 6 * data8 (6 - 3) ≠ zeroSeed 3 (by decide) data8 two 6 := by
  simp [data8, two, zeroSeed]

end CyclicSchur.Controls
