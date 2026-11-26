import S008.NumericalCutoff

/-! Real-variable endpoint control for the continuous true-label curve.
    Algebraic Jensen proof using only log(u) ≤ u−1, with no derivative oracle. -/
namespace S008.TrueLabel
open S008.NumericalCutoff

theorem true_letter_invoice {d s t σ : ℝ} (hd : 16≤d) (ht : 1≤t)
    (hwidth : t≤s/d^2+3) (hh : S008.NumericalCutoff.logTwo (2*d-1)≤d)
    (hin : σ+2 ≤ 39+S008.NumericalCutoff.logTwo (2*d-1)+(d+1)*(2*d-1)+
      (2*d-1+d)*t+d*(d-1)*S008.NumericalCutoff.logTwo t) :
    σ+2 ≤ 3*s/d+d^2*(S008.NumericalCutoff.logTwo t+3) := by
  have hg : 0≤S008.NumericalCutoff.logTwo t := by
    unfold S008.NumericalCutoff.logTwo
    exact div_nonneg (Real.log_nonneg ht) (Real.log_nonneg (by norm_num))
  have hp : 0<d := by linarith
  have hwidth' : 3*d*t≤3*s/d+9*d := by
    have h := mul_le_mul_of_nonneg_left hwidth (by linarith : 0≤3*d)
    have he : 3*d*(s/d^2+3)=3*s/d+9*d := by field_simp; ring
    rwa [he] at h
  have hquad : 39+12*d≤d^2 := by
    nlinarith only [mul_nonneg (sub_nonneg.mpr hd) (show 0≤d+4 by linarith)]
  have hsum : 0 ≤ (d-S008.NumericalCutoff.logTwo (2*d-1))+
      (3*s/d+9*d-3*d*t)+(d^2-(39+12*d))+t+
      d*S008.NumericalCutoff.logTwo t+(d+1) := by
    exact add_nonneg (add_nonneg (add_nonneg (add_nonneg (add_nonneg
      (sub_nonneg.mpr hh) (sub_nonneg.mpr hwidth')) (sub_nonneg.mpr hquad))
      (show 0≤t by linarith)) (mul_nonneg hp.le hg)) (by linarith)
  apply hin.trans
  apply sub_nonneg.mp
  convert hsum using 1
  ring

end S008.TrueLabel
