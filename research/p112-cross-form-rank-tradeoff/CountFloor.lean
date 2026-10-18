import Lean

/-
Copyright (c) 2026 commdata2338. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

Only the integer-count interface is formalized. Matrix ranks, support
classification, and the derivation of hcharge are explicit external premises.
-/
namespace P112CrossForm

theorem floor_of_counts (k n d mu charge : Nat)
    (hk : k ≤ 8)
    (hinc : 16 ≤ n + d)
    (hschur : 16 ≤ n + mu)
    (hcharge : 8 * n + (8 - k) * d + k * mu ≤ charge) :
    128 ≤ charge := by
  match k with
  | 0 => omega
  | 1 => omega
  | 2 => omega
  | 3 => omega
  | 4 => omega
  | 5 => omega
  | 6 => omega
  | 7 => omega
  | 8 => omega
  | k + 9 => omega

-- This is the source-level specialization for the new rank-(4,4) region.
theorem rank_four_floor (n d mu charge : Nat)
    (hinc : 16 ≤ n + d)
    (hschur : 16 ≤ n + mu)
    (hcharge : 8 * n + 4 * d + 4 * mu ≤ charge) :
    128 ≤ charge := by
  exact floor_of_counts 4 n d mu charge (by decide) hinc hschur hcharge

-- Pure directions are charged separately; their counts each dominate mu.
theorem floor_of_term_prices (k n d mu charge c01 c10 p01 p10 : Nat)
    (hk : k ≤ 8) (hinc : 16 ≤ n + d) (hschur : 16 ≤ n + mu)
    (hp01 : mu ≤ p01) (hp10 : mu ≤ p10) (hcross : k ≤ c01 + c10)
    (hbill : 8 * n + (8 - k) * d + c01 * p01 + c10 * p10 ≤ charge) :
    128 ≤ charge := by
  have h01 := Nat.mul_le_mul_left c01 hp01
  have h10 := Nat.mul_le_mul_left c10 hp10
  have hsum := Nat.mul_le_mul_right mu hcross
  rw [Nat.add_mul] at hsum
  apply floor_of_counts k n d mu charge hk hinc hschur
  omega

-- Concrete counterexamples to dropping one of the mathematical inputs.
example : 16 ≤ 8 + 8 ∧ 8 * 8 + (8 - 0) * 0 + 0 * 8 ≤ 64 ∧ ¬128 ≤ 64 := by decide
example : 16 ≤ 0 + 16 ∧ 8 * 0 + (8 - 8) * 16 + 8 * 0 ≤ 0 ∧ ¬128 ≤ 0 := by decide
example : 16 ≤ 8 + 8 ∧ 8 * 8 + (8 - 8) * 8 ≤ 64 ∧ ¬128 ≤ 64 := by decide
example : 16 ≤ 16 + 0 ∧ 7 * 16 ≤ 112 ∧ ¬128 ≤ 112 := by decide

#print axioms floor_of_counts
#print axioms rank_four_floor
#print axioms floor_of_term_prices
end P112CrossForm
