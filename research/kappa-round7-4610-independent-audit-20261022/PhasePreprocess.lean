/- Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
   Scoped moment inequality. Native phase support and invoices are separate. -/
import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

namespace PhasePreprocess

/-- Preprocessing one arbitrary helper cannot create a moment gain merely
    by increasing its rank by the rank of the additional paid child. -/
theorem strict_preprocess_loss {g h t : ℝ} (hg : 0 < g) (hh : 0 < h)
    (ht0 : 0 < t) (ht1 : t < 1) :
    (g+h)^t - g^t < h^t := by
  have hs : 0 < g+h := add_pos hg hh
  have hwg : 0 < g/(g+h) := div_pos hg hs
  have hwh : 0 < h/(g+h) := div_pos hh hs
  have hw : g/(g+h) + h/(g+h) = 1 := by
    rw [← add_div, div_self (ne_of_gt hs)]
  have hmixg : g/(g+h)*(g+h) = g := div_mul_cancel₀ _ (ne_of_gt hs)
  have hmixh : h/(g+h)*(g+h) = h := div_mul_cancel₀ _ (ne_of_gt hs)
  have hcg := (Real.strictConcaveOn_rpow ht0 ht1).2
    (show g+h ∈ Set.Ici 0 from hs.le)
    (show (0 : ℝ) ∈ Set.Ici 0 by simp)
    (ne_of_gt hs) hwg hwh hw
  have hch := (Real.strictConcaveOn_rpow ht0 ht1).2
    (show g+h ∈ Set.Ici 0 from hs.le)
    (show (0 : ℝ) ∈ Set.Ici 0 by simp)
    (ne_of_gt hs) hwh hwg (by linarith [hw])
  simp only [smul_eq_mul, Real.zero_rpow (ne_of_gt ht0), mul_zero,
    add_zero, hmixg, hmixh] at hcg hch
  have hc : g/(g+h)*(g+h)^t + h/(g+h)*(g+h)^t = (g+h)^t := by
    rw [← add_mul, hw, one_mul]
  linarith

theorem bounded_preprocess_loss {g h d t : ℝ} (hg : 0 < g) (hh : 0 < h)
    (hd0 : 0 ≤ d) (hdh : d ≤ h) (ht0 : 0 < t) (ht1 : t < 1) :
    (g+d)^t - g^t < h^t := by
  have hm : (g+d)^t ≤ (g+h)^t :=
    Real.rpow_le_rpow (by linarith) (by linarith) ht0.le
  linarith [strict_preprocess_loss hg hh ht0 ht1]

theorem whole_preprocess_loss {g h t m : ℝ} (hg : 0 < g) (hh : 0 < h)
    (ht0 : 0 < t) (ht1 : t < 1) (hm : 0 < m) :
    m * ((g+h)^t - g^t - h^t) < 0 := by
  exact mul_neg_of_pos_of_neg hm (sub_neg.mpr (strict_preprocess_loss hg hh ht0 ht1))

end PhasePreprocess

#print axioms PhasePreprocess.strict_preprocess_loss
#print axioms PhasePreprocess.bounded_preprocess_loss
#print axioms PhasePreprocess.whole_preprocess_loss
