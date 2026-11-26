import S008.InputClock63

namespace S008.ProfileLimit
open S008.ThreeSlope S008.NumericalCutoff S008.WholeProfile

def fixedHeight : ℚ := 299/36

private theorem recurrence_step {x r:ℚ} (hx:x≤fixedHeight) (hr:0≤r) (hmax:r≤1/4) :
    20/3+r*(x-7/4) ≤ fixedHeight := by
  have h1 := mul_le_mul_of_nonneg_left (sub_le_sub_right hx (7/4:ℚ)) hr
  have h2 := mul_le_mul_of_nonneg_right hmax (show 0≤fixedHeight-7/4 by norm_num [fixedHeight])
  unfold fixedHeight at *
  linarith only [h1,h2]

/-- All degree bands j≥6 lie on the smaller side of the limiting recurrence. -/
theorem tail_height (i:ℕ) : height (i+1) ≤ fixedHeight := by
  induction i with
  | zero =>
    have h5 : scale 5 = 22 := by decide +kernel
    have h6 : scale 6 = 25 := by decide +kernel
    norm_num [height,fixedHeight,h5,h6]
  | succ i ih =>
    let k := i+1
    have hQ : (0:ℚ)<(scale (6+k):ℕ) := by unfold scale; positivity
    have hm : (scale (5+k):ℚ) ≤ (scale (6+k):ℚ) := by
      exact_mod_cast (show scale (5+k) ≤ scale (6+k) by
        simpa only [show 5+k+1=6+k by omega] using scale_mono (5+k))
    apply recurrence_step ih (by positivity)
    rw [div_le_iff₀ (show (0:ℚ)<4*(scale (6+k):ℚ) by positivity)]
    linarith only [hm]

theorem knot_cubes :
    (fixedHeight+17/4)^3 < 4*fixedHeight^3 ∧
    (fixedHeight+17/4+22/3)^3 < 16*fixedHeight^3 ∧
    (159/4+(115/12):ℚ)^3 < 240*fixedHeight^3 ∧
    240*fixedHeight^3 < (479/8-(33/4):ℚ)^3 := by
  norm_num [fixedHeight]

/-- One bit of margin after the actual outer clock has paid its spectrum and movement. -/
theorem outer_sixty {t:ℝ} (ht : 1572864480≤t) :
    182+4*logTwo (t+2)+(479/8)*phi (t+2)+1 ≤ 60*phi t := by
  have hp : 0≤t := by linarith
  have hlog := logTwo_mono (show (0:ℝ)<2 by norm_num) (show 2≤t+2 by linarith)
  have hlog2 : logTwo 2=1 := div_self (ne_of_gt (Real.log_pos (by norm_num)))
  rw [hlog2] at hlog
  have hbound : 512*logTwo (t+2) ≤ t :=
    log_control 512 (2^30) 31 (by norm_num) (by norm_num) (by norm_num) (by norm_num)
      (by norm_num) (by linarith only [ht])
  have hr : 64*logTwo (t+2) ≤ phi t := by
    apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) (S008.Piecewise.phi_nonneg hp)
    rw [mul_pow,phi_cube hp]
    have hs : (512*logTwo (t+2))^2≤t^2 := by
      nlinarith [mul_nonneg (sub_nonneg.mpr hbound) (show 0≤t+512*logTwo (t+2) by linarith)]
    nlinarith only [mul_le_mul_of_nonneg_right hs (show 0≤logTwo (t+2) by linarith only [hlog])]
  have hsize : (2:ℝ)^20 ≤ phi t := by
    apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) (S008.Piecewise.phi_nonneg hp)
    rw [phi_cube hp]
    have hh : 2^30 ≤ t := by linarith only [ht]
    nlinarith only [mul_nonneg (sub_nonneg.mpr hh) (show 0≤t+2^30 by linarith only [ht]),
      mul_nonneg (sq_nonneg t) (sub_nonneg.mpr hlog)]
  have hshift := shifted_phi (show 2≤t by linarith only [ht])
  linarith only [hr,hsize,hshift]

end S008.ProfileLimit
