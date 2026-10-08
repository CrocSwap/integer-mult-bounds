import Mathlib.Data.Matrix.Basic
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.Ring

/-! Rosowski's known division-free even-inner-dimension construction.
All multiplication gates are displayed explicitly; only addition/subtraction
is used to reconstruct outputs. This is a known leaf, not a novelty claim. -/
namespace PersonalMatrix.RosowskiEven
open scoped BigOperators
variable {K I H J : Type*} [CommRing K] [Fintype I] [Fintype H] [Fintype J]
abbrev Gates (I H J : Type*) := ((I×H) ⊕ (I×H)) ⊕ ((H×J) ⊕ ((I×H)×J))

def products (A : Matrix I (H×Bool) K) (B : Matrix (H×Bool) (Option J) K) : Gates I H J → K
  | Sum.inl (Sum.inl (i,h)) => A i (h,false) * (B (h,false) none + A i (h,true))
  | Sum.inl (Sum.inr (i,h)) => A i (h,true) * (B (h,true) none - A i (h,false))
  | Sum.inr (Sum.inl (h,j)) => B (h,true) (some j) * (B (h,false) none + B (h,false) (some j))
  | Sum.inr (Sum.inr ((i,h),j)) => (A i (h,false) + B (h,true) (some j)) *
      (A i (h,true) + B (h,false) none + B (h,false) (some j))

def reconstruct (p : Gates I H J → K) : Matrix I (Option J) K
  | i, none => ∑ h : H, (p (Sum.inl (Sum.inl (i,h))) + p (Sum.inl (Sum.inr (i,h))))
  | i, some j => ∑ h : H, (p (Sum.inr (Sum.inr ((i,h),j))) -
      p (Sum.inl (Sum.inl (i,h))) - p (Sum.inr (Sum.inl (h,j))))

def eval (A : Matrix I (H×Bool) K) (B : Matrix (H×Bool) (Option J) K) :=
  reconstruct (products A B)

theorem sound (A : Matrix I (H×Bool) K) (B : Matrix (H×Bool) (Option J) K) :
    eval A B = A*B := by
  ext i j
  cases j <;> simp only [eval, reconstruct, products, Matrix.mul_apply,
    Fintype.sum_prod_type, Fintype.sum_bool]
  all_goals
    apply Finset.sum_congr rfl
    intro h _
    ring

theorem gate_count : Fintype.card (Gates I H J) =
    Fintype.card H * (Fintype.card I * (Fintype.card J + 1) +
      Fintype.card I + Fintype.card J) := by
  simp only [Gates, Fintype.card_sum, Fintype.card_prod]
  ring

theorem square_four_gate_count : Fintype.card (Gates (Fin 4) (Fin 2) (Fin 3)) = 46 := by
  simp [Gates]

/-- Actual rectangular4×4 matrices (paired inner indexFin2×Bool and four
output columnsOptionFin3); coordinate relabelling does not change multiplication. -/
theorem square_four_sound
    (A : Matrix (Fin 4) (Fin 2×Bool) K) (B : Matrix (Fin 2×Bool) (Option (Fin 3)) K) :
    eval A B = A*B := sound A B

#print axioms sound
#print axioms gate_count
#print axioms square_four_gate_count
#print axioms square_four_sound
#check @sound
end PersonalMatrix.RosowskiEven
