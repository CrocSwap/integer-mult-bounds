import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp


open scoped BigOperators

namespace OrdinaryClock

/-- A counted paid owner has disjoint equal low packets. Each pivot uses up to nine copies. -/
theorem ninePhysical {P B Q : ℕ} (hB : 0 < B) (hQ : 0 < Q) (V factor : ℝ)
    (hV : 0 ≤ V) (hf : 0 ≤ factor) (children : Fin P → Fin Q → ℕ)
    (hnine : ∀ i j, children i j ≤ 9) :
    (∑ i, ∑ j, (children i j : ℝ) * (V/((B:ℝ)*Q)) * factor) ≤
      9*((P:ℝ)/B)*V*factor := by
  have positiveB : (0:ℝ) < B := by exact_mod_cast hB
  have positiveQ : (0:ℝ) < Q := by exact_mod_cast hQ
  have hvol : 0 ≤ V/((B:ℝ)*Q) := by positivity
  calc
    _ ≤ ∑ _i : Fin P, ∑ _j : Fin Q, (9:ℝ)*(V/((B:ℝ)*Q))*factor := by
      apply Finset.sum_le_sum
      intro i _
      apply Finset.sum_le_sum
      intro j _
      have h9 : (children i j : ℝ) ≤ 9 := by exact_mod_cast hnine i j
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right h9 hvol) hf
    _ = _ := by simp; field_simp

/-- Each physical child occurrence has its own index, area, and exponent cost. -/
theorem paidTree {Node : Type*} (rank : Node → ℕ) (arity : Node → ℕ)
    (child : Node → ℕ → Node) (cost rows power : Node → ℝ) (L σ : ℝ) (hL : 0 ≤ L) (hσ : σ < 1)
    (descend : ∀ n i, i < arity n → rank (child n i) < rank n)
    (localCost : ∀ n, cost n ≤ L * (rows n + power n) +
      ∑ i ∈ Finset.range (arity n), cost (child n i))
    (rowMoment : ∀ n, (∑ i ∈ Finset.range (arity n), rows (child n i)) ≤ σ * rows n)
    (powerMoment : ∀ n, (∑ i ∈ Finset.range (arity n), power (child n i)) ≤ σ * power n)
    (root : Node) : cost root ≤ (L / (1-σ)) * (rows root + power root) := by
  suffices H : ∀ k n, rank n = k → cost n ≤ (L / (1-σ)) * (rows n + power n) by
    exact H _ _ rfl
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    intro n hn
    have hp : 0 < 1-σ := sub_pos.mpr hσ
    have hK : 0 ≤ L / (1-σ) := div_nonneg hL hp.le
    have childBounds : (∑ i ∈ Finset.range (arity n), cost (child n i)) ≤
        ∑ i ∈ Finset.range (arity n), (L / (1-σ)) * (rows (child n i) + power (child n i)) := by
      apply Finset.sum_le_sum
      intro i hi
      exact ih _ (hn ▸ descend n i (Finset.mem_range.mp hi)) _ rfl
    rw [← Finset.mul_sum, Finset.sum_add_distrib] at childBounds
    calc
      cost n ≤ _ := localCost n
      _ ≤ L * (rows n + power n) + (L / (1-σ)) *
            (σ * rows n + σ * power n) := by
              exact add_le_add_right (childBounds.trans (mul_le_mul_of_nonneg_left
                (add_le_add (rowMoment n) (powerMoment n)) hK)) _
      _ = _ := by field_simp; ring

/-- Fixed program factors multiply across the finite ordinary stages. -/
theorem stageClock (J B : ℕ → ℝ) (A : ℝ) (hA : 1 ≤ A) (init : B 0 ≤ A)
    (hJ : ∀ n, 2 ≤ J n) (step : ∀ n, B (n+1) ≤ J n ^ 14 * (1+B n)) (n : ℕ) :
    B n ≤ A * ∏ i ∈ Finset.range n, J i ^ 15 := by
  induction n with
  | zero => simpa using init
  | succ n ih =>
    have hJ₁ : ∀ i, 1 ≤ J i := fun i => le_trans (by norm_num) (hJ i)
    have hb : ∀ k, 1 ≤ A * ∏ i ∈ Finset.range k, J i ^ 15 := by
      intro k
      induction k with
      | zero => simpa using hA
      | succ k hk =>
        rw [Finset.prod_range_succ, ← mul_assoc]
        exact hk.trans (le_mul_of_one_le_right (le_trans zero_le_one hk) (one_le_pow₀ (hJ₁ k)))
    have hs := hb n
    have hK : 0 ≤ J n ^ 14 := pow_nonneg (le_trans (by norm_num) (hJ n)) _
    have hP : 0 ≤ A * ∏ i ∈ Finset.range n, J i ^ 15 := le_trans zero_le_one hs
    rw [Finset.prod_range_succ]
    calc
      B (n+1) ≤ J n ^ 14 * (1+B n) := step n
      _ ≤ J n ^ 14 * (2 * (A * ∏ i ∈ Finset.range n, J i ^ 15)) := by
        apply mul_le_mul_of_nonneg_left _ hK
        linarith
      _ ≤ J n ^ 14 * (J n * (A * ∏ i ∈ Finset.range n, J i ^ 15)) := by
        exact mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_right (hJ n) hP) hK
      _ = _ := by ring

#print axioms ninePhysical
#print axioms paidTree
#print axioms stageClock

end OrdinaryClock
