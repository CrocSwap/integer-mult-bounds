import S008.NativeFacets

namespace S008.Piecewise

/-- A finite upper frame for every contribution to the historical maximum.
    The test includes the zero-surplus and all earlier actual-width cases. -/
def prefixBound (P H : ℝ → ℝ) (z B : ℝ) : Prop :=
  48*P z ≤ B ∧ ∀ v, 0 ≤ v → v ≤ z → 48*P z+H v-(159/4:ℝ)*P v ≤ B

/-- Decreasing density of the two input shapes implies decreasing density of
    their full historical majorant. This crosses arbitrarily many later native
    slope changes and requires no upper bound on their number. -/
theorem prefix_density (P H : ℝ → ℝ) {z t B : ℝ} (hz : 0 < z) (ht : z ≤ t)
    (hP : ∀ u v, z ≤ u → u ≤ v → u*P v ≤ v*P u)
    (hH : ∀ v, z ≤ v → z*H v ≤ v*H z) (hb : prefixBound P H z B) :
    prefixBound P H t (t*B/z) := by
  obtain ⟨hb0,hbc⟩ := hb
  have ht0 : 0 < t := hz.trans_le ht
  have hpzt := hP z t (le_refl _) ht
  have hbare : z*(48*P t) ≤ t*B := by
    nlinarith only [hpzt,mul_le_mul_of_nonneg_left hb0 ht0.le]
  constructor
  · rw [le_div_iff₀ hz]
    linarith only [hbare]
  intro v hv hvmax
  rw [le_div_iff₀ hz]
  rcases le_total v z with hshort | hlong
  · by_cases hs : 0 ≤ H v-(159/4:ℝ)*P v
    · have hθ := mul_nonneg (sub_nonneg.mpr ht) hs
      have hcompare := mul_le_mul_of_nonneg_left (hbc v hv hshort) ht0.le
      nlinarith only [hpzt,hcompare,hθ]
    · nlinarith only [hbare,mul_nonpos_of_nonneg_of_nonpos hz.le (le_of_not_ge hs)]
  · have hpvt := hP v t hlong hvmax
    have hh := hH v hlong
    have hcoef : 0 ≤ 48*t-(159/4:ℝ)*v := by linarith
    have hp₁ := mul_le_mul_of_nonneg_left hpzt hcoef
    have hp₂ := mul_le_mul_of_nonneg_left hpvt hz.le
    have hh₁ := mul_le_mul_of_nonneg_left hh ht0.le
    have hb₁ := mul_le_mul_of_nonneg_left hb0 (sub_nonneg.mpr hvmax)
    have hb₂ := mul_le_mul_of_nonneg_left (hbc z hz.le (le_refl _)) hv
    have hbt := mul_le_mul_of_nonneg_left (add_le_add hb₁ hb₂) ht0.le
    by_contra! hn
    nlinarith only [hp₁,hp₂,hh₁,hbt,mul_pos ht0 (sub_pos.mpr hn)]

/-- The +2 rounded-width slack preserves the comparison after one divides by
    the original input scale. -/
theorem shifted_prefix_density (P H : ℝ → ℝ) {z t B : ℝ}
    (hz : 0 < z) (ht : z ≤ t) (hB : 0 ≤ B)
    (hP : ∀ u v, z+2 ≤ u → u ≤ v → u*P v ≤ v*P u)
    (hH : ∀ v, z+2 ≤ v → (z+2)*H v ≤ v*H (z+2)) (hb : prefixBound P H (z+2) B) :
    prefixBound P H (t+2) (t*B/z) := by
  have hz2 : 0 < z+2 := by linarith
  have h := prefix_density P H hz2 (by linarith : z+2 ≤ t+2) hP hH hb
  have hcost : (t+2)*B/(z+2) ≤ t*B/z := by
    rw [div_le_div_iff₀ hz2 hz]
    nlinarith only [mul_nonneg (sub_nonneg.mpr ht) hB]
  exact ⟨h.1.trans hcost, fun v h0 h1 => (h.2 v h0 h1).trans hcost⟩

end S008.Piecewise
