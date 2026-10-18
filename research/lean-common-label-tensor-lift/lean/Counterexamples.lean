import TensorLift
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
Small kernel-checked limits of the tensor lift. These disprove shortcuts, not
the common-label theorem or PR2287. Gareth Davidson with OpenAI Codex. Apache-2.0.
-/

open LemmaG

namespace CommonLabelTensor.Boundary

def bareWord : List (Event Unit Bool ℚ) :=
  [.scale () 2, .relabel () false true]

def bareRecipe (f : ℕ) (_ _ : Bool) (x : ℚ) : ℚ := (1 / 2) ^ f * x

theorem bare_one_column (x : ℚ) :
    Stream.physRun (bareRecipe 1) bareWord (fun _ => x) () = x := by
  norm_num [bareWord, bareRecipe, Stream.physRun, Event.phys]
  ring

theorem bare_two_columns :
    Stream.physRun (bareRecipe 2) bareWord (fun _ => 1) () = 1 / 2 := by
  norm_num [bareWord, bareRecipe, Stream.physRun, Event.phys]

/-- The one-column physical identity alone does not imply the lifted identity. -/
theorem bare_endpoint_does_not_lift :
    Stream.physRun (bareRecipe 2) bareWord (fun _ => 1) () ≠ 1 := by
  rw [bare_two_columns]
  norm_num

/-- The role SCALE remains -1 even when an address tensor has two columns. -/
theorem role_sign_is_not_tensor_squared :
    Stream.scalRun ([Event.scale () (-1)] : List (Event Unit Bool ℚ)) (fun _ => 1) ()
      ≠ (-1 : ℚ) ^ 2 := by
  norm_num [Stream.scalRun, Stream.physRun, Event.scal, Event.phys]

/-- By contrast, a -1 phase within each unary recipe contributes (-1)^2. -/
theorem unary_sign_does_tensor : ((-1 : ℚ) * (-1)) = 1 := by norm_num

/-- Tensor products do not distribute over sums of whole operators. -/
theorem tensor_of_sum_boundary : ((1 + 1 : ℚ) ^ 2) ≠ 1 ^ 2 + 1 ^ 2 := by norm_num

/-- The 2x2 diagonal array cannot be a pure tensor over Q. -/
theorem correlated_array_not_pure :
    ¬ ∃ a b c d : ℚ, a * c = 1 ∧ a * d = 0 ∧ b * c = 0 ∧ b * d = 1 := by
  rintro ⟨a, b, c, d, hac, had, hbc, hbd⟩
  have h : (a * c) * (b * d) = (a * d) * (b * c) := by ring
  rw [hac, had, hbc, hbd] at h
  norm_num at h

end CommonLabelTensor.Boundary
