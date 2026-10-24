/- Scoped obstruction to the global-Pauli inner-hole repair.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
This is coefficient algebra, not a Python/native-word/compiler theorem. -/
import Mathlib.Data.Complex.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum

namespace PauliHole
noncomputable section

/-- The two extracted binary polar coefficients cannot both vanish. -/
theorem incompatible_polar_blocks (a : ZMod 2) :
    ¬ ((1+a = 0) ∧ (a = 0)) := by
  rintro ⟨h, ha⟩
  rw [ha] at h
  norm_num at h

def sign (b : Bool) : ℂ := if b then -1 else 1

/-- On the two selected bits, Q^-1(a+bP) has values
    A, -iB, -iB, -A. No translation character makes them constant,
    for any A≠0. This covers every invertible function of P. -/
theorem pauli_sector_cannot_remove_two_column_hole
    (A B : ℂ) (s t : Bool) (hA : A ≠ 0)
    (h01 : (-Complex.I * B) * sign s = A)
    (h10 : (-Complex.I * B) * sign t = A)
    (h11 : (-A) * sign s * sign t = A) : False := by
  cases s <;> cases t <;> simp only [sign, Bool.false_eq_true,
    ite_false, ite_true, mul_one, mul_neg_one, neg_neg] at h01 h10 h11
  all_goals
    apply hA
    first
    | linear_combination -(1/2 : ℂ) * h11
    | linear_combination -(1/2 : ℂ) * h01 - (1/2 : ℂ) * h10

#print axioms incompatible_polar_blocks
#print axioms pauli_sector_cannot_remove_two_column_hole
end
end PauliHole
