import Nov15.NumCertK

/-!
CONGESTION-I3 numeric half A : the 8|9 crossing of F1 (internal notes sec. 3) with NumCertK.
F_base = F of the #7113 caller C(8|9) (caller 6 7) at 17 calls with the native replaced by R1/R2's owned floor (400 * 8^s + 16) and NO stops
(`cfB`; = WholeFloorCover.cfW with the 17 * 88 stop terms (1, -2992), (2, +1496) removed).  The I3 lift is the constant 17 * 1936 * sigma0,
sigma0 = 9785438/10^9 <= sp_F(t) (shape-DAG path bound in F currency, F1 f1ceil.spF at t = tbar = .0183952347; DATA, python).
Crossing: dF_base/ds > 0 on [.9, s0] (dLo, kernel), F_base(s0) < 17 * 1936 * sigma0 (kernel), s0 = 1 - tbar, tbar = .0183952347.
-/
namespace CongestionI3
open NumCertK

def cfB : CF := [(1, -656), (8, -7456), (9, 384), (16, -416), (17, 416), (24, -416), (25, 416), (32, -416), (33, 416),
  (40, -416), (41, 416), (48, -416), (49, 416), (56, -416), (57, 416), (64, -208), (65, 416), (73, 208), (137, 208)]
def sigma0 : ℚ := 9785438 / 10 ^ 9
def sA : ℚ := 9816047653 / 10 ^ 10
def liftA : ℚ := 17 * 1936 * sigma0

theorem cfB_ok : okR cfB := by decide +kernel
theorem cfB_p1 : Fup cfB (90 / 100) (91 / 100) < liftA := by decide +kernel
theorem cfB_p2 : Fup cfB (91 / 100) (92 / 100) < liftA := by decide +kernel
theorem cfB_p3 : Fup cfB (92 / 100) (93 / 100) < liftA := by decide +kernel
theorem cfB_d : 0 < dLo cfB (93 / 100) sA := by decide +kernel
theorem cfB_end : Fup cfB sA sA < liftA := by decide +kernel

/-- F_base(s) < 17 * 1936 * sigma0 on s in [.9, 1 - tbar] -/
theorem cfB_neg (s : ℝ) (h1 : (9 / 10 : ℝ) ≤ s) (h2 : s ≤ ((sA : ℚ) : ℝ)) : Fc cfB s < ((liftA : ℚ) : ℝ) := by
  have piece : ∀ a b : ℚ, 0 ≤ a → b ≤ 1 → Fup cfB a b < liftA → (a : ℝ) ≤ s → s ≤ b → Fc cfB s < ((liftA : ℚ) : ℝ) := by
    intro a b ha hb hF h1 h2
    have := Fc_le cfB cfB_ok a b ha hb s h1 h2
    have h' : ((Fup cfB a b : ℚ) : ℝ) < ((liftA : ℚ) : ℝ) := by exact_mod_cast hF
    linarith
  by_cases c1 : s ≤ (((91 / 100 : ℚ)) : ℝ)
  · exact piece (90 / 100) (91 / 100) (by norm_num) (by norm_num) cfB_p1 (by push_cast; linarith) c1
  by_cases c2 : s ≤ (((92 / 100 : ℚ)) : ℝ)
  · exact piece (91 / 100) (92 / 100) (by norm_num) (by norm_num) cfB_p2 (by push_neg at c1; exact c1.le) c2
  by_cases hc : s ≤ (((93 / 100 : ℚ)) : ℝ)
  · exact piece (92 / 100) (93 / 100) (by norm_num) (by norm_num) cfB_p3 (by push_neg at c2; exact c2.le) hc
  have h1' : (((93 / 100 : ℚ)) : ℝ) ≤ s := by push_neg at hc; exact hc.le
  have hm := Fc_mono cfB cfB_ok (93 / 100) sA (by norm_num) (by unfold sA; norm_num) cfB_d s h1' h2
  have he := Fc_le cfB cfB_ok sA sA (by unfold sA; norm_num) (by unfold sA; norm_num) sA (le_refl _) (le_refl _)
  have he' : ((Fup cfB sA sA : ℚ) : ℝ) < ((liftA : ℚ) : ℝ) := by exact_mod_cast cfB_end
  linarith

end CongestionI3

#print axioms CongestionI3.cfB_neg
