import Mathlib.Tactic

namespace BoundedDirect

def privateLog (s : ℕ) : ℕ := s + 1024*(128*s^2+s+88)
def inputFloor (s : ℕ) : ℕ := ((2^(s-1) - 2)/6)-1

/-- Exhaust the actual small-precision range with kernel-reduced integer arithmetic. -/
theorem prefixSmall (s : Fin 32) : privateLog s ≤ 84484466 + inputFloor s := by
  fin_cases s <;> norm_num [privateLog, inputFloor]

theorem attained : privateLog 27 - inputFloor 27 = 84484466 := by
  norm_num [privateLog, inputFloor]

/-- The earlier quadratic private bound fits the input from s = 32 on. -/
theorem polynomialGrowth (s : ℕ) (hs : 32 ≤ s) :
    privateLog (s+1) ≤ 2*privateLog s := by
  unfold privateLog
  nlinarith [Nat.mul_le_mul hs hs]

theorem tailPays (j : ℕ) : privateLog (j+32) < 2^(j+28) := by
  induction j with
  | zero => norm_num [privateLog]
  | succ j ih =>
    have h := polynomialGrowth (j+32) (by omega)
    have need := Nat.mul_lt_mul_of_pos_left ih (by decide : 0 < 2)
    calc
      privateLog (j+1+32) = privateLog ((j+32)+1) := by congr 1
      _ ≤ 2*privateLog (j+32) := h
      _ < 2*2^(j+28) := need
      _ = 2^(j+28)*2 := Nat.mul_comm _ _
      _ = 2^((j+28)+1) := (pow_succ _ _).symm
      _ = 2^(j+1+28) := by congr 1

/-- This tariff covers the exact single-child direct route and every unequal quotient count. -/
theorem twoModes (children : ℝ) (h : children ≤ 75/32 ∨ children = 1) :
    children / (47/20) ≤ 375/376 := by
  rcases h with h | h
  · linarith
  · rw [h]; norm_num

theorem geometric : (1:ℝ) / (1 - 375/376) = 376 := by norm_num

#print axioms prefixSmall
#print axioms tailPays
#print axioms twoModes
#print axioms geometric

end BoundedDirect
