import Nov15.NumCertK

/-!
NUMCERT-K data half : the concrete interval checks for the K(S22) invoice (kernel `decide`), and the real-analysis
conclusion `cfK_neg`: F(s) < 0 on [0, 1 - .0060197405].  Library: Nov15/NumCertK.lean.
-/
namespace NumCertK

/-! ### 5. the K(S22) invoice, merged by rank: F(s) = sum c_r r^s, caller(6|7) + 17 * native K22 -/
def cfK : CF := [(1, -42272), (2, 6494), (3, -1751), (4, -2159), (5, -2499), (6, -170), (8, -656), (9, 384),
  (16, -416), (17, 416), (24, -416), (25, 416), (32, -416), (33, 416), (40, -416), (41, 416), (48, -416),
  (49, 416), (56, -416), (57, 416), (64, -208), (65, 416), (73, 208), (137, 208)]

theorem cfK_ok : okR cfK := by decide +kernel
theorem cfK_p1 : Fup cfK 0 (45/100) < 0 := by decide +kernel
theorem cfK_p2 : Fup cfK (45/100) (6/10) < 0 := by decide +kernel
theorem cfK_p3 : Fup cfK (6/10) (7/10) < 0 := by decide +kernel
theorem cfK_p4 : Fup cfK (7/10) (8/10) < 0 := by decide +kernel
theorem cfK_p5 : Fup cfK (8/10) (85/100) < 0 := by decide +kernel
theorem cfK_p6 : Fup cfK (85/100) (9/10) < 0 := by decide +kernel
theorem cfK_d : 0 < dLo cfK (9/10) (9939802595/10^10) := by decide +kernel
theorem cfK_end : Fup cfK (9939802595/10^10) (9939802595/10^10) < 0 := by decide +kernel

/-- **F(s) < 0 for every s in [0, 1 - .0060197405]**, F(s) = sum over the 24 ranks of c_r r^s (kernel-checked). -/
theorem cfK_neg (s : ℝ) (h0 : 0 ≤ s) (hs : s ≤ ((9939802595 / 10 ^ 10 : ℚ) : ℝ)) : Fc cfK s < 0 := by
  have o := cfK_ok
  by_cases a1 : s ≤ ((45/100 : ℚ) : ℝ)
  · exact Fc_neg_piece cfK o 0 (45/100) (le_refl _) (by norm_num) cfK_p1 s (by simpa using h0) a1
  by_cases a2 : s ≤ ((6/10 : ℚ) : ℝ)
  · exact Fc_neg_piece cfK o (45/100) (6/10) (by norm_num) (by norm_num) cfK_p2 s (by push_neg at a1; exact a1.le) a2
  by_cases a3 : s ≤ ((7/10 : ℚ) : ℝ)
  · exact Fc_neg_piece cfK o (6/10) (7/10) (by norm_num) (by norm_num) cfK_p3 s (by push_neg at a2; exact a2.le) a3
  by_cases a4 : s ≤ ((8/10 : ℚ) : ℝ)
  · exact Fc_neg_piece cfK o (7/10) (8/10) (by norm_num) (by norm_num) cfK_p4 s (by push_neg at a3; exact a3.le) a4
  by_cases a5 : s ≤ ((85/100 : ℚ) : ℝ)
  · exact Fc_neg_piece cfK o (8/10) (85/100) (by norm_num) (by norm_num) cfK_p5 s (by push_neg at a4; exact a4.le) a5
  by_cases a6 : s ≤ ((9/10 : ℚ) : ℝ)
  · exact Fc_neg_piece cfK o (85/100) (9/10) (by norm_num) (by norm_num) cfK_p6 s (by push_neg at a5; exact a5.le) a6
  -- s in [9/10, s0]: F is increasing there (F' >= dLo > 0), so F(s) <= F(s0) < 0
  have h1 := Fc_mono cfK o (9/10) (9939802595/10^10) (by norm_num) (by norm_num) cfK_d s
    (by push_neg at a6; exact a6.le) hs
  have h2 := Fc_neg_piece cfK o (9939802595/10^10) (9939802595/10^10) (by norm_num) (by norm_num) cfK_end
    ((9939802595 / 10 ^ 10 : ℚ) : ℝ) (le_refl _) (le_refl _)
  linarith

end NumCertK

#print axioms NumCertK.pow_lo
#print axioms NumCertK.pow_hi
#print axioms NumCertK.cfK_neg
