/- Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
   Analytic rank-debt argument credited to Cinna Davis, PR4696.
   This module proves the generic finite-list inequality only. The native
   symmetric-form rank grammar and source-specific path facts are premises. -/
import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

namespace PhaseRankDebt

/-- Equal-length increments of a concave function decrease with the base.
    The two concavity applications avoid differentiation at zero. -/
theorem concave_increment_antitone {f : ℝ → ℝ}
    (hf : ConcaveOn ℝ (Set.Ici 0) f) {a b d : ℝ}
    (ha : 0 ≤ a) (hab : a ≤ b) (hd : 0 ≤ d) :
    f (b+d) - f b ≤ f (a+d) - f a := by
  by_cases hz : b+d-a = 0
  · have hb : b = a := by linarith
    have hd' : d = 0 := by linarith
    simp [hb, hd']
  have hpos : 0 < b+d-a := lt_of_le_of_ne (by linarith) (Ne.symm hz)
  have hα : 0 ≤ (b-a)/(b+d-a) := div_nonneg (by linarith) hpos.le
  have hβ : 0 ≤ d/(b+d-a) := div_nonneg hd hpos.le
  have hsum : (b-a)/(b+d-a) + d/(b+d-a) = 1 := by
    field_simp
    <;> ring
  have hm₁ : (b-a)/(b+d-a)*a + d/(b+d-a)*(b+d) = a+d := by
    field_simp
    <;> ring
  have hm₂ : d/(b+d-a)*a + (b-a)/(b+d-a)*(b+d) = b := by
    field_simp
    <;> ring
  have hc₁ := hf.2 ha (show b+d ∈ Set.Ici 0 by change 0 ≤ b+d; linarith) hα hβ hsum
  have hc₂ := hf.2 ha (show b+d ∈ Set.Ici 0 by change 0 ≤ b+d; linarith) hβ hα (by linarith [hsum])
  simp only [smul_eq_mul, hm₁] at hc₁
  simp only [smul_eq_mul, hm₂] at hc₂
  have ht : (b-a)/(b+d-a)*f a + d/(b+d-a)*f (b+d) +
      (d/(b+d-a)*f a + (b-a)/(b+d-a)*f (b+d)) = f a + f (b+d) := by
    calc
      _ = ((b-a)/(b+d-a) + d/(b+d-a)) * (f a + f (b+d)) := by ring
      _ = _ := by rw [hsum, one_mul]
  linarith [hc₁, hc₂, ht]

theorem rpow_increment_antitone {a b d t : ℝ}
    (ha : 0 ≤ a) (hab : a ≤ b) (hd : 0 ≤ d)
    (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    (b+d)^t - b^t ≤ (a+d)^t - a^t := by
  exact concave_increment_antitone (Real.concaveOn_rpow ht0 ht1) ha hab hd

def deltaSum (xs : List (ℝ × ℝ)) : ℝ := (xs.map Prod.snd).sum

noncomputable def paidDelta (t : ℝ) (xs : List (ℝ × ℝ)) : ℝ :=
  (xs.map (fun p => (p.1+p.2)^t - p.1^t)).sum

theorem deltaSum_nonneg (xs : List (ℝ × ℝ))
    (hx : ∀ p ∈ xs, 0 ≤ p.2) : 0 ≤ deltaSum xs := by
  induction xs with
  | nil => simp [deltaSum]
  | cons p xs ih =>
    have hp := hx p (by simp)
    have ht := ih (fun q hq => hx q (by simp [hq]))
    simpa [deltaSum] using add_nonneg hp ht

/-- A finite list of old block ranks r≤h and added ranks δ≥0 pays at least
    the concave moment of adding their total rank to h. No sum r=h is needed
    for this analytic inequality; that equality is a native-path premise. -/
theorem finite_list_debt {h t : ℝ} (hh : 0 ≤ h)
    (ht0 : 0 ≤ t) (ht1 : t ≤ 1) (xs : List (ℝ × ℝ))
    (hx : ∀ p ∈ xs, 0 ≤ p.1 ∧ p.1 ≤ h ∧ 0 ≤ p.2) :
    (h + deltaSum xs)^t - h^t ≤ paidDelta t xs := by
  induction xs with
  | nil => simp [deltaSum, paidDelta]
  | cons p xs ih =>
    have hp := hx p (by simp)
    have htail : ∀ q ∈ xs, 0 ≤ q.1 ∧ q.1 ≤ h ∧ 0 ≤ q.2 :=
      fun q hq => hx q (by simp [hq])
    have hd := deltaSum_nonneg xs (fun q hq => (htail q hq).2.2)
    have hi := ih htail
    have hc := rpow_increment_antitone hp.1
      (show p.1 ≤ h + deltaSum xs by linarith [hp.2.1]) hp.2.2 ht0 ht1
    simp only [deltaSum, List.map_cons, List.sum_cons] at *
    simp only [paidDelta, List.map_cons, List.sum_cons] at *
    have heq : h + (p.2 + (xs.map Prod.snd).sum) =
        h + (xs.map Prod.snd).sum + p.2 := by ring
    rw [heq]
    linarith [hi, hc]

/-- If the helper's endpoint gain is bounded by its own added paid rank,
    its productive moment increase cannot exceed its paid increase. -/
theorem helper_gain_le_paid_debt {h g t : ℝ} (hh : 0 ≤ h) (hg : 0 ≤ g)
    (ht0 : 0 ≤ t) (ht1 : t ≤ 1) (xs : List (ℝ × ℝ))
    (hx : ∀ p ∈ xs, 0 ≤ p.1 ∧ p.1 ≤ h ∧ 0 ≤ p.2)
    (hdebt : g ≤ deltaSum xs) :
    (h+g)^t - h^t ≤ paidDelta t xs := by
  have hm := Real.rpow_le_rpow (add_nonneg hh hg) (add_le_add_left hdebt h) ht0
  linarith [finite_list_debt hh ht0 ht1 xs hx]

end PhaseRankDebt

#print axioms PhaseRankDebt.concave_increment_antitone
#print axioms PhaseRankDebt.rpow_increment_antitone
#print axioms PhaseRankDebt.deltaSum_nonneg
#print axioms PhaseRankDebt.finite_list_debt
#print axioms PhaseRankDebt.helper_gain_le_paid_debt
