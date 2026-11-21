import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Linarith
import Mathlib.Algebra.GroupWithZero.Units.Basic

namespace QuotientLimbScale

/-- The four executed additions multiply the two old limbs by inverse units. -/
theorem paired_shears {R : Type*} [CommRing R] (c ci h l : R)
    (hc : c * ci = 1) :
    let l₁ := l - c*h
    let h₂ := h + (ci-1)*l₁
    let l₃ := l₁ + h₂
    let h₄ := h₂ + (c-1)*l₃
    (h₄, l₃) = (c*h, ci*l) := by
  dsimp
  have h₂ : h + (ci-1)*(l-c*h) = c*h+(ci-1)*l := by
    linear_combination -h*hc
  rw [h₂]
  have h₃ : l-c*h+(c*h+(ci-1)*l) = ci*l := by ring
  rw [h₃]
  congr 1
  linear_combination l*hc

/-- Recover the high and low output with the single carry from the old low. -/
theorem recombine (a h l B C : ℕ) (hB : 0 < B) (hC : 0 < C) :
    a*(B*h+l) % (B*C) = B*((a*h+a*l/B)%C) + a*l%B := by
  set K := a*h+a*l/B
  set t := a*l%B
  have split : a*(B*h+l) = B*K+t := by
    calc
      a*(B*h+l) = B*(a*h) + a*l := by ring
      _ = B*(a*h) + (a*l%B + B*(a*l/B)) := by rw [Nat.mod_add_div]
      _ = B*K+t := by dsimp [K,t]; ring
  have carry : B*K+t = (B*(K%C)+t) + (B*C)*(K/C) := by
    calc
      B*K+t = B*(K%C+C*(K/C))+t := by rw [Nat.mod_add_div]
      _ = _ := by ring
  have small : B*(K%C)+t < B*C := by
    calc
      B*(K%C)+t < B*(K%C)+B := Nat.add_lt_add_left (Nat.mod_lt _ hB) _
      _ = B*(K%C+1) := by ring
      _ ≤ B*C := Nat.mul_le_mul_left _ (Nat.succ_le_of_lt (Nat.mod_lt _ hC))
  rw [split, carry, Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt small]

#print axioms paired_shears
#print axioms recombine

end QuotientLimbScale
