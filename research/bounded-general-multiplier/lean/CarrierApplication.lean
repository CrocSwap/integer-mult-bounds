import GuardInterpretation
import AppliedInvoice

namespace ShiftedCarrier
open CarrierGuards Finset
open scoped BigOperators

/-- Project one emitted periodic job to its funded occurrence counts.
The source field and every paid exit keep their own multiplicities. -/
structure PeriodBill (v : Bound) (C : ℝ) (L : ℕ→ℝ) (n : ℕ) where
  source : Finset ℕ
  exits : Finset ℕ
  size : ℕ→ℝ
  period : ℕ→ℝ
  count : ℕ→ℝ
  active : ℝ
  lanes : ℝ
  keep : ℝ
  active_pos : 0<active
  active_le : active≤n
  lanes_nonneg : 0≤lanes
  keep_pos : 0<keep
  ownership : ∀ i ∈ source, 0<size i ∧ 0<period i ∧
    active≤(threshold v:ℝ)*size i ∧ period i*size i≤2*active
  cancellation : (∑ e ∈ exits, count e*(e:ℝ)^(1-C)) ≤ ∑ i ∈ source, (size i)^(1-C)
  padding : lanes*(∑ i ∈ source, 1/period i)≤(16/15:ℝ)*keep
  child : ∀ e ∈ exits, 0<e ∧ e<n ∧ 0≤count e ∧
    (e:ℝ)≤v.ceiling*((n:ℝ)/threshold v)^(ratio v)
  full_cost : L n ≤ 3+∑ e ∈ exits, (lanes*count e/keep)*L e

/-- Use each period bill, the unchanged primitive and the integer guards to
bound the normalized price at all positive ranks. -/
theorem all_ranks {v : Bound} {C : ℝ} {a d : ℕ} {L : ℕ→ℝ}
    (guard : valid v a d) (hd : 0<d) (hX : 256 ≤ threshold v)
    (hr : 0<v.ceiling) (hb : 0<v.shift) (hC : 0≤C) (ht : C≤1/2)
    (cap : C≤(a:ℝ)/d)
    (base : ∀ n : ℕ, 0<n → n < threshold v → L n ≤ n)
    (bills : ∀ n : ℕ, threshold v ≤ n → PeriodBill v C L n)
    (n : ℕ) (hn : 0<n) : L n ≤ (n:ℝ)^(1-C)*(height v.shift n)^v.logPower := by
  have hden := guard.1.trans guard.2.1
  have hden' : (0:ℝ)<v.den := by exact_mod_cast hden
  have hθ : 0≤ratio v := div_nonneg (Nat.cast_nonneg _) hden'.le
  have ga := real_guards guard hd (by omega) hr cap
  have bx : (0:ℝ)<threshold v := by exact_mod_cast (show 0<threshold v by omega)
  have br : (0:ℝ)<v.ceiling := by exact_mod_cast hr
  have bb : (0:ℝ)<v.shift := by exact_mod_cast hb
  apply uniform_price (X:=threshold v) (θ:=ratio v) bb hC hθ ga.base_price ga.exit_price _ _ _ n hn
  · intro j hj hj'
    refine ⟨base j hj hj',?_⟩
    have h : (j:ℝ)≤ threshold v := by exact_mod_cast hj'.le
    have jpos : (0:ℝ)<j := by exact_mod_cast hj
    exact (div_le_div_of_nonneg_right (Real.log_le_log jpos h)
      (Real.log_nonneg (by norm_num : (1:ℝ)≤2))).trans ga.log_ceiling
  · intro j hj
    have h : 256 ≤ j := hX.trans hj
    have jcast : (256:ℝ)≤j := by exact_mod_cast h
    have root : (256:ℝ)^((1:ℝ)/2) = 16 := by
      rw [←Real.sqrt_eq_rpow]
      exact (Real.sqrt_eq_iff_mul_self_eq (by norm_num) (by norm_num)).mpr (by norm_num)
    calc
      (12:ℝ) ≤ (256:ℝ)^((1:ℝ)/2) := by rw [root]; norm_num
      _ ≤ (j:ℝ)^((1:ℝ)/2) := Real.rpow_le_rpow (by norm_num) jcast (by norm_num)
      _ ≤ _ := Real.rpow_le_rpow_of_exponent_le (by linarith) (by linarith)
  · intro j hj
    let q := bills j hj
    have jpos : (0:ℝ)<j := by exact_mod_cast (show 0<j by omega)
    let weight := fun e ↦ q.lanes*q.count e/q.keep
    refine ⟨q.exits,weight,?_,?_,q.full_cost⟩
    · intro e he
      obtain ⟨he',less,paid,bound⟩ := q.child e he
      refine ⟨he',less,div_nonneg (mul_nonneg q.lanes_nonneg paid) q.keep_pos.le,?_⟩
      exact exit_height bb jpos (by exact_mod_cast he') bx br bound ga.shrink
    · have h := normalized_invoice q.source q.exits q.size q.period (fun e : ℕ ↦ (e:ℝ)) q.count
        q.active_pos bx hC q.lanes_nonneg q.keep_pos q.ownership q.cancellation q.padding
      have hp := Real.rpow_le_rpow q.active_pos.le q.active_le (show 0≤1-C by linarith)
      exact h.trans (mul_le_mul_of_nonneg_left hp (by positivity))

/-- Combine all-rank funding and the literal terminal margin for the binary
word. The input assumptions are its unnormalized finite receipts. -/
theorem bit_program {L : ℕ→ℝ}
    (base : ∀ n : ℕ, 0<n → n < threshold bit → L n ≤ n)
    (bills : ∀ n : ℕ, threshold bit ≤ n → PeriodBill bit 0.003879928046148 L n) :
    L (2^bitH)*32 < ((2:ℝ)^bitH)^((1:ℝ)-0.003879928035648) := by
  apply bit_terminal
  have h := all_ranks bit_guard (by decide) (by decide +kernel) (by decide +kernel)
    (by decide) (by norm_num : (0:ℝ)≤0.003879928046148) (by norm_num)
    (by norm_num) base bills (2^bitH) (pow_pos (by decide) _)
  simpa only [show bit.shift=8192 by rfl, show bit.logPower=71 by rfl,
    Nat.cast_pow,Nat.cast_ofNat] using h

/-- The rational word is funded at the full outer target and reserve. -/
theorem complex_program {L : ℕ→ℝ}
    (base : ∀ n : ℕ, 0<n → n < threshold complex → L n ≤ n)
    (bills : ∀ n : ℕ, threshold complex ≤ n → PeriodBill complex 0.00388013 L n) :
    L (2^complexH)*2 < ((2:ℝ)^complexH)^((1:ℝ)-(0.00387992803556+5/100000000000000)) := by
  apply complex_terminal
  have h := all_ranks complex_guard (by decide) (by decide +kernel) (by decide +kernel)
    (by decide) (by norm_num : (0:ℝ)≤0.00388013) (by norm_num)
    (by norm_num) base bills (2^complexH) (pow_pos (by decide) _)
  simpa only [show complex.shift=2048 by rfl, show complex.logPower=31 by rfl,
    Nat.cast_pow,Nat.cast_ofNat] using h

#print axioms all_ranks
#print axioms bit_program
#print axioms complex_program
end ShiftedCarrier
