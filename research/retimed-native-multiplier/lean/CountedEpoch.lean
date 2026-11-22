import Mathlib.Tactic

set_option exponentiation.threshold 4096

namespace CountedEpoch

def ratio : ℚ := (5/4 : ℚ)^430
def ceiling (h : ℕ) : ℚ := (2:ℚ)^h / (4*134^430)

theorem depthBound (k : ℕ) :
    4*(134:ℚ)^430 * ratio^k ≤ 2^(2+8*430+430*k) := by
  have a := pow_le_pow_left₀ (by norm_num : (0:ℚ) ≤ 134)
    (by norm_num : (134:ℚ) ≤ 2^8) 430
  have r := pow_le_pow_left₀ (by norm_num : (0:ℚ) ≤ 5/4)
    (by norm_num : (5/4:ℚ) ≤ 2) (430*k)
  calc
    _ = 4*(134:ℚ)^430 * (5/4 : ℚ)^(430*k) := by rw [pow_mul]; rfl
    _ ≤ 4*((2:ℚ)^8)^430 * 2^(430*k) := by gcongr
    _ = (2:ℚ)^(2+8*430+430*k) := by rw [pow_add, pow_add, pow_mul (2:ℚ) 8 430]; rfl

/-- `tail+1` is the first level above the upper band. Its preceding all-minimum
    suffix is active, and each of its ordered labelled words gives a separate unit. -/
theorem firstLayer (h tail : ℕ) (hh : 512*430 ≤ h)
    (prev : ratio^tail ≤ ceiling h) (cross : ceiling h < ratio^(tail+1)) :
    (2:ℚ)^70 < ratio^tail ∧ ratio^tail ≤ ceiling h ∧ ceiling h < ratio^tail*ratio ∧
      (2:ℕ)^(8*h-30976) < Fintype.card (Fin tail → Fin 430 → Fin 444) := by
  have pos : (0:ℚ) < 4*134^430 := by positivity
  have step : 0 < ratio := by unfold ratio; positivity
  have square : ceiling h < ratio^tail*ratio := by simpa [pow_succ] using cross
  have launch : (2:ℚ)^70 * ratio < ceiling h := by
    apply (lt_div_iff₀ pos).2
    calc
      _ = (2:ℚ)^70 * (4*134^430 * ratio^1) := by rw [pow_one]; ring
      _ ≤ (2:ℚ)^70 * 2^(2+8*430+430*1) := by
        exact mul_le_mul_of_nonneg_left (depthBound 1) (by positivity)
      _ = (2:ℚ)^(70+(2+8*430+430*1)) := (pow_add _ _ _).symm
      _ < 2^h := pow_lt_pow_right₀ (by norm_num) (by omega)
  have hstep : (2:ℚ)^70 < ratio^tail := by
    by_contra! bad
    exact (not_lt_of_ge (mul_le_mul_of_nonneg_right bad step.le)) (launch.trans square)
  have exponent : h < 2+8*430+430*(tail+1) := by
    apply (pow_lt_pow_iff_right₀ (a := (2:ℚ)) (by norm_num)).1
    calc
      _ < ratio^(tail+1) * (4*134^430) := (div_lt_iff₀ pos).1 cross
      _ = 4*134^430 * ratio^(tail+1) := mul_comm _ _
      _ ≤ _ := depthBound (tail+1)
  refine ⟨hstep, prev, square, ?_⟩
  calc
    _ < (2:ℕ)^(8*(430*tail)) := Nat.pow_lt_pow_right (by decide) (by omega)
    _ = (256:ℕ)^(430*tail) := by rw [pow_mul]; rfl
    _ ≤ 444^(430*tail) := Nat.pow_le_pow_left (by decide) _
    _ = Fintype.card (Fin tail → Fin 430 → Fin 444) := by simp [pow_mul]

#print axioms depthBound
#print axioms firstLayer

end CountedEpoch
