import Mathlib.Tactic

open scoped BigOperators

namespace QuotientAverage

/-- A card with no exceptional case spends one, three, three or five calls. -/
theorem regularMix (p11 p10 p01 p00 : ℝ) (h : p11 + p10 + p01 + p00 = 1) :
    p11 + 3*p10 + 3*p01 + 5*p00 =
      5 - 2 * (p11+p10) - 2 * (p11+p01) := by
  linarith

/-- K is the number of all vectors. Each exceptional line holds two nonzero vectors. -/
theorem finiteBound (K : ℝ) (hK : 729 ≤ K) :
    5 - 4*(2*K / (3*(K-1))) + 8/(K-1) < 75/32 := by
  have hpos : 0 < K-1 := by linarith
  have eq : 5 - 4*(2*K / (3*(K-1))) + 8/(K-1) =
      (7*(K-1) + 16)/(3*(K-1)) := by
    field_simp
    ring
  rw [eq]
  apply (div_lt_iff₀ (show 0 < 3*(K-1) by positivity)).mpr
  linarith

/-- Sum over the realized low classes with their actual common field volume. -/
theorem projectedPhysical {P B Q : ℕ} (hB : 0 < B) (hQ : 0 < Q) (V factor : ℝ)
    (hV : 0 ≤ V) (hf : 0 ≤ factor) (children : Fin P → Fin Q → ℕ)
    (labels : ∀ i, (∑ j, (children i j : ℝ)) ≤ (75/32:ℝ)*Q) :
    (∑ i, ∑ j, (children i j : ℝ) * (V/((B:ℝ)*Q)) * factor) ≤
      (75/32:ℝ) * (P/B) * V * factor := by
  have positiveB : (0:ℝ) < B := by exact_mod_cast hB
  have positiveQ : (0:ℝ) < Q := by exact_mod_cast hQ
  have hvol : 0 ≤ V/((B:ℝ)*Q) := by positivity
  calc
    _ ≤ ∑ _i : Fin P, ((75/32:ℝ)*Q) * (V/((B:ℝ)*Q)) * factor := by
      apply Finset.sum_le_sum
      intro i _
      rw [← Finset.sum_mul, ← Finset.sum_mul]
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right (labels i) hvol) hf
    _ = _ := by simp; field_simp

/-- A subtree either already has the stopped direct bill or exposes a funded quotient step. -/
theorem mixedTree {Node : Type*} (rank arity : Node → ℕ) (child : Node → ℕ → Node)
    (cost moment : Node → ℝ) (positive : ∀ n, 0 ≤ moment n)
    (descend : ∀ n i, i < arity n → rank (child n i) < rank n)
    (one : ∀ n, cost n ≤ 376 * moment n ∨
      (cost n ≤ moment n + ∑ i ∈ Finset.range (arity n), cost (child n i)) ∧
      (∑ i ∈ Finset.range (arity n), moment (child n i)) ≤ (375/376) * moment n)
    (root : Node) : cost root ≤ 376 * moment root := by
  suffices H : ∀ k n, rank n = k → cost n ≤ 376 * moment n by
    exact H _ _ rfl
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    intro n hn
    rcases one n with stop | ⟨work, mass⟩
    · exact stop
    · have all : (∑ i ∈ Finset.range (arity n), cost (child n i)) ≤
          ∑ i ∈ Finset.range (arity n), 376 * moment (child n i) := by
        apply Finset.sum_le_sum
        intro i hi
        exact ih _ (hn ▸ descend n i (Finset.mem_range.mp hi)) _ rfl
      rw [← Finset.mul_sum] at all
      linarith [positive n]

#print axioms regularMix
#print axioms finiteBound
#print axioms projectedPhysical
#print axioms mixedTree

end QuotientAverage
