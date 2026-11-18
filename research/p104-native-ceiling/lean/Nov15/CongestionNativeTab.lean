import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Nov15.CongestionI3DualConst

/-! CONGESTION-NATIVE certified rational tables.
Source: internal notes (Decimal exp/ln at 80 digits, +-1e-70 brackets; every weight of the spF DAG rounded DOWN,
cst rounded UP, unit_lo = 9^s lower - 8^s upper).  The values below were emitted by re-running hc9's `spF_lo` / `unit_lo` and converting the
80-digit Decimals to exact rationals, rounded DOWN to 14 digits (outward).  `cHC_j` are hc9's own rounded-UP cst brackets.
Here only the pure arithmetic is proved (kernel, norm_num):  lcpC_j + 8 cHC_j <= 1936 * min(spFloC_j, unitLoC_j / 48).
The statements `spFloC_j <= spF(tC_j)`, `cst(t_{j+1}) <= cHC_j`, `unitLoC_j <= 9^s - 8^s` are HYPOTHESES of the ceiling (computed, hc9.log). -/
namespace CongestionNative
open CongestionI3Dual

def spFloC0 : ℚ := 131069767447 / 20000000000000
def spFloC1 : ℚ := 655443767027 / 100000000000000
def spFloC2 : ℚ := 26407594739 / 4000000000000
def spFloC3 : ℚ := 141372084217 / 12500000000000
/-- lower bound of 9^(1-t_{j+1}) - 8^(1-t_{j+1}) (t_1, t_2, t_3, 1/10) -/
def unitLoC0 : ℚ := 11974198659989 / 12500000000000
def unitLoC1 : ℚ := 95763386760327 / 100000000000000
def unitLoC2 : ℚ := 23196470570391 / 25000000000000
def unitLoC3 : ℚ := 72665488499219 / 100000000000000
/-- upper brackets of cst(t_{j+1}) -/
def cHC0 : ℚ := 84217 / 2500000
def cHC1 : ℚ := 339299 / 10 ^ 7
def cHC2 : ℚ := 579807 / 10 ^ 7
def cHC3 : ℚ := 2255027 / 10 ^ 7

theorem tabC0 : lcpC0 + 8 * cHC0 ≤ 1936 * spFloC0 ∧ lcpC0 + 8 * cHC0 ≤ 1936 * (unitLoC0 / 48) := by
  unfold lcpC0 cHC0 spFloC0 unitLoC0; constructor <;> norm_num
theorem tabC1 : lcpC1 + 8 * cHC1 ≤ 1936 * spFloC1 ∧ lcpC1 + 8 * cHC1 ≤ 1936 * (unitLoC1 / 48) := by
  unfold lcpC1 cHC1 spFloC1 unitLoC1; constructor <;> norm_num
theorem tabC2 : lcpC2 + 8 * cHC2 ≤ 1936 * spFloC2 ∧ lcpC2 + 8 * cHC2 ≤ 1936 * (unitLoC2 / 48) := by
  unfold lcpC2 cHC2 spFloC2 unitLoC2; constructor <;> norm_num
theorem tabC3 : lcpC3 + 8 * cHC3 ≤ 1936 * spFloC3 ∧ lcpC3 + 8 * cHC3 ≤ 1936 * (unitLoC3 / 48) := by
  unfold lcpC3 cHC3 spFloC3 unitLoC3; constructor <;> norm_num

end CongestionNative
