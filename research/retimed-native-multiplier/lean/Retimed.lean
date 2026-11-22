import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

namespace Retimed

open scoped BigOperators

noncomputable def columns (x : ℝ) : ℕ := 2 * ⌊x/2⌋₊ - 8

theorem column_interval {x : ℝ} (hx : 10 ≤ x) :
    x - 10 < (columns x : ℝ) ∧ (columns x : ℝ) ≤ x - 8 := by
  have h₁ := Nat.floor_le (show 0 ≤ x/2 by linarith)
  have h₂ := Nat.lt_floor_add_one (x/2)
  have hf : 4 ≤ ⌊x/2⌋₊ := Nat.le_floor (by linarith : (4 : ℝ) ≤ x/2)
  have h : 8 ≤ 2 * ⌊x/2⌋₊ := by omega
  simp only [columns, Nat.cast_sub h, Nat.cast_mul, Nat.cast_ofNat]
  constructor <;> linarith

theorem paid_fringe {x y r k : ℝ} (hx : 10 ≤ x) (hy : 10 ≤ y) (hr : 0 < r)
    (hk : 5*r ≤ 4*k) (match_size : r*x=k*y) :
    0 ≤ r * (columns x : ℝ) - k * (columns y : ℝ) ∧
    r * (columns x : ℝ) - k * (columns y : ℝ) < 10*k := by
  have hk' : 0 < k := by linarith
  obtain ⟨xa, xb⟩ := column_interval hx
  obtain ⟨ya, yb⟩ := column_interval hy
  constructor
  · nlinarith [mul_lt_mul_of_pos_left xa hr, mul_le_mul_of_nonneg_left yb hk'.le]
  · nlinarith [mul_le_mul_of_nonneg_left xb hr.le, mul_lt_mul_of_pos_left ya hk']

noncomputable def mass (t x y : ℝ) : ℝ := (x^(-t)- y^(-t))/t

theorem dilate_mass {t x y r k : ℝ} (hx : 0 < x) (hy : 0 < y)
    (hr : 0 < r) (hk : 0 < k) :
    mass t (x*(k/r)) (y*(k/r)) = (r^t/k^t) * mass t x y := by
  have ha : 0 < k/r := div_pos hk hr
  simp only [mass, Real.mul_rpow hx.le ha.le, Real.mul_rpow hy.le ha.le,
    Real.div_rpow hk.le hr.le, Real.rpow_neg hk.le, Real.rpow_neg hr.le]
  have hp := (Real.rpow_pos_of_pos hr t).ne'
  have hq := (Real.rpow_pos_of_pos hk t).ne'
  by_cases ht : t=0
  · simp [ht]
  · field_simp

theorem offered_capacity {ι : Type} (s : Finset ι) {t x y k : ℝ} (r p : ι → ℝ)
    (hx : 0 < x) (hy : 0 < y) (hk : 0 < k) (hr : ∀ j ∈ s, 0 < r j)
    (cap : ∑ j ∈ s, p j * r j ^ t ≤ k ^ t) (ht : 0 < t) (hxy : x ≤ y) :
    ∑ j ∈ s, p j * mass t (x*(k/r j)) (y*(k/r j)) ≤ mass t x y := by
  have h : ∑ j ∈ s, p j * mass t (x*(k/r j)) (y*(k/r j)) =
      (∑ j ∈ s, p j * (r j)^t) * (mass t x y / k^t) := by
    rw [Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro j hj
    rw [dilate_mass hx hy (hr j hj) hk]
    ring
  rw [h]
  have hp := Real.rpow_pos_of_pos hk t
  have m : 0 ≤ mass t x y := div_nonneg (sub_nonneg.mpr
      (Real.rpow_le_rpow_of_nonpos hx hxy (neg_nonpos.mpr ht.le))) ht.le
  calc
    _ ≤ k^t * (mass t x y / k^t) := mul_le_mul_of_nonneg_right cap (div_nonneg m hp.le)
    _ = mass t x y := by field_simp

theorem equal_end_mass {L U r k : ℝ} (hL : 0 < L) (hU : 0 < U)
    (hr : 0 < r) (hk : 0 < k) :
    Real.log (L*(k/r)) - Real.log L = Real.log (U*(k/r)) - Real.log U := by
  have h := (div_pos hk hr).ne'
  rw [Real.log_mul hL.ne' h, Real.log_mul hU.ne' h]
  ring

theorem timely_return (birth j child parent slots : ℕ) (h : slots * child ≤ parent) :
    birth+j*parent+slots*child ≤ birth+(j+1)*parent := by
  rw [Nat.add_mul]
  simp
  omega

theorem complete_copy_tariff (B h : ℕ) (hB : 4096*h ≤ B) :
    4096 * (((B+h-1)/h)*h) ≤ 4097*B := by
  have a := Nat.div_mul_le_self (B+h-1) h
  omega

#print axioms column_interval
#print axioms paid_fringe
#print axioms dilate_mass
#print axioms offered_capacity
#print axioms equal_end_mass
#print axioms timely_return
#print axioms complete_copy_tariff

end Retimed
