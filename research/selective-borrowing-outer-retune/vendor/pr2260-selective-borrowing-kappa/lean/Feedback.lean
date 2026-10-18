import Mathlib.Tactic.Linarith
import Mathlib.Data.Real.Basic

/-! Sufficient all-cut feedback bounds for the selective-borrowing invoice.
These lemmas do not assert that a particular implementation meets the defect
contract; the independently recounted instruction envelope supplies that data.
-/

namespace IntegerMultBounds.SelectiveBorrowing

theorem absorb_feedback (error coefficient budget : ℝ)
    (herror : 0 ≤ error) (hsmall : coefficient ≤ 1 / 2)
    (hfeedback : error ≤ coefficient * (budget + error)) :
    error ≤ 2 * coefficient * budget := by
  have h := mul_nonneg (sub_nonneg.mpr hsmall) herror
  nlinarith

theorem relative_error_of_feedback (error amplification defect unit initial target : ℝ)
    (herror : 0 ≤ error) (hinitial : 0 ≤ initial)
    (hsmall : defect * unit ≤ 1 / 2)
    (hbudget : 2 * defect * unit * amplification ≤ target)
    (hfeedback : error ≤ defect * unit * (amplification * initial + error)) :
    error ≤ target * initial := by
  calc
    error ≤ 2 * (defect * unit) * (amplification * initial) :=
      absorb_feedback error (defect * unit) (amplification * initial) herror hsmall hfeedback
    _ = (2 * defect * unit * amplification) * initial := by simp only [mul_assoc]
    _ ≤ target * initial := mul_le_mul_of_nonneg_right hbudget hinitial

theorem owner_stock_reserve (oldHelpers newHelpers cleanup : ℕ)
    (hreserve : newHelpers ≤ oldHelpers) :
    newHelpers + cleanup ≤ oldHelpers + cleanup :=
  Nat.add_le_add_right hreserve cleanup

end IntegerMultBounds.SelectiveBorrowing

#print axioms IntegerMultBounds.SelectiveBorrowing.absorb_feedback
#print axioms IntegerMultBounds.SelectiveBorrowing.relative_error_of_feedback
#print axioms IntegerMultBounds.SelectiveBorrowing.owner_stock_reserve
