import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

namespace RetimedGrid

open scoped BigOperators

/-- A row has a causal budget, a total coefficient mass, and a dyadic height. -/
inductive Row : ℕ → ℝ → ℕ → Prop
  | entry {m : ℝ} (atMostOne : m ≤ 1) : Row 0 m 0
  | reserve {j m d} (prior : Row j m d) : Row (j+1) m d
  | combine {j n : ℕ} {m w : Fin n → ℝ} {d : Fin n → ℕ} {out : ℕ}
      (prior : ∀ i, Row j (m i) (d i))
      (sign : ∀ i, 0 ≤ w i)
      (mass : ∑ i, w i ≤ (2 : ℝ)^436)
      (height : out ≤ 148 + Finset.univ.sup d) :
      Row (j+1) (∑ i, w i * m i) out

/-- The number of causal parents is arbitrary. A joined row pays for one raw context. -/
theorem joined {j : ℕ} {m : ℝ} {d : ℕ} (r : Row j m d) :
    m ≤ ((2 : ℝ)^436)^j ∧ d ≤ 148*j := by
  induction r with
  | entry h => simpa using h
  | @reserve j m d _ ih =>
    constructor
    · calc
        m ≤ ((2 : ℝ)^436)^j := ih.1
        _ = ((2 : ℝ)^436)^j * 1 := (mul_one _).symm
        _ ≤ ((2 : ℝ)^436)^(j+1) := by
          rw [pow_succ _ j]
          exact mul_le_mul_of_nonneg_left (one_le_pow₀ (by norm_num)) (by positivity)
    · omega
  | @combine j n m w d out prior sign mass height ih =>
    constructor
    · calc
        ∑ i, w i * m i ≤ ∑ i, w i * ((2 : ℝ)^436)^j := by
          exact Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (ih i).1 (sign i)
        _ = (∑ i, w i) * ((2 : ℝ)^436)^j := (Finset.sum_mul _ _ _).symm
        _ ≤ (2 : ℝ)^436 * ((2 : ℝ)^436)^j :=
          mul_le_mul_of_nonneg_right mass (by positivity)
        _ = ((2 : ℝ)^436)^(j+1) := by rw [pow_succ _ j, mul_comm]
    · have bound : Finset.univ.sup d ≤ 148*j := Finset.sup_le fun i _ => (ih i).2
      omega

/-- Root reserve for a descent with proved causal depth and actual remaining rank. -/
theorem root_width {D M H ell K : ℕ}
    (causal : K ≤ (4*H+1)*ell)
    (rank : 872*(4*H+1)<M)
    (descent : M*ell≤D) :
    (D+1)/2 + 148*K ≤ D ∧ (D+2)/2 + 436*K + 1 ≤ D+2 := by
  have h : 872*K ≤ D := calc
    872*K ≤ 872*((4*H+1)*ell) := Nat.mul_le_mul_left _ causal
    _ = (872*(4*H+1))*ell := (Nat.mul_assoc _ _ _).symm
    _ ≤ M*ell := Nat.mul_le_mul_right _ rank.le
    _ ≤ D := descent
  omega

#print axioms joined
#print axioms root_width

end RetimedGrid
