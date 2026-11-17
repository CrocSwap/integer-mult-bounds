import Nov15.WholeFloorCoverData1

namespace WholeFloorCover
open NumCertK

theorem cfW_p6 : Fup cfW (763/1000) (163/200) < 0 := by decide +kernel
theorem cfW_p7 : Fup cfW (163/200) (851/1000) < 0 := by decide +kernel
theorem cfW_p8 : Fup cfW (851/1000) (879/1000) < 0 := by decide +kernel
theorem cfW_p9 : Fup cfW (879/1000) (901/1000) < 0 := by decide +kernel
theorem cfW_p10 : Fup cfW (901/1000) (459/500) < 0 := by decide +kernel
theorem cfW_p11 : Fup cfW (459/500) (93/100) < 0 := by decide +kernel
theorem cfW_d : 0 < dLo cfW (93/100) (9795889035/10^10) := by decide +kernel
theorem cfW_end : Fup cfW (9795889035/10^10) (9795889035/10^10) < 0 := by decide +kernel

theorem cfW_neg (s : ℝ) (h0 : 0 ≤ s) (hs : s ≤ ((9795889035 / 10 ^ 10 : ℚ) : ℝ)) : Fc cfW s < 0 := by
  have o := cfW_ok
  by_cases a1 : s ≤ (((73/250) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o 0 (73/250) (le_refl _) (by norm_num) cfW_p1 s (by simpa using h0) a1
  by_cases a2 : s ≤ (((59/125) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (73/250) (59/125) (by norm_num) (by norm_num) cfW_p2 s (by push_neg at a1; exact a1.le) a2
  by_cases a3 : s ≤ (((301/500) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (59/125) (301/500) (by norm_num) (by norm_num) cfW_p3 s (by push_neg at a2; exact a2.le) a3
  by_cases a4 : s ≤ (((87/125) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (301/500) (87/125) (by norm_num) (by norm_num) cfW_p4 s (by push_neg at a3; exact a3.le) a4
  by_cases a5 : s ≤ (((763/1000) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (87/125) (763/1000) (by norm_num) (by norm_num) cfW_p5 s (by push_neg at a4; exact a4.le) a5
  by_cases a6 : s ≤ (((163/200) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (763/1000) (163/200) (by norm_num) (by norm_num) cfW_p6 s (by push_neg at a5; exact a5.le) a6
  by_cases a7 : s ≤ (((851/1000) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (163/200) (851/1000) (by norm_num) (by norm_num) cfW_p7 s (by push_neg at a6; exact a6.le) a7
  by_cases a8 : s ≤ (((879/1000) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (851/1000) (879/1000) (by norm_num) (by norm_num) cfW_p8 s (by push_neg at a7; exact a7.le) a8
  by_cases a9 : s ≤ (((901/1000) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (879/1000) (901/1000) (by norm_num) (by norm_num) cfW_p9 s (by push_neg at a8; exact a8.le) a9
  by_cases a10 : s ≤ (((459/500) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (901/1000) (459/500) (by norm_num) (by norm_num) cfW_p10 s (by push_neg at a9; exact a9.le) a10
  by_cases a11 : s ≤ (((93/100) : ℚ) : ℝ)
  · exact Fc_neg_piece cfW o (459/500) (93/100) (by norm_num) (by norm_num) cfW_p11 s (by push_neg at a10; exact a10.le) a11
  have h1 := Fc_mono cfW o (93/100) (9795889035/10^10) (by norm_num) (by norm_num) cfW_d s
    (by push_neg at a11; exact a11.le) hs
  have h2 := Fc_neg_piece cfW o (9795889035/10^10) (9795889035/10^10) (by norm_num) (by norm_num) cfW_end
    ((9795889035/10^10 : ℚ) : ℝ) (le_refl _) (le_refl _)
  linarith

end WholeFloorCover

#print axioms WholeFloorCover.cfW_neg
