import Nov15.CongestionI3NumC3

/-! CONGESTION-I3 numeric part C4 : kernel interval pieces for the own56 ceiling; see CongestionI3NumC1 and CongestionI3.md. -/
namespace CongestionI3
open NumCertK

theorem cfC_d : 0 < dLo cfC (93 / 100) sC := by decide +kernel
theorem cfC_end : Fup cfC sC sC < liftC := by decide +kernel

theorem cfC88_neg (s : ℝ) (h0 : 0 ≤ s) (hs : s ≤ (9 / 10 : ℝ)) : Fc cfC88 s < 0 := by
  have piece : ∀ a b : ℚ, 0 ≤ a → b ≤ 1 → Fup cfC88 a b < 0 → (a : ℝ) ≤ s → s ≤ b → Fc cfC88 s < 0 :=
    fun a b ha hb hF h1 h2 => Fc_neg_piece cfC88 cfC88_ok a b ha hb hF s h1 h2
  by_cases c1 : s ≤ (((22/100) : ℚ) : ℝ)
  · exact piece (0) (22/100) (by norm_num) (by norm_num) cfC88_p1 (by simpa using h0) c1
  by_cases c2 : s ≤ (((39/100) : ℚ) : ℝ)
  · exact piece (22/100) (39/100) (by norm_num) (by norm_num) cfC88_p2 (by push_cast; push_neg at c1; linarith) c2
  by_cases c3 : s ≤ (((51/100) : ℚ) : ℝ)
  · exact piece (39/100) (51/100) (by norm_num) (by norm_num) cfC88_p3 (by push_cast; push_neg at c2; linarith) c3
  by_cases c4 : s ≤ (((6/10) : ℚ) : ℝ)
  · exact piece (51/100) (6/10) (by norm_num) (by norm_num) cfC88_p4 (by push_cast; push_neg at c3; linarith) c4
  by_cases c5 : s ≤ (((67/100) : ℚ) : ℝ)
  · exact piece (6/10) (67/100) (by norm_num) (by norm_num) cfC88_p5 (by push_cast; push_neg at c4; linarith) c5
  by_cases c6 : s ≤ (((72/100) : ℚ) : ℝ)
  · exact piece (67/100) (72/100) (by norm_num) (by norm_num) cfC88_p6 (by push_cast; push_neg at c5; linarith) c6
  by_cases c7 : s ≤ (((76/100) : ℚ) : ℝ)
  · exact piece (72/100) (76/100) (by norm_num) (by norm_num) cfC88_p7 (by push_cast; push_neg at c6; linarith) c7
  by_cases c8 : s ≤ (((79/100) : ℚ) : ℝ)
  · exact piece (76/100) (79/100) (by norm_num) (by norm_num) cfC88_p8 (by push_cast; push_neg at c7; linarith) c8
  by_cases c9 : s ≤ (((81/100) : ℚ) : ℝ)
  · exact piece (79/100) (81/100) (by norm_num) (by norm_num) cfC88_p9 (by push_cast; push_neg at c8; linarith) c9
  by_cases c10 : s ≤ (((83/100) : ℚ) : ℝ)
  · exact piece (81/100) (83/100) (by norm_num) (by norm_num) cfC88_p10 (by push_cast; push_neg at c9; linarith) c10
  by_cases c11 : s ≤ (((86/100) : ℚ) : ℝ)
  · exact piece (83/100) (86/100) (by norm_num) (by norm_num) cfC88_p11 (by push_cast; push_neg at c10; linarith) c11
  by_cases c12 : s ≤ (((88/100) : ℚ) : ℝ)
  · exact piece (86/100) (88/100) (by norm_num) (by norm_num) cfC88_p12 (by push_cast; push_neg at c11; linarith) c12
  exact piece (88/100) (9/10) (by norm_num) (by norm_num) cfC88_p13 (by push_cast; push_neg at c12; linarith) (by push_cast; linarith)

/-- F_base < 17 * LcC on s in [.9, 1 - tbarC] (the lift is the constant 17 * LcC) -/
theorem cfC_neg (s : ℝ) (h1 : (9 / 10 : ℝ) ≤ s) (h2 : s ≤ ((sC : ℚ) : ℝ)) : Fc cfC s < ((liftC : ℚ) : ℝ) := by
  have piece : ∀ a b : ℚ, 0 ≤ a → b ≤ 1 → Fup cfC a b < liftC → (a : ℝ) ≤ s → s ≤ b → Fc cfC s < ((liftC : ℚ) : ℝ) := by
    intro a b ha hb hF h1 h2
    have := Fc_le cfC cfC_ok a b ha hb s h1 h2
    have h' : ((Fup cfC a b : ℚ) : ℝ) < ((liftC : ℚ) : ℝ) := by exact_mod_cast hF
    linarith
  by_cases c1 : s ≤ (((915 / 1000 : ℚ)) : ℝ)
  · exact piece (90 / 100) (915 / 1000) (by norm_num) (by norm_num) cfC_q1 (by push_cast; linarith) c1
  by_cases c2 : s ≤ (((93 / 100 : ℚ)) : ℝ)
  · exact piece (915 / 1000) (93 / 100) (by norm_num) (by norm_num) cfC_q2 (by push_neg at c1; exact c1.le) c2
  have h1' : (((93 / 100 : ℚ)) : ℝ) ≤ s := by push_neg at c2; exact c2.le
  have hm := Fc_mono cfC cfC_ok (93 / 100) sC (by norm_num) (by unfold sC; norm_num) cfC_d s h1' h2
  have he := Fc_le cfC cfC_ok sC sC (by unfold sC; norm_num) (by unfold sC; norm_num) sC (le_refl _) (le_refl _)
  have he' : ((Fup cfC sC sC : ℚ) : ℝ) < ((liftC : ℚ) : ℝ) := by exact_mod_cast cfC_end
  linarith

end CongestionI3

#print axioms CongestionI3.cfC88_neg
#print axioms CongestionI3.cfC_neg
