import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity

/-! A scaled logarithm bounds the leaf price at every intermediate rank.
The primitive at ranks below the ambient window uses its original price. -/
namespace ShiftedCarrier
open Finset
open scoped BigOperators

noncomputable def bitsLog (x : ℝ) : ℝ := Real.log x / Real.log 2
noncomputable def height (b x : ℝ) : ℝ := 1 + bitsLog x / b

theorem height_one_le {b x : ℝ} (hb : 0 < b) (hx : 1 ≤ x) : 1 ≤ height b x := by
  have h := div_nonneg (Real.log_nonneg hx) (Real.log_pos (by norm_num : (1:ℝ)<2)).le
  unfold height bitsLog
  linarith [div_nonneg h hb.le]

theorem base_height {b x C U : ℝ} {p : ℕ} (hb : 0 < b) (hx : 1 ≤ x)
    (hc : 0 ≤ C) (hu : bitsLog x ≤ U) (budget : C*(b+U) ≤ p) :
    x ≤ x^(1-C) * (height b x)^p := by
  let u := bitsLog x
  have hu₀ : 0 ≤ u := div_nonneg (Real.log_nonneg hx) (Real.log_pos (by norm_num : (1:ℝ)<2)).le
  have hx₀ : 0 < x := by linarith
  have hl₂ : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have hl₁ : Real.log 2 ≤ 1 := by linarith [Real.log_le_sub_one_of_pos (by norm_num : (0:ℝ)<2)]
  have hu' : Real.log x ≤ u := by
    have h : Real.log x = u*Real.log 2 := by dsimp [u,bitsLog]; field_simp
    rw [h]
    simpa only [mul_one] using mul_le_mul_of_nonneg_left hl₁ hu₀
  have hp : C*(b+u) ≤ p := (mul_le_mul_of_nonneg_left (show b+u ≤ b+U by dsimp [u]; linarith) hc).trans budget
  have hbu : 0 < b+u := by positivity
  have hh₀ : 0 < height b x := lt_of_lt_of_le zero_lt_one (height_one_le hb hx)
  have hh : u/(b+u) ≤ Real.log (height b x) := by
    have eqn : 1-(height b x)⁻¹ = u/(b+u) := by
      change 1-(1+u/b)⁻¹ = _
      field_simp
      ring
    rw [← eqn]
    exact Real.one_sub_inv_le_log_of_pos hh₀
  have hbnd : Real.log x*C ≤ (p : ℝ)*Real.log (height b x) := by
    calc
      Real.log x*C ≤ u*C := mul_le_mul_of_nonneg_right hu' hc
      _ ≤ (p:ℝ)*(u/(b+u)) := by
        rw [← mul_div_assoc,le_div_iff₀ hbu]
        nlinarith [mul_le_mul_of_nonneg_left hp hu₀]
      _ ≤ _ := mul_le_mul_of_nonneg_left hh (Nat.cast_nonneg _)
  have hpow : x^C ≤ (height b x)^p := by
    rw [Real.rpow_def_of_pos hx₀]
    apply (Real.exp_le_exp.mpr hbnd).trans_eq
    rw [← Real.log_pow, Real.exp_log (pow_pos hh₀ p)]
  have hxx : x = x^(1-C)*x^C := by rw [← Real.rpow_add hx₀]; simp
  calc
    x = x^(1-C)*x^C := hxx
    _ ≤ _ := mul_le_mul_of_nonneg_left hpow (Real.rpow_nonneg hx₀.le _)

theorem exit_height {b x e a r θ : ℝ} (hb : 0 < b) (hx : 0<x) (he : 0<e) (ha : 0<a) (hr : 0<r)
    (bound : e ≤ r*(x/a)^θ)
    (shift : (1-θ)*b ≤ θ*bitsLog a - bitsLog r) : height b e ≤ θ*height b x := by
  have h := Real.log_le_log he bound
  rw [Real.log_mul hr.ne' (Real.rpow_pos_of_pos (div_pos hx ha) θ).ne',Real.log_rpow (div_pos hx ha),
    Real.log_div hx.ne' ha.ne'] at h
  have hl : 0 < Real.log 2 := Real.log_pos (by norm_num)
  unfold height bitsLog at *
  field_simp at shift ⊢
  nlinarith

