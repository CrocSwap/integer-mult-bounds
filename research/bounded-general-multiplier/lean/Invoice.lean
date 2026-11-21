import ShiftedCarrier
import CarrierGuards

/-! Connect physical occurrence counts to the recursive leaf-price induction. -/
namespace ShiftedCarrier
open Finset
open scoped BigOperators

theorem port_sum {I : Type*} (F : Finset I) (s k : I → ℝ) {x A C : ℝ}
    (hx : 0<x) (ha : 0<A) (hc : 0≤C)
    (hs : ∀ i ∈ F, 0 < s i ∧ 0 < k i ∧ x ≤ A*s i ∧ k i*s i ≤ 2*x) :
    (∑ i ∈ F, (s i)^(1-C)) ≤ (2*A^C*x^(1-C))*(∑ i ∈ F, 1/k i) := by
  rw [Finset.mul_sum]
  apply Finset.sum_le_sum
  intro i hi
  obtain ⟨h₁,h₂,h₃,h₄⟩ := hs i hi
  simpa only [one_div,div_eq_mul_inv,one_mul] using paid_port hx h₁ h₂ ha hc h₃ h₄

/-- Multiply the full paid census by the number of actual schedules. Divide
by exactly the surviving independent owners. Empty source/exit slots cost zero. -/
theorem normalized_invoice {I J : Type*} (src : Finset I) (ex : Finset J) (s k : I→ℝ) (r mult : J→ℝ)
    {x A C lanes keep : ℝ} (hx : 0<x) (ha : 0<A) (hc : 0≤C) (hl : 0≤lanes) (hk : 0<keep)
    (hs : ∀ i ∈ src, 0 < s i ∧ 0 < k i ∧ x ≤ A*s i ∧ k i*s i ≤ 2*x)
    (priced : (∑ i ∈ ex, mult i*(r i)^(1-C)) ≤ ∑ i ∈ src, (s i)^(1-C))
    (rounding : lanes*(∑ i ∈ src, 1/k i) ≤ (16/15:ℝ)*keep) :
    (∑ i ∈ ex, (lanes*mult i/keep)*(r i)^(1-C)) ≤ ((16/15:ℝ)*2*A^C)*x^(1-C) := by
  have hh := priced.trans (port_sum src s k hx ha hc hs)
  have ha' := Real.rpow_pos_of_pos ha C
  have hx' := Real.rpow_pos_of_pos hx (1-C)
  calc
    _ = (lanes*(∑ i ∈ ex, mult i*(r i)^(1-C)))/keep := by
      simp only [div_eq_mul_inv,Finset.mul_sum,Finset.sum_mul]
      exact Finset.sum_congr rfl fun _ _ ↦ by ring
    _ ≤ (lanes*((2*A^C*x^(1-C))*(∑ i ∈ src, 1/k i)))/keep :=
      div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_left hh hl) hk.le
    _ ≤ _ := by
      rw [div_le_iff₀ hk]
      nlinarith [mul_le_mul_of_nonneg_left rounding (by positivity : 0≤2*A^C*x^(1-C))]

theorem bitsLog_pow_two (H : ℕ) : bitsLog ((2:ℝ)^H) = (H:ℝ) := by
  rw [bitsLog,Real.log_pow,mul_div_cancel_right₀]
  exact (Real.log_pos (by norm_num : (1:ℝ)<2)).ne'

/-- Terminal funding uses the literal integer guard. The conclusion is strict
after multiplying the paid-leaf invoice by the specified reserve. -/
theorem terminal {L C target : ℝ} {H b p overhead q : ℕ} (hb : 0<b)
    (bound : L ≤ ((2:ℝ)^H)^(1-C)*(height b ((2:ℝ)^H))^p)
    (fund : (H+b)^p*2^overhead < b^p*2^q)
    (room : (q:ℝ) ≤ H*(C-target)) :
    L*2^overhead < ((2:ℝ)^H)^(1-target) := by
  have rb : (0:ℝ)<b := by exact_mod_cast hb
  have hb' : 0<(b:ℝ)^p := pow_pos rb _
  have e : height b ((2:ℝ)^H) = ((H:ℝ)+b)/b := by
    rw [height,bitsLog_pow_two]
    field_simp
    ring
  have hp' : (height b ((2:ℝ)^H))^p*2^overhead < (2:ℝ)^q := by
    rw [e,div_pow,div_mul_eq_mul_div,div_lt_iff₀ hb']
    have hc : ((H:ℝ)+b)^p*2^overhead < (b:ℝ)^p*2^q := by exact_mod_cast fund
    linarith
  have hpow : (2:ℝ)^q ≤ ((2:ℝ)^H)^(C-target) := by
    rw [← Real.rpow_natCast 2 q,← Real.rpow_natCast 2 H,←Real.rpow_mul (by norm_num : (0:ℝ)≤2)]
    exact Real.rpow_le_rpow_of_exponent_le (by norm_num) room
  have hpos : 0 < ((2:ℝ)^H)^(1-C) := by positivity
  calc
    L*2^overhead ≤ (((2:ℝ)^H)^(1-C)*(height b ((2:ℝ)^H))^p)*2^overhead :=
      mul_le_mul_of_nonneg_right bound (by positivity)
    _ < ((2:ℝ)^H)^(1-C)*((2:ℝ)^H)^(C-target) := by
      rw [mul_assoc]
      exact mul_lt_mul_of_pos_left (hp'.trans_le hpow) hpos
    _ = _ := by rw [← Real.rpow_add (by positivity : 0<(2:ℝ)^H)]; ring_nf

#print axioms normalized_invoice
#print axioms terminal
end ShiftedCarrier
