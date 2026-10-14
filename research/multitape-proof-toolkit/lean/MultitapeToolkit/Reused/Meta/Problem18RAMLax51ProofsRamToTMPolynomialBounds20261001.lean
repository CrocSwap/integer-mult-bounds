import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSparseMemory20261001
import Mathlib.Algebra.Polynomial.Degree.Support
import Mathlib.Tactic.Linarith

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Polynomial

/-- Natural-coefficient polynomials are monotone on natural arguments. -/
theorem polynomial_eval_mono (p : Polynomial ℕ) {m n : ℕ} (h : m ≤ n) :
    p.eval m ≤ p.eval n := by
  rw [Polynomial.eval_eq_sum, Polynomial.eval_eq_sum]
  apply Finset.sum_le_sum
  intro i hi
  exact Nat.mul_le_mul_left _ (Nat.pow_le_pow_left h i)

/-- A concrete coefficient sum used to dominate a natural-coefficient
polynomial by one monomial. -/
def polyCoeffSum (p : Polynomial ℕ) : ℕ :=
  p.support.sum p.coeff

theorem polynomial_eval_le_coeffSum_mul (p : Polynomial ℕ) (n : ℕ) :
    p.eval n ≤ polyCoeffSum p * (n + 1) ^ p.natDegree := by
  rw [Polynomial.eval_eq_sum]
  calc
    p.sum (fun i a => a * n ^ i) ≤
        p.support.sum (fun i => p.coeff i * (n + 1) ^ p.natDegree) := by
      apply Finset.sum_le_sum
      intro i hi
      apply Nat.mul_le_mul_left
      exact (Nat.pow_le_pow_left (by omega) i).trans
        (Nat.pow_le_pow_right (by omega) (Polynomial.le_natDegree_of_mem_supp i hi))
    _ = polyCoeffSum p * (n + 1) ^ p.natDegree := by
      rw [polyCoeffSum, Finset.sum_mul]

/-- Every natural-coefficient polynomial is bounded by the especially
simple polynomial `C coeffSum * (X + 1)^natDegree`.  This normal form is
what the reverse TM interpreter computes as its word budget. -/
noncomputable def polynomialSimpleMajorant (p : Polynomial ℕ) : Polynomial ℕ :=
  C (polyCoeffSum p) * (X + 1) ^ p.natDegree

@[simp] theorem polynomialSimpleMajorant_eval (p : Polynomial ℕ) (n : ℕ) :
    (polynomialSimpleMajorant p).eval n =
      polyCoeffSum p * (n + 1) ^ p.natDegree := by
  simp [polynomialSimpleMajorant]

theorem polynomial_eval_le_simpleMajorant (p : Polynomial ℕ) (n : ℕ) :
    p.eval n ≤ (polynomialSimpleMajorant p).eval n := by
  simpa using polynomial_eval_le_coeffSum_mul p n

end Lax51Proofs.RamToTM
