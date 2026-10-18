import SelectedMomentUpperAggregate
import Mathlib.Data.Complex.Exponential

/-!
Source-specific Real exponential enclosure for the accepted twelve-step
rational expression in PR531's pinned base_two_moment.py.
The finite rational checkpoint sources are imported unchanged. The analytic
bound reuses Real.exp_bound' at n=15 and a short geometric-tail comparison;
no new infinite-series theorem or arithmetic oracle is introduced.

Conditional source context: kappa = 1517760977820331/1000000000000000000
= 0.001517760977820331. This source supplies only the exponential part of the
moment enclosure. Logarithm/rounding transport, operator/profile realization,
all-size transfer and the multiplier theorem remain separate.
Attribution: inherited PR361 base-two engine through PR531; Mathlib's existing
exponential bound. Prepared with OpenAI assistance.
-/
namespace CurrentMain.SelectedMomentExpEnclosure

open scoped BigOperators
open Finset
set_option Elab.async false

/-- Finite cast/algebra correspondence, not a reevaluation of checkpoint literals. -/
private theorem cast_state12 (x : Rat) :
    ((SelectedMomentUpperAggregate.expState12 x).1 : ℝ) = (x : ℝ)^12 / (12 : Nat).factorial ∧
    ((SelectedMomentUpperAggregate.expState12 x).2 : ℝ) =
      ∑ j ∈ range 13, (x : ℝ)^j / (j.factorial : ℝ) := by
  constructor <;>
    norm_num [SelectedMomentUpperAggregate.expState12, SelectedMomentUpperAggregate.expBlock, SelectedMomentUpperAggregate.expStep, Rat.cast_add,
      Rat.cast_mul, Rat.cast_div, Finset.sum_range_succ, Nat.factorial] <;> ring

/-- The library n=15 remainder fits the source degree12 geometric tail. -/
private theorem tail_comparison (x : ℝ) (hx : 0 ≤ x) (h1 : x < 1) :
    x^13 / (13 : Nat).factorial + x^14 / (14 : Nat).factorial +
      x^15 * 16 / ((15 : Nat).factorial * 15) ≤
    (x^12 / (12 : Nat).factorial) * x / 13 / (1 - x/14) := by
  have hd : 0 < 1 - x/14 := by linarith
  have ht : 0 ≤ x^13 / (13 : Nat).factorial := by positivity
  have hcoef : (16 : ℝ)/(14*15^2) ≤ 1/14^2 := by norm_num
  have hrem : (16 : ℝ)/(14*15^2) ≤ 1/(14^2*(1-x/14)) := by
    refine hcoef.trans ?_
    apply (div_le_div_iff₀ (by norm_num : (0 : ℝ) < 14^2)
      (mul_pos (by norm_num : (0 : ℝ) < 14^2) hd)).2
    nlinarith
  have hm := mul_le_mul_of_nonneg_left hrem (mul_nonneg ht (sq_nonneg x))
  calc
    x^13 / (13 : Nat).factorial + x^14 / (14 : Nat).factorial +
        x^15 * 16 / ((15 : Nat).factorial * 15) =
        x^13 / (13 : Nat).factorial +
          (x^13 / (13 : Nat).factorial)*x/14 +
          ((x^13 / (13 : Nat).factorial)*x^2)*(16/(14*15^2)) := by
      norm_num [Nat.factorial] <;> ring
    _ ≤ x^13 / (13 : Nat).factorial +
          (x^13 / (13 : Nat).factorial)*x/14 +
          ((x^13 / (13 : Nat).factorial)*x^2)*(1/(14^2*(1-x/14))) :=
      add_le_add_left hm _
    _ = (x^12 / (12 : Nat).factorial)*x/13/(1-x/14) := by
      have hg (t : ℝ) :
          t + t*(x/14) + t*(x/14)^2/(1-x/14) = t/(1-x/14) := by
        apply (eq_div_iff (ne_of_gt hd)).2
        rw [add_mul, add_mul, div_mul_cancel₀ _ (ne_of_gt hd)]
        ring
      calc
        _ = x^13 / (13 : Nat).factorial +
            (x^13 / (13 : Nat).factorial)*(x/14) +
            (x^13 / (13 : Nat).factorial)*(x/14)^2/(1-x/14) := by
          simp only [one_div, mul_inv_rev]
          ring
        _ = (x^13 / (13 : Nat).factorial)/(1-x/14) := hg _
        _ = (x^12 / (12 : Nat).factorial)*x/13/(1-x/14) := by
          norm_num [Nat.factorial] <;> ring

