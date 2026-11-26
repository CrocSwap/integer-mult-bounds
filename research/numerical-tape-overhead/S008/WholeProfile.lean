import S008.NumericalCutoff

namespace S008.WholeProfile

open S008.NumericalCutoff

private theorem ln_two_lower : (1/2:ℝ) ≤ Real.log 2 := by
  have h := Real.log_le_sub_one_of_pos (show (0:ℝ) < 1/2 by norm_num)
  rw [Real.log_div (by norm_num) (by norm_num), Real.log_one] at h
  linarith

private theorem log_two_sq : Real.log (4:ℝ) = 2*Real.log 2 := by
  have a := Real.log_pow (2:ℝ) 2
  norm_num at a ⊢
  exact a

/-- For every larger scale the logarithmic density decreases. -/
theorem log_density {x y : ℝ} (hx : 2 ≤ x) (hy : x ≤ y) :
    x*logTwo (y+2) ≤ y*logTwo (x+2) := by
  have hp : 0 < x+2 := by linarith
  have hq : 0 < y+2 := by linarith
  have hden : 0 < Real.log (2:ℝ) := Real.log_pos (by norm_num)
  have ht := Real.log_le_sub_one_of_pos (div_pos hq hp)
  rw [Real.log_div (ne_of_gt hq) (ne_of_gt hp)] at ht
  have hd : (y+2)/(x+2)-1 = (y-x)/(x+2) := by field_simp; ring
  rw [hd, le_div_iff₀ hp] at ht
  have hl := Real.log_le_log (show (0:ℝ)<4 by norm_num) (show (4:ℝ)≤x+2 by linarith)
  rw [log_two_sq] at hl
  have hly : Real.log (x+2) ≤ Real.log (y+2) := Real.log_le_log hp (by linarith)
  have hg : 1 ≤ Real.log (x+2) := by linarith [ln_two_lower]
  unfold logTwo
  rw [← mul_div_assoc, ← mul_div_assoc, div_le_div_iff_of_pos_right hden]
  nlinarith [mul_nonneg (sub_nonneg.mpr hy) (sub_nonneg.mpr hg)]

private theorem nonneg_phi {x : ℝ} (hx : 0 ≤ x) : 0 ≤ phi x := by
  unfold phi logTwo
  apply Real.rpow_nonneg
  exact mul_nonneg (sq_nonneg _) (div_nonneg (Real.log_nonneg (by linarith))
    (Real.log_nonneg (by norm_num)))


theorem phi_density {x y : ℝ} (hx : 2 ≤ x) (hy : x ≤ y) : x*phi y ≤ y*phi x := by
  have ax : 0 ≤ x := by linarith
  have ay : 0 ≤ y := by linarith
  have hd := log_density hx hy
  apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) (mul_nonneg ay (nonneg_phi ax))
  rw [mul_pow, mul_pow, phi_cube ax, phi_cube ay]
  nlinarith only [mul_nonneg (mul_nonneg (sq_nonneg x) (sq_nonneg y)) (sub_nonneg.mpr hd)]

theorem phi_at_most_width {x : ℝ} (hx : 2 ≤ x) : phi x ≤ x := by
  have hlog := log_density (by norm_num : (2:ℝ) ≤ 2) hx
  have hfour : logTwo (2+2) = 2 := by
    unfold logTwo
    norm_num
    rw [log_two_sq]
    field_simp [ne_of_gt (Real.log_pos (by norm_num : (1:ℝ)<2))]
  rw [hfour] at hlog
  have hpos : 0 ≤ x := by linarith
  apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) hpos
  rw [phi_cube hpos]
  nlinarith only [mul_nonneg (sq_nonneg x) (show 0 ≤ x-logTwo (x+2) by linarith)]

theorem shifted_phi {x : ℝ} (hx : 2 ≤ x) : phi (x+2) ≤ phi x+2 := by
  have hd := phi_density hx (show x ≤ x+2 by linarith)
  have hp := phi_at_most_width hx
  by_contra! h
  nlinarith [mul_pos (show 0<x by linarith) (sub_pos.mpr h)]


end S008.WholeProfile