/-- One original input port serves k physical rounds. This comparison retains
its exact multiplicity. The largest allowed port count is represented by x. -/
theorem paid_port {x s k a C : ℝ} (hx : 0<x) (hs : 0<s) (hk : 0<k) (ha : 0<a)
    (hc : 0 ≤ C) (source : x ≤ a*s) (rounds : k*s ≤ 2*x) :
    s^(1-C) ≤ (2*a^C*x^(1-C)) / k := by
  have hr : x^C ≤ a^C*s^C := by
    simpa only [Real.mul_rpow ha.le hs.le] using Real.rpow_le_rpow hx.le source hc
  rw [Real.rpow_sub hs, Real.rpow_one, Real.rpow_sub hx, Real.rpow_one,le_div_iff₀ hk]
  have hsc := Real.rpow_pos_of_pos hs C
  have hxc := Real.rpow_pos_of_pos hx C
  field_simp
  nlinarith [mul_le_mul_of_nonneg_right rounds hxc.le, mul_le_mul_of_nonneg_left hr hx.le]

/-- The exit list and its nonnegative weights are the normalized, paid
recursive calls. Local single-axis remainders cost at most three calls. -/
theorem uniform_price {L : ℕ → ℝ} {X p : ℕ} {C b θ K U : ℝ} (hb : 0<b) (hc : 0≤C)
    (hθ : 0≤θ) (budget : C*(b+U) ≤ p) (absorb : K*θ^p ≤ (3:ℝ)/4)
    (base : ∀ n : ℕ, 0<n → n<X → L n ≤ n ∧ bitsLog n ≤ U)
    (large : ∀ n : ℕ, X ≤ n → 12 ≤ (n:ℝ)^(1-C))
    (flow : ∀ n : ℕ, X ≤ n → ∃ (kids : Finset ℕ) (weight : ℕ→ℝ),
      (∀ i ∈ kids, 0 < i ∧ i < n ∧ 0 ≤ weight i ∧ height b i ≤ θ*height b n) ∧
      (∑ i ∈ kids, weight i*(i:ℝ)^(1-C)) ≤ K*(n:ℝ)^(1-C) ∧
      L n ≤ 3 + ∑ i ∈ kids, weight i*L i)
    (n : ℕ) (hn : 0<n) : L n ≤ (n:ℝ)^(1-C)*(height b n)^p := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    by_cases hsmall : n<X
    · have h := base n hn hsmall
      exact h.1.trans (base_height hb (by exact_mod_cast hn) hc h.2 budget)
    have hg : X ≤ n := by omega
    obtain ⟨kids,w,hw,hm,hcost⟩ := flow n hg
    have hN : (1:ℝ) ≤ n := by exact_mod_cast hn
    have hheight := height_one_le hb hN
    have hz : 0≤(n:ℝ)^(1-C) := Real.rpow_nonneg (Nat.cast_nonneg _) _
    have hf : 0 ≤ (θ*height b n)^p := pow_nonneg (mul_nonneg hθ (by linarith)) _
    have ht : (∑ i ∈ kids, w i*L i) ≤ (K*(n:ℝ)^(1-C)) * (θ*height b n)^p := by
      calc
        _ ≤ ∑ i ∈ kids, (w i*(i:ℝ)^(1-C))*(θ*height b n)^p := by
          apply Finset.sum_le_sum
          intro i hi
          obtain ⟨hip,hin,hwp,he⟩ := hw i hi
          have h₁ := ih i hin hip
          have hhp := height_one_le hb (show (1:ℝ) ≤ i by exact_mod_cast hip)
          have h₂ := pow_le_pow_left₀ (show 0≤height b i by linarith) he p
          rw [mul_assoc]
          exact mul_le_mul_of_nonneg_left (h₁.trans (mul_le_mul_of_nonneg_left h₂
            (Real.rpow_nonneg (Nat.cast_nonneg _) _))) hwp
        _ = (∑ i ∈ kids, w i*(i:ℝ)^(1-C))*(θ*height b n)^p := (Finset.sum_mul _ _ _).symm
        _ ≤ _ := mul_le_mul_of_nonneg_right hm hf
    have one : (1:ℝ) ≤ (height b n)^p := one_le_pow₀ hheight
    have h12 : 12 ≤ (n:ℝ)^(1-C)*(height b n)^p := (large n hg).trans (le_mul_of_one_le_right hz one)
    have hK' := mul_le_mul_of_nonneg_right absorb (mul_nonneg hz (by positivity : 0≤(height b n)^p))
    rw [mul_pow] at ht
    nlinarith

#print axioms base_height
#print axioms exit_height
#print axioms paid_port
#print axioms uniform_price
end ShiftedCarrier