private theorem real_expression_enclosure (x : ℝ) (hx : 0 ≤ x) (h1 : x < 1) :
    Real.exp x ≤ (∑ j ∈ range 13, x^j / (j.factorial : ℝ)) +
      (x^12 / (12 : Nat).factorial)*x/13/(1-x/14) := by
  have hb := Real.exp_bound' hx h1.le (n := 15) (by decide)
  have hs : (∑ j ∈ range 15, x^j / (j.factorial : ℝ)) =
      (∑ j ∈ range 13, x^j / (j.factorial : ℝ)) +
        x^13/(13 : Nat).factorial + x^14/(14 : Nat).factorial := by
    rw [Finset.sum_range_succ, Finset.sum_range_succ]
  rw [hs] at hb
  have ht := tail_comparison x hx h1
  norm_num only at hb
  linarith

/-- Exact source-domain exponential enclosure for the accepted rational expression. -/
theorem expUpper_real_enclosure (x : Rat) (hx : 0 ≤ x) (h1 : x < 1) :
    Real.exp (x : ℝ) ≤ (SelectedMomentUpperAggregate.expUpper x : ℝ) := by
  have hxR : (0 : ℝ) ≤ (x : ℝ) := by exact_mod_cast hx
  have h1R : (x : ℝ) < 1 := by exact_mod_cast h1
  have hs := cast_state12 x
  have hu : (SelectedMomentUpperAggregate.expUpper x : ℝ) =
      (∑ j ∈ range 13, (x : ℝ)^j / (j.factorial : ℝ)) +
        ((x : ℝ)^12/(12 : Nat).factorial)*(x : ℝ)/13/(1-(x : ℝ)/14) := by
    norm_num [SelectedMomentUpperAggregate.expUpper, Rat.cast_add, Rat.cast_mul, Rat.cast_div,
      Rat.cast_sub, hs.1, hs.2]
  rw [hu]
  exact real_expression_enclosure (x : ℝ) hxR h1R

/-- Nine source arguments, with domain facts reused from the accepted finite root. -/
theorem selected_exp_enclosures :
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 6 9 137 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 6 9 137) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 5 9 137 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 5 9 137) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 4 25 121 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 4 25 121) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 4 9 137 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 4 9 137) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 3 33 113 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 3 33 113) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 3 25 121 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 3 25 121) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 3 17 129 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 3 17 129) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 1 9 137 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 1 9 137) : ℝ) ∧
    Real.exp ((SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 0 25 121 : Rat) : ℝ) ≤
      (SelectedMomentUpperAggregate.expUpper (SelectedMomentUpperAggregate.bMinus * SelectedMomentUpperAggregate.roundedLog 0 25 121) : ℝ) := by
  rcases SelectedMomentUpperAggregate.source_domains with
    ⟨_, _, _, _, _, _, _, _, _, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
  exact ⟨expUpper_real_enclosure _ h1.1 h1.2,
    expUpper_real_enclosure _ h2.1 h2.2, expUpper_real_enclosure _ h3.1 h3.2,
    expUpper_real_enclosure _ h4.1 h4.2, expUpper_real_enclosure _ h5.1 h5.2,
    expUpper_real_enclosure _ h6.1 h6.2, expUpper_real_enclosure _ h7.1 h7.2,
    expUpper_real_enclosure _ h8.1 h8.2, expUpper_real_enclosure _ h9.1 h9.2⟩

end CurrentMain.SelectedMomentExpEnclosure
#print axioms CurrentMain.SelectedMomentExpEnclosure.expUpper_real_enclosure
#print axioms CurrentMain.SelectedMomentExpEnclosure.selected_exp_enclosures
