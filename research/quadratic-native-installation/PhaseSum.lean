import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic

namespace NativePhase

def sign (b : Bool) : ℂ := if b then -1 else 1

def quarter (neg : Bool) : ℂ := if neg then -Complex.I else Complex.I

theorem odd_square (neg : Bool) : quarter neg * quarter neg = -1 := by
  cases neg <;> simp [quarter]

theorem odd_column (neg b : Bool) :
    1 + quarter neg * sign b = (1+quarter neg) * (if b then -quarter neg else 1) := by
  cases b
  · simp [sign]
  · simp only [sign, ite_true, mul_neg, mul_one, add_mul, one_mul, odd_square]
    ring

/-- Sum out an odd linear term in an arbitrary finite quadratic path sum. -/
theorem eliminate_odd {α : Type*} (s : Finset α) (w : α → ℂ) (l : α → Bool) (neg : Bool) :
    ∑ a ∈ s, (w a + w a * quarter neg * sign (l a))
      = (1+quarter neg) * ∑ a ∈ s, w a * (if l a then -quarter neg else 1) := by
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro a _
  calc
    _ = w a * (1 + quarter neg * sign (l a)) := by ring
    _ = _ := by rw [odd_column]; ring

theorem pair_selector (a b : ℂ) (condition : Bool) :
    a + b + a * sign condition + b * sign (!condition)
      = 2 * (if condition then b else a) := by
  cases condition <;> simp [sign] <;> ring

/-- Sum out a coupled pair of binary variables and keep the surviving affine fibre. -/
theorem eliminate_pair {α : Type*} (s : Finset α) (w : α → Bool → ℂ) (l : α → Bool) :
    ∑ a ∈ s, (w a false + w a true + w a false * sign (l a) + w a true * sign (!(l a)))
      = 2 * ∑ a ∈ s, w a (l a) := by
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro a _
  rw [pair_selector]
  cases l a <;> rfl

/-- One branch choice gives the two exact coefficients of either numerical C gate. -/
theorem native_gate_entry (neg : Bool) (identity shifted : ℂ) :
    (1+quarter neg)/2 * (identity - quarter neg * shifted)
      = ((1+quarter neg)*identity + (1-quarter neg)*shifted)/2 := by
  have hh := odd_square neg
  linear_combination -shifted/2 * hh

#print axioms eliminate_odd
#print axioms eliminate_pair
#print axioms native_gate_entry
end NativePhase
